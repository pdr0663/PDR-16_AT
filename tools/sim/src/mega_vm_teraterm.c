#include <windows.h>

#include <signal.h>
#include <stdbool.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "simavr/avr_uart.h"
#include "simavr/fifo_declare.h"
#include "simavr/sim_avr.h"
#include "simavr/sim_elf.h"
#include "simavr/sim_gdb.h"
#include "simavr/sim_hex.h"

DECLARE_FIFO(uint8_t, uart_pipe_fifo, 1024);
DEFINE_FIFO(uint8_t, uart_pipe_fifo);

enum {
  IRQ_UART_PIPE_BYTE_IN = 0,
  IRQ_UART_PIPE_BYTE_OUT,
  IRQ_UART_PIPE_COUNT,
};

static const char *const kDefaultPipeName = "PDR16_XT_UART0";
static const char *const kDefaultLogPath = "tools\\sim\\logs\\mega_vm_pipe_bridge.log";
static const char *const kDefaultFirmware =
    "firmware\\mega\\pdr_vm\\.build-cli\\pdr_vm.ino.elf";
static const char *const kFallbackFirmware =
    "firmware\\mega\\pdr_vm\\.build-cli\\pdr_vm.ino.hex";

typedef struct uart_pipe_t {
  avr_t *avr;
  avr_irq_t *irq;
  HANDLE pipe_handle;
  FILE *log;
  int xon;
  uart_pipe_fifo_t host_to_avr;
  uart_pipe_fifo_t avr_to_host;
} uart_pipe_t;

static const char *kPipeIrqNames[IRQ_UART_PIPE_COUNT] = {
    [IRQ_UART_PIPE_BYTE_IN] = "8<uart_pipe.in",
    [IRQ_UART_PIPE_BYTE_OUT] = "8>uart_pipe.out",
};

static avr_t *g_avr = NULL;

static void handle_signal(int signum) {
  (void)signum;
  if (g_avr != NULL) {
    avr_terminate(g_avr);
  }
}

static void usage(const char *argv0) {
  fprintf(stderr,
          "Usage: %s [--firmware <path>] [--mcu <name>] [--freq <hz>] "
          "[--pipe-name <name>] [--log-path <path>] [-g [port]] [-v]\n",
          argv0);
}

static void log_line(FILE *log, const char *fmt, ...) {
  va_list ap;
  va_start(ap, fmt);
  vfprintf(log, fmt, ap);
  fputc('\n', log);
  fflush(log);
  va_end(ap);
}

static void log_bytes(FILE *log, const char *label, const uint8_t *data, size_t len) {
  if (len == 0) {
    return;
  }

  fprintf(log, "%s ", label);
  for (size_t i = 0; i < len; ++i) {
    unsigned char ch = data[i];
    if (ch == '\r') {
      continue;
    }
    if (ch == '\n') {
      fputc('\n', log);
      fprintf(log, "%s ", label);
      continue;
    }
    if (ch == '\t' || (ch >= 0x20 && ch < 0x7f)) {
      fputc((int)ch, log);
    } else {
      fprintf(log, "\\x%02X", ch);
    }
  }
  fputc('\n', log);
  fflush(log);
}

static bool create_directory_for_file(const char *path) {
  char buffer[MAX_PATH];
  size_t len = strlen(path);
  if (len >= sizeof(buffer)) {
    return false;
  }
  memcpy(buffer, path, len + 1);

  char *slash = strrchr(buffer, '\\');
  char *fslash = strrchr(buffer, '/');
  if (!slash || (fslash && fslash > slash)) {
    slash = fslash;
  }
  if (!slash) {
    return true;
  }
  *slash = '\0';
  if (*buffer == '\0') {
    return true;
  }
  if (CreateDirectoryA(buffer, NULL)) {
    return true;
  }
  return GetLastError() == ERROR_ALREADY_EXISTS;
}

static void uart_pipe_in_hook(struct avr_irq_t *irq, uint32_t value, void *param);
static void uart_pipe_xon_hook(struct avr_irq_t *irq, uint32_t value, void *param);
static void uart_pipe_xoff_hook(struct avr_irq_t *irq, uint32_t value, void *param);
static void uart_pipe_flush_to_avr(uart_pipe_t *bridge);
static void uart_pipe_pump(uart_pipe_t *bridge);

static bool file_exists(const char *path) {
  DWORD attrs = GetFileAttributesA(path);
  return attrs != INVALID_FILE_ATTRIBUTES && !(attrs & FILE_ATTRIBUTE_DIRECTORY);
}

