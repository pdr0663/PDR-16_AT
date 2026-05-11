#ifndef PDR_VM_PRIMITIVES_H
#define PDR_VM_PRIMITIVES_H

#include <stdint.h>

#include "vm_memory.h"
#include "vm_serial.h"
#include "vm_state.h"

typedef void (*primitive_fn_t)(machine_state_t *vm);

static uint8_t g_vm_qrx_seen_input = 0u;

static uint16_t vm_pop(machine_state_t *vm) {
  if (vm->sp == VM_SP_EMPTY) {
    vm_halt_fault(vm, VM_FAULT_DATA_STACK_UNDERFLOW, vm->last_ip);
    return 0u;
  }
  vm->sp = (uint16_t)(vm->sp + 1u);
  return vm_read_word(vm, vm->sp);
}

static void vm_push(machine_state_t *vm, uint16_t value) {
  if (vm->sp < VM_DATA_STACK_WRITE_FLOOR) {
    vm_halt_fault(vm, VM_FAULT_DATA_STACK_OVERFLOW, vm->last_ip);
    return;
  }
  vm_write_word(vm, vm->sp, value);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm->sp = (uint16_t)(vm->sp - 1u);
}

static uint16_t vm_rpeek(machine_state_t *vm) {
  if (vm->rp == VM_RP_EMPTY) {
    vm_halt_fault(vm, VM_FAULT_RETURN_STACK_UNDERFLOW, vm->last_ip);
    return 0u;
  }
  return vm_read_word(vm, (uint16_t)(vm->rp + 1u));
}

static uint16_t vm_rpop(machine_state_t *vm) {
  if (vm->rp == VM_RP_EMPTY) {
    vm_halt_fault(vm, VM_FAULT_RETURN_STACK_UNDERFLOW, vm->last_ip);
    return 0u;
  }
  vm->rp = (uint16_t)(vm->rp + 1u);
  return vm_read_word(vm, vm->rp);
}

static void vm_rpush(machine_state_t *vm, uint16_t value) {
  if (vm->rp < VM_RETURN_STACK_WRITE_FLOOR) {
    vm_halt_fault(vm, VM_FAULT_RETURN_STACK_OVERFLOW, vm->last_ip);
    return;
  }
  vm_write_word(vm, vm->rp, value);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm->rp = (uint16_t)(vm->rp - 1u);
}

static uint16_t vm_peek(machine_state_t *vm, uint16_t depth) {
  return vm_read_word(vm, (uint16_t)(vm->sp + 1u + depth));
}

static void vm_call(machine_state_t *vm, uint16_t xt) {
  if (xt < 64u) {
    vm_halt_fault(vm, VM_FAULT_BAD_EXECUTE, xt);
    return;
  }
  vm_rpush(vm, vm->ip);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm->ip = xt;
}

static void prim_reserved(machine_state_t *vm) {
  vm_halt_fault(vm, VM_FAULT_BAD_PRIMITIVE, vm->last_ip);
}

static void prim_unimplemented(machine_state_t *vm) {
  vm_halt_fault(vm, VM_FAULT_UNIMPLEMENTED_PRIMITIVE, vm->last_ip);
}

static void prim_NOP(machine_state_t *vm) {
  (void)vm;
}

static void prim_jump(machine_state_t *vm) {
  vm->ip = vm_read_word(vm, vm->ip);
}

static void prim_qrx(machine_state_t *vm) {
  if (vm_serial_readable()) {
    uint8_t raw = vm_serial_read();
    g_vm_qrx_seen_input = 1u;
#if VM_SERIAL_RX_TRACE
    Serial.print("\r\n[RX $");
    vm_serial_print_hex8(raw);
    Serial.print("]\r\n");
#endif
    vm_push(vm, (uint16_t)raw);
    vm_push(vm, 0xFFFFu);
    return;
  }
  vm_push(vm, 0u);
}

static void prim_tx_store(machine_state_t *vm) {
  uint16_t value = vm_pop(vm);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm_serial_write((uint8_t)(value & 0x00FFu));
}

static void prim_doLIT(machine_state_t *vm) {
  uint16_t literal = vm_read_word(vm, vm->ip);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm->ip = (uint16_t)(vm->ip + 1u);
  vm_push(vm, literal);
}

static void prim_doLIST(machine_state_t *vm) {
  uint16_t addr = vm_pop(vm);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm_rpush(vm, vm->ip);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm->ip = addr;
}

static void prim_doVAR(machine_state_t *vm) {
  uint16_t data_addr = vm->ip;
  vm_push(vm, data_addr);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  if (vm->rp == VM_RP_EMPTY) {
    vm_halt_normal(vm);
    return;
  }
  vm->ip = vm_rpop(vm);
}

