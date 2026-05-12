#line 1 "C:\\Users\\Paul.Riley\\PDR-16_XT\\firmware\\mega\\pdr_vm\\vm_dispatch.h"
#ifndef PDR_VM_DISPATCH_H
#define PDR_VM_DISPATCH_H

#include <stdint.h>

#include "vm_primitives.h"

static uint16_t g_vm_trace_steps = 0u;

static void vm_trace_step(machine_state_t *vm, uint16_t cell) {
  if (g_vm_trace_steps >= VM_TRACE_STEPS) {
    return;
  }
  ++g_vm_trace_steps;
  Serial.print(F("T ip=$"));
  vm_serial_print_hex16(vm->last_ip);
  Serial.print(F(" cell=$"));
  vm_serial_print_hex16(cell);
  Serial.print(F(" sp=$"));
  vm_serial_print_hex16(vm->sp);
  Serial.print(F(" rp=$"));
  vm_serial_print_hex16(vm->rp);
  Serial.print(F("\r\n"));
}

static void vm_step(machine_state_t *vm) {
  uint16_t cell;
  if (!vm->running) {
    return;
  }
  vm->last_ip = vm->ip;
  cell = vm_read_word(vm, vm->ip);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm_trace_step(vm, cell);
  vm->ip = (uint16_t)(vm->ip + 1u);
  if (cell < 64u) {
    primitive_table[cell](vm);
    return;
  }
  vm_call(vm, cell);
}

static void vm_run_budget(machine_state_t *vm, uint16_t step_budget) {
  uint16_t step_index;
  for (step_index = 0u; step_index < step_budget; ++step_index) {
    if (!vm->running) {
      return;
    }
    vm_step(vm);
  }
}

#endif