static bool make_permissive_pipe_security(SECURITY_ATTRIBUTES *sa, SECURITY_DESCRIPTOR *sd) {
  if (!InitializeSecurityDescriptor(sd, SECURITY_DESCRIPTOR_REVISION)) {
    return false;
  }
  if (!SetSecurityDescriptorDacl(sd, TRUE, NULL, FALSE)) {
    return false;
  }
  sa->nLength = sizeof(*sa);
  sa->lpSecurityDescriptor = sd;
  sa->bInheritHandle = FALSE;
  return true;
}

static void uart_pipe_in_hook(struct avr_irq_t *irq, uint32_t value, void *param) {
  (void)irq;
  uart_pipe_t *bridge = (uart_pipe_t *)param;
  uart_pipe_fifo_write(&bridge->avr_to_host, (uint8_t)value);
}

static void uart_pipe_xon_hook(struct avr_irq_t *irq, uint32_t value, void *param) {
  (void)irq;
  (void)value;
  uart_pipe_t *bridge = (uart_pipe_t *)param;
  bridge->xon = 1;
  uart_pipe_flush_to_avr(bridge);
}

static void uart_pipe_xoff_hook(struct avr_irq_t *irq, uint32_t value, void *param) {
  (void)irq;
  (void)value;
  uart_pipe_t *bridge = (uart_pipe_t *)param;
  bridge->xon = 0;
}

static bool uart_pipe_open(uart_pipe_t *bridge, const char *pipe_name, FILE *log) {
  char pipe_path[256];
  SECURITY_ATTRIBUTES sa;
  SECURITY_DESCRIPTOR sd;
  snprintf(pipe_path, sizeof(pipe_path), "\\\\.\\pipe\\%s", pipe_name);

  if (!make_permissive_pipe_security(&sa, &sd)) {
    log_line(log, "[bridge] failed to configure pipe security: %lu", GetLastError());
    return false;
  }

  bridge->pipe_handle = CreateNamedPipeA(
      pipe_path,
      PIPE_ACCESS_DUPLEX,
      PIPE_TYPE_BYTE | PIPE_READMODE_BYTE | PIPE_WAIT,
      1,
      4096,
      4096,
      0,
      &sa);

  if (bridge->pipe_handle == INVALID_HANDLE_VALUE) {
    log_line(log, "[bridge] CreateNamedPipe failed: %lu", GetLastError());
    return false;
  }

  log_line(log, "[bridge] waiting for Tera Term on %s", pipe_path);
  BOOL connected = ConnectNamedPipe(bridge->pipe_handle, NULL);
  if (!connected) {
    DWORD err = GetLastError();
    if (err != ERROR_PIPE_CONNECTED) {
      log_line(log, "[bridge] ConnectNamedPipe failed: %lu", err);
      CloseHandle(bridge->pipe_handle);
      bridge->pipe_handle = INVALID_HANDLE_VALUE;
      return false;
    }
  }

  log_line(log, "[bridge] Tera Term connected");
  return true;
}

static void uart_pipe_close(uart_pipe_t *bridge) {
  if (bridge->pipe_handle != INVALID_HANDLE_VALUE) {
    FlushFileBuffers(bridge->pipe_handle);
    DisconnectNamedPipe(bridge->pipe_handle);
    CloseHandle(bridge->pipe_handle);
    bridge->pipe_handle = INVALID_HANDLE_VALUE;
  }
}

static void uart_pipe_flush_to_avr(uart_pipe_t *bridge) {
  while (bridge->xon && !uart_pipe_fifo_isempty(&bridge->host_to_avr)) {
    uint8_t byte = uart_pipe_fifo_read(&bridge->host_to_avr);
    avr_raise_irq(bridge->irq + IRQ_UART_PIPE_BYTE_OUT, byte);
  }
}

static void uart_pipe_flush_to_host(uart_pipe_t *bridge) {
  if (bridge->pipe_handle == INVALID_HANDLE_VALUE) {
    return;
  }

  uint8_t buffer[256];
  while (!uart_pipe_fifo_isempty(&bridge->avr_to_host)) {
    size_t count = 0;
    while (count < sizeof(buffer) && !uart_pipe_fifo_isempty(&bridge->avr_to_host)) {
      buffer[count++] = uart_pipe_fifo_read(&bridge->avr_to_host);
    }

    size_t start = 0;
    for (size_t i = 0; i < count; ++i) {
      uint8_t byte = buffer[i];
      if (byte == 0x11u || byte == 0x13u) {
        if (i > start) {
          DWORD written = 0;
          if (!WriteFile(bridge->pipe_handle, &buffer[start], (DWORD)(i - start), &written, NULL)) {
            log_line(bridge->log, "[bridge] WriteFile failed: %lu", GetLastError());
            return;
          }
          log_bytes(bridge->log, "[bridge:uart->host]", &buffer[start], written);
          if (written < (DWORD)(i - start)) {
            return;
          }
        }
        {
          DWORD written = 0;
          uint8_t ctrl = byte;
          if (!WriteFile(bridge->pipe_handle, &ctrl, 1, &written, NULL)) {
            log_line(bridge->log, "[bridge] WriteFile failed: %lu", GetLastError());
            return;
          }
          if (written < 1) {
            return;
          }
        }
        bridge->xon = (byte == 0x11u) ? 1 : 0;
        log_line(bridge->log, byte == 0x11u ? "[bridge] XON from target" : "[bridge] XOFF from target");
        start = i + 1;
        continue;
      }
    }

    if (start < count) {
      DWORD written = 0;
      if (!WriteFile(bridge->pipe_handle, &buffer[start], (DWORD)(count - start), &written, NULL)) {
        log_line(bridge->log, "[bridge] WriteFile failed: %lu", GetLastError());
        break;
      }

      log_bytes(bridge->log, "[bridge:uart->host]", &buffer[start], written);
      if (written < (DWORD)(count - start)) {
        break;
      }
    }
  }
}