static void prim_doNEXT(machine_state_t *vm) {
  uint16_t target = vm_read_word(vm, vm->ip);
  uint16_t counter;
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm->ip = (uint16_t)(vm->ip + 1u);
  counter = vm_rpeek(vm);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  counter = (uint16_t)(counter + 1u);
  vm_write_word(vm, (uint16_t)(vm->rp + 1u), counter);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  if (counter != 0u) {
    vm->ip = target;
  }
}

static void prim_qbranch(machine_state_t *vm) {
  uint16_t target = vm_read_word(vm, vm->ip);
  uint16_t flag;
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm->ip = (uint16_t)(vm->ip + 1u);
  flag = vm_pop(vm);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  if (flag == 0u) {
    vm->ip = target;
  }
}

static void prim_branch(machine_state_t *vm) {
  vm->ip = vm_read_word(vm, vm->ip);
}

static void prim_EXECUTE(machine_state_t *vm) {
  uint16_t xt = vm_pop(vm);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  if (xt < 64u) {
    prim_reserved(vm);
    return;
  }
  vm_call(vm, xt);
}

static void prim_EXIT(machine_state_t *vm) {
  if (vm->rp == VM_RP_EMPTY) {
    vm_halt_normal(vm);
    return;
  }
  vm->ip = vm_rpop(vm);
}

static void prim_store(machine_state_t *vm) {
  uint16_t addr = vm_pop(vm);
  uint16_t value;
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  value = vm_pop(vm);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm_write_word(vm, addr, value);
}

static void prim_fetch(machine_state_t *vm) {
  uint16_t addr = vm_pop(vm);
  uint16_t value;
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  value = vm_read_word(vm, addr);
  vm_push(vm, value);
}

static void prim_cstore(machine_state_t *vm) {
  uint16_t addr = vm_pop(vm);
  uint16_t value;
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  value = vm_pop(vm);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm_write_byte(vm, addr, value);
}

static void prim_cfetch(machine_state_t *vm) {
  uint16_t addr = vm_pop(vm);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm_push(vm, (uint16_t)vm_read_byte(vm, addr));
}

static void prim_RP_store(machine_state_t *vm) {
  uint16_t visible_addr = vm_pop(vm);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm->rp = visible_addr;
}

static void prim_RP_fetch(machine_state_t *vm) {
  vm_push(vm, vm->rp);
}

static void prim_R_from(machine_state_t *vm) {
  uint16_t value = vm_rpop(vm);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm_push(vm, value);
}

static void prim_R_fetch(machine_state_t *vm) {
  vm_push(vm, vm_rpeek(vm));
}

static void prim_to_R(machine_state_t *vm) {
  uint16_t value = vm_pop(vm);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm_rpush(vm, value);
}

static void prim_SP_fetch(machine_state_t *vm) {
  vm_push(vm, vm->sp);
}

static void prim_SP_store(machine_state_t *vm) {
  uint16_t visible_addr = vm_pop(vm);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm->sp = visible_addr;
}

static void prim_DROP(machine_state_t *vm) {
  (void)vm_pop(vm);
}

static void prim_DUP(machine_state_t *vm) {
  vm_push(vm, vm_peek(vm, 0u));
}

static void prim_SWAP(machine_state_t *vm) {
  uint16_t top = vm_peek(vm, 0u);
  uint16_t next = vm_peek(vm, 1u);
  vm_write_word(vm, (uint16_t)(vm->sp + 1u), next);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm_write_word(vm, (uint16_t)(vm->sp + 2u), top);
}

static void prim_OVER(machine_state_t *vm) {
  vm_push(vm, vm_peek(vm, 1u));
}

static void prim_0less(machine_state_t *vm) {
  int16_t value = (int16_t)vm_pop(vm);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm_push(vm, (value < 0) ? 0xFFFFu : 0u);
}

static void prim_AND(machine_state_t *vm) {
  uint16_t b = vm_pop(vm);
  uint16_t a;
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  a = vm_pop(vm);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm_push(vm, (uint16_t)(a & b));
}

static void prim_OR(machine_state_t *vm) {
  uint16_t b = vm_pop(vm);
  uint16_t a;
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  a = vm_pop(vm);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm_push(vm, (uint16_t)(a | b));
}

static void prim_XOR(machine_state_t *vm) {
  uint16_t b = vm_pop(vm);
  uint16_t a;
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  a = vm_pop(vm);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm_push(vm, (uint16_t)(a ^ b));
}

static void prim_UMplus(machine_state_t *vm) {
  uint16_t b = vm_pop(vm);
  uint16_t a;
  uint32_t sum;
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  a = vm_pop(vm);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  sum = (uint32_t)a + (uint32_t)b;
  vm_push(vm, (uint16_t)(sum & 0xFFFFu));
  vm_push(vm, (sum > 0xFFFFu) ? 1u : 0u);
}

