#line 1 "C:\\Users\\pdr0663\\PDR-16_XT\\firmware\\mega\\pdr_vm\\pdr_vm.ino"
#include <Arduino.h>

#include "vm_config.h"
#include "vm_dispatch.h"
#include "vm_serial.h"
#include "vm_state.h"

static machine_state_t g_vm;

#line 10 "C:\\Users\\pdr0663\\PDR-16_XT\\firmware\\mega\\pdr_vm\\pdr_vm.ino"
static void vm_report_status(machine_state_t *vm);
#line 31 "C:\\Users\\pdr0663\\PDR-16_XT\\firmware\\mega\\pdr_vm\\pdr_vm.ino"
static void vm_probe_host_serial(void);
#line 51 "C:\\Users\\pdr0663\\PDR-16_XT\\firmware\\mega\\pdr_vm\\pdr_vm.ino"
void setup(void);
#line 56 "C:\\Users\\pdr0663\\PDR-16_XT\\firmware\\mega\\pdr_vm\\pdr_vm.ino"
void loop(void);
#line 10 "C:\\Users\\pdr0663\\PDR-16_XT\\firmware\\mega\\pdr_vm\\pdr_vm.ino"
static void vm_report_status(machine_state_t *vm) {
  Serial.print("\r\n[PDR-16/XT VM ");
  if (vm->fault == VM_FAULT_NONE) {
    Serial.print("stopped");
  } else {
    Serial.print("fault ");
    Serial.print(vm->fault);
  }
  Serial.print(" ip=$");
  vm_serial_print_hex16(vm->ip);
  Serial.print(" last=$");
  vm_serial_print_hex16(vm->last_ip);
  Serial.print(" detail=$");
  vm_serial_print_hex16(vm->fault_detail);
  Serial.print(" sp=$");
  vm_serial_print_hex16(vm->sp);
  Serial.print(" rp=$");
  vm_serial_print_hex16(vm->rp);
  Serial.print("]\r\n");
}

static void vm_probe_host_serial(void) {
#if VM_SERIAL_PEEK_TRACE
  static uint8_t announced_waiting = 0u;
  int peeked = vm_serial_peek();
  if (peeked >= 0 && !announced_waiting) {
    Serial.print("\r\n[HOSTWAIT $");
    vm_serial_print_hex8((uint8_t)peeked);
    Serial.print("]\r\n");
    announced_waiting = 1u;
  }
  if (peeked < 0) {
    announced_waiting = 0u;
  }
  if (g_vm_qrx_seen_input) {
    Serial.print("\r\n[QRX-CONSUMED]\r\n");
    g_vm_qrx_seen_input = 0u;
  }
#endif
}

void setup(void) {
  vm_serial_init();
  vm_reset(&g_vm);
}

void loop(void) {
  vm_probe_host_serial();
  if (g_vm.running) {
    vm_run_budget(&g_vm, VM_STEP_BUDGET);
    return;
  }
  if (!g_vm.reported_fault) {
    vm_report_status(&g_vm);
    g_vm.reported_fault = 1u;
  }
}