static void uart_pipe_pump(uart_pipe_t *bridge) {
  if (bridge->pipe_handle == INVALID_HANDLE_VALUE) {
    return;
  }

  DWORD available = 0;
  if (PeekNamedPipe(bridge->pipe_handle, NULL, 0, NULL, &available, NULL) && available > 0) {
    uint8_t buffer[256];
    DWORD to_read = available < sizeof(buffer) ? available : (DWORD)sizeof(buffer);
    DWORD read = 0;
    if (ReadFile(bridge->pipe_handle, buffer, to_read, &read, NULL) && read > 0) {
      log_bytes(bridge->log, "[bridge:host->uart]", buffer, read);
      for (DWORD i = 0; i < read; ++i) {
        uart_pipe_fifo_write(&bridge->host_to_avr, buffer[i]);
      }
    } else if (GetLastError() == ERROR_BROKEN_PIPE) {
      log_line(bridge->log, "[bridge] Tera Term disconnected");
      return;
    }
  }

  uart_pipe_flush_to_avr(bridge);
  uart_pipe_flush_to_host(bridge);
}

static bool uart_pipe_attach(uart_pipe_t *bridge, avr_t *avr, FILE *log) {
  memset(bridge, 0, sizeof(*bridge));
  bridge->avr = avr;
  bridge->pipe_handle = INVALID_HANDLE_VALUE;
  bridge->xon = 1;
  bridge->log = log;
  bridge->irq = avr_alloc_irq(&avr->irq_pool, 0, IRQ_UART_PIPE_COUNT, kPipeIrqNames);

  if (bridge->irq == NULL) {
    log_line(log, "[bridge] failed to allocate IRQs");
    return false;
  }

  avr_irq_register_notify(bridge->irq + IRQ_UART_PIPE_BYTE_IN, uart_pipe_in_hook, bridge);

  uint32_t flags = 0;
  avr_ioctl(avr, AVR_IOCTL_UART_GET_FLAGS('0'), &flags);
  flags &= ~AVR_UART_FLAG_STDIO;
  avr_ioctl(avr, AVR_IOCTL_UART_SET_FLAGS('0'), &flags);

  avr_irq_t *src = avr_io_getirq(avr, AVR_IOCTL_UART_GETIRQ('0'), UART_IRQ_OUTPUT);
  avr_irq_t *dst = avr_io_getirq(avr, AVR_IOCTL_UART_GETIRQ('0'), UART_IRQ_INPUT);
  avr_irq_t *xon = avr_io_getirq(avr, AVR_IOCTL_UART_GETIRQ('0'), UART_IRQ_OUT_XON);
  avr_irq_t *xoff = avr_io_getirq(avr, AVR_IOCTL_UART_GETIRQ('0'), UART_IRQ_OUT_XOFF);

  if (src && dst) {
    avr_connect_irq(src, bridge->irq + IRQ_UART_PIPE_BYTE_IN);
    avr_connect_irq(bridge->irq + IRQ_UART_PIPE_BYTE_OUT, dst);
  } else {
    log_line(log, "[bridge] UART0 IRQ wiring failed");
    return false;
  }
  if (xon) {
    avr_irq_register_notify(xon, uart_pipe_xon_hook, bridge);
  }
  if (xoff) {
    avr_irq_register_notify(xoff, uart_pipe_xoff_hook, bridge);
  }

  return true;
}

static int parse_int(const char *value) {
  return (int)strtol(value, NULL, 10);
}

