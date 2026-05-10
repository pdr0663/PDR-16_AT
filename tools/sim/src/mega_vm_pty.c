#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "sim_avr.h"
#include "sim_elf.h"
#include "sim_gdb.h"
#include "sim_hex.h"
#include "uart_pty.h"

static avr_t *g_avr = NULL;
static uart_pty_t g_uart_pty;

static void handle_signal(int signum) {
  (void)signum;
  if (g_avr != NULL) {
    avr_terminate(g_avr);
  }
}

static void usage(const char *argv0) {
  fprintf(stderr, "Usage: %s [--firmware <path>] [--mcu <name>] [--freq <hz>] [-g [port]] [-v]\n", argv0);
}

int main(int argc, char **argv) {
  const char *firmware_path = NULL;
  const char *mmcu_override = NULL;
  uint32_t freq_override = 0;
  int gdb = 0;
  int gdb_port = 1234;
  int log_level = 0;
  elf_firmware_t fw = {{0}};

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
    } else if (!strcmp(argv[i], "-g") || !strcmp(argv[i], "--gdb")) {
      gdb = 1;
      if (i + 1 < argc && argv[i + 1][0] != '-') {
        gdb_port = atoi(argv[++i]);
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
    fprintf(stderr, "Missing --firmware <path>\n");
    usage(argv[0]);
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
    fprintf(stderr, "Firmware did not provide an MCU and none was supplied.\n");
    return 1;
  }

  g_avr = avr_make_mcu_by_name(fw.mmcu);
  if (g_avr == NULL) {
    fprintf(stderr, "Unknown AVR MCU: %s\n", fw.mmcu);
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

  signal(SIGINT, handle_signal);
  signal(SIGTERM, handle_signal);

  uart_pty_init(g_avr, &g_uart_pty);
  uart_pty_connect(&g_uart_pty, '0');

  for (;;) {
    int state = avr_run(g_avr);
    if (state == cpu_Done || state == cpu_Crashed) {
      break;
    }
  }

  uart_pty_stop(&g_uart_pty);
  avr_terminate(g_avr);
  return 0;
}