static void prim_shift_left_4(machine_state_t *vm) {
  uint16_t value = vm_pop(vm);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm_push(vm, (uint16_t)(value << 4));
}

static void prim_shift_left_8(machine_state_t *vm) {
  uint16_t value = vm_pop(vm);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm_push(vm, (uint16_t)(value << 8));
}

static void prim_shift_left_9(machine_state_t *vm) {
  uint16_t value = vm_pop(vm);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm_push(vm, (uint16_t)(value << 9));
}

static void prim_0equals(machine_state_t *vm) {
  uint16_t value = vm_pop(vm);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm_push(vm, (value == 0u) ? 0xFFFFu : 0u);
}

static void prim_inc1(machine_state_t *vm) {
  uint16_t value = vm_pop(vm);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm_push(vm, (uint16_t)(value + 1u));
}

static void prim_dec1(machine_state_t *vm) {
  uint16_t value = vm_pop(vm);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm_push(vm, (uint16_t)(value - 1u));
}

static void prim_inc2(machine_state_t *vm) {
  uint16_t value = vm_pop(vm);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm_push(vm, (uint16_t)(value + 2u));
}

static void prim_dec2(machine_state_t *vm) {
  uint16_t value = vm_pop(vm);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm_push(vm, (uint16_t)(value - 2u));
}

static void prim_NOT(machine_state_t *vm) {
  uint16_t value = vm_pop(vm);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm_push(vm, (uint16_t)(~value));
}

static void prim_SUB(machine_state_t *vm) {
  uint16_t b = vm_pop(vm);
  uint16_t a;
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  a = vm_pop(vm);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm_push(vm, (uint16_t)(a - b));
}

static void prim_NEGATE(machine_state_t *vm) {
  uint16_t value = vm_pop(vm);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm_push(vm, (uint16_t)(0u - value));
}

static void prim_INC(machine_state_t *vm) {
  prim_inc1(vm);
}

static void prim_DEC(machine_state_t *vm) {
  prim_dec1(vm);
}

static void prim_ZERO(machine_state_t *vm) {
  (void)vm_pop(vm);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm_push(vm, 0u);
}

static void prim_Uplus(machine_state_t *vm) {
  uint16_t b = vm_pop(vm);
  uint16_t a;
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  a = vm_pop(vm);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm_push(vm, (uint16_t)(a + b));
}

static void prim_2star(machine_state_t *vm) {
  uint16_t value = vm_pop(vm);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm_push(vm, (uint16_t)(value << 1));
}

static void prim_UMstar(machine_state_t *vm) {
  uint16_t multiplier = vm_pop(vm);
  uint16_t multiplicand;
  uint32_t product;
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  multiplicand = vm_pop(vm);
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  product = (uint32_t)multiplicand * (uint32_t)multiplier;
  vm_push(vm, (uint16_t)(product & 0xFFFFu));
  if (!vm->running && vm->fault != VM_FAULT_NONE) {
    return;
  }
  vm_push(vm, (uint16_t)((product >> 16) & 0xFFFFu));
}

static const primitive_fn_t primitive_table[64] = {
  prim_NOP,
  prim_jump,
  prim_qrx,
  prim_tx_store,
  prim_doLIT,
  prim_doLIST,
  prim_doVAR,
  prim_doNEXT,
  prim_qbranch,
  prim_branch,
  prim_EXECUTE,
  prim_EXIT,
  prim_store,
  prim_fetch,
  prim_cstore,
  prim_cfetch,
  prim_RP_store,
  prim_RP_fetch,
  prim_R_from,
  prim_R_fetch,
  prim_to_R,
  prim_SP_fetch,
  prim_SP_store,
  prim_DROP,
  prim_DUP,
  prim_SWAP,
  prim_OVER,
  prim_0less,
  prim_AND,
  prim_OR,
  prim_XOR,
  prim_UMplus,
  prim_shift_left_4,
  prim_shift_left_8,
  prim_shift_left_9,
  prim_0equals,
  prim_inc1,
  prim_dec1,
  prim_inc2,
  prim_dec2,
  prim_unimplemented,
  prim_unimplemented,
  prim_unimplemented,
  prim_unimplemented,
  prim_unimplemented,
  prim_unimplemented,
  prim_unimplemented,
  prim_unimplemented,
  prim_unimplemented,
  prim_unimplemented,
  prim_unimplemented,
  prim_UMstar,
  prim_unimplemented,
  prim_NOT,
  prim_SUB,
  prim_NEGATE,
  prim_INC,
  prim_DEC,
  prim_ZERO,
  prim_Uplus,
  prim_2star,
  prim_reserved,
  prim_reserved
};

#endif