int main(int argc, char **argv) {
  const char *firmware_path = NULL;
  const char *mmcu_override = NULL;
  const char *pipe_name = kDefaultPipeName;
  const char *log_path = kDefaultLogPath;
  uint32_t freq_override = 0;
  int gdb = 0;
  int gdb_port = 1234;
  int log_level = 0;
  elf_firmware_t fw = {0};
  FILE *log = NULL;
  uart_pipe_t bridge;

  for (int i = 1; i < argc; ++i) {
    if (!strcmp(argv[i], "--firmware") || !strcmp(argv[i], "--elf")) {
      if (i + 1 >= argc) {
        usage(argv[0]);
        return 1;
      }
      firmware_path = argv[++i];
    } else if (!strcmp(argv[i], "--mcu")) {
      if (i + 1 >= argc) {
        usage(argv[0]);
        return 1;
      }
      mmcu_override = argv[++i];
    } else if (!strcmp(argv[i], "--freq")) {
      if (i + 1 >= argc) {
        usage(argv[0]);
        return 1;
      }
      freq_override = (uint32_t)strtoul(argv[++i], NULL, 10);
    } else if (!strcmp(argv[i], "--pipe-name")) {
      if (i + 1 >= argc) {
        usage(argv[0]);
        return 1;
      }
      pipe_name = argv[++i];
    } else if (!strcmp(argv[i], "--log-path")) {
      if (i + 1 >= argc) {
        usage(argv[0]);
        return 1;
      }
      log_path = argv[++i];
    } else if (!strcmp(argv[i], "-g") || !strcmp(argv[i], "--gdb")) {
      gdb = 1;
      if (i + 1 < argc && argv[i + 1][0] != '-') {
        gdb_port = parse_int(argv[++i]);
      }
    } else if (!strcmp(argv[i], "-v")) {
      ++log_level;
    } else if (!strcmp(argv[i], "-h") || !strcmp(argv[i], "--help")) {
      usage(argv[0]);
      return 0;
    } else {
      fprintf(stderr, "Unknown argument: %s\n", argv[i]);
      usage(argv[0]);
      return 1;
    }
  }

  if (firmware_path == NULL) {
    firmware_path = kDefaultFirmware;
    if (!file_exists(firmware_path)) {
      firmware_path = kFallbackFirmware;
    }
  }

  if (!create_directory_for_file(log_path)) {
    fprintf(stderr, "Unable to create log directory for %s\n", log_path);
    return 1;
  }

  log = fopen(log_path, "a");
  if (log == NULL) {
    fprintf(stderr, "Unable to open log file %s\n", log_path);
    return 1;
  }
  setvbuf(log, NULL, _IOLBF, 0);

  log_line(log, "[bridge] pipe=\\\\.\\pipe\\%s", pipe_name);
  log_line(log, "[bridge] firmware=%s", firmware_path);

  if (!file_exists(firmware_path)) {
    log_line(log, "[bridge] missing firmware image");
    fclose(log);
    return 1;
  }

  sim_setup_firmware(firmware_path, AVR_SEGMENT_OFFSET_FLASH, &fw, argv[0]);
  if (mmcu_override != NULL) {
    snprintf(fw.mmcu, sizeof(fw.mmcu), "%s", mmcu_override);
  }
  if (freq_override != 0) {
    fw.frequency = freq_override;
  }
  if (!fw.mmcu[0]) {
    log_line(log, "[bridge] firmware did not provide an MCU and none was supplied");
    fclose(log);
    return 1;
  }

  g_avr = avr_make_mcu_by_name(fw.mmcu);
  if (g_avr == NULL) {
    log_line(log, "[bridge] unknown AVR MCU: %s", fw.mmcu);
    fclose(log);
    return 1;
  }

  avr_init(g_avr);
  if (fw.frequency != 0) {
    g_avr->frequency = fw.frequency;
  }
  g_avr->log = log_level;
  avr_load_firmware(g_avr, &fw);
  if (fw.flashbase) {
    g_avr->pc = fw.flashbase;
  }

  g_avr->gdb_port = gdb_port;
  if (gdb) {
    g_avr->state = cpu_Stopped;
    avr_gdb_init(g_avr);
  }

  if (!uart_pipe_attach(&bridge, g_avr, log)) {
    avr_terminate(g_avr);
    fclose(log);
    return 1;
  }

  signal(SIGINT, handle_signal);
  signal(SIGTERM, handle_signal);

  if (!uart_pipe_open(&bridge, pipe_name, log)) {
    uart_pipe_close(&bridge);
    avr_terminate(g_avr);
    fclose(log);
    return 1;
  }

  log_line(log, "[bridge] avrsim starting");

  for (;;) {
    int state = avr_run(g_avr);
    uart_pipe_pump(&bridge);
    if (state == cpu_Done || state == cpu_Crashed) {
      break;
    }
  }

  uart_pipe_close(&bridge);
  avr_terminate(g_avr);
  log_line(log, "[bridge] avrsim exited");
  fclose(log);
  return 0;
}
