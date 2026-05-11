#line 1 "C:\\Users\\pdr0663\\PDR-16_AT\\firmware\\mega\\pdr_vm\\vm_state.h"
#ifndef PDR_VM_STATE_H
#define PDR_VM_STATE_H

#include <stdint.h>
#include "vm_config.h"

enum vm_fault_t {
  VM_FAULT_NONE = 0,
  VM_FAULT_BAD_PRIMITIVE = 1,
  VM_FAULT_UNMAPPED_READ = 2,
  VM_FAULT_UNMAPPED_WRITE = 3,
  VM_FAULT_DATA_STACK_UNDERFLOW = 4,
  VM_FAULT_DATA_STACK_OVERFLOW = 5,
  VM_FAULT_RETURN_STACK_UNDERFLOW = 6,
  VM_FAULT_RETURN_STACK_OVERFLOW = 7,
  VM_FAULT_UNIMPLEMENTED_PRIMITIVE = 8,
  VM_FAULT_BAD_EXECUTE = 9,
};

typedef struct machine_state_t {
  uint16_t ip;
  uint16_t sp;
  uint16_t rp;
  uint16_t up;
  uint16_t last_ip;
  uint16_t fault_detail;
  uint8_t running;
  uint8_t reported_fault;
  uint8_t fault;
} machine_state_t;

/*
 * This draft VM does not cache TOS in a private C variable.
 * The visible Forth stacks live in the VM memory map so words like
 * SP@, SP!, DEPTH, PICK, CATCH, and THROW see the same stack state.
 */

static void vm_memory_reset(void);

static void vm_reset(machine_state_t *vm) {
  vm_memory_reset();
  vm->ip = VM_COLD_VECTOR;
  vm->sp = VM_SP_EMPTY;
  vm->rp = VM_RP_EMPTY;
  vm->up = VM_UPP;
  vm->last_ip = VM_COLD_VECTOR;
  vm->fault_detail = 0u;
  vm->running = 1u;
  vm->reported_fault = 0u;
  vm->fault = VM_FAULT_NONE;
}

static void vm_halt_fault(machine_state_t *vm, uint8_t fault, uint16_t detail) {
  vm->running = 0u;
  vm->fault = fault;
  vm->fault_detail = detail;
}

static void vm_halt_normal(machine_state_t *vm) {
  vm->running = 0u;
  if (vm->fault == VM_FAULT_NONE) {
    vm->fault_detail = vm->ip;
  }
}

#endif
