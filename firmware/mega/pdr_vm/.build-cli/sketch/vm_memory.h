#line 1 "C:\\Users\\pdr0663\\PDR-16_AT\\firmware\\mega\\pdr_vm\\vm_memory.h"
#ifndef PDR_VM_MEMORY_H
#define PDR_VM_MEMORY_H

#include <stdint.h>
#include <string.h>
#include <avr/pgmspace.h>
#include "generated/pdr16_at_forth_image.h"
#include "vm_config.h"
#include "vm_state.h"

static uint16_t g_vm_low_ram[VM_RAM_LOW_WORDS];
static uint16_t g_vm_high_ram[VM_RAM_HIGH_WORDS];

static uint16_t *vm_translate_ram_word(uint16_t addr) {
  if (addr >= VM_RAM_LOW_START && addr <= VM_RAM_LOW_END) {
    return &g_vm_low_ram[addr - VM_RAM_LOW_START];
  }
  if (addr >= VM_RAM_HIGH_START) {
    return &g_vm_high_ram[addr - VM_RAM_HIGH_START];
  }
  return (uint16_t *)0;
}

static void vm_memory_reset(void) {
  memset(g_vm_low_ram, 0, sizeof(g_vm_low_ram));
  memset(g_vm_high_ram, 0, sizeof(g_vm_high_ram));
}

static uint16_t vm_read_rom_word(uint16_t addr) {
  return pdr16_at_rom_read_word(addr);
}

static uint16_t vm_read_word(machine_state_t *vm, uint16_t addr) {
  uint16_t *ram_word = vm_translate_ram_word(addr);
  if (addr <= VM_ROM_END) {
    return vm_read_rom_word(addr);
  }
  if (ram_word != (uint16_t *)0) {
    return *ram_word;
  }
  vm_halt_fault(vm, VM_FAULT_UNMAPPED_READ, addr);
  return 0u;
}

static void vm_write_word(machine_state_t *vm, uint16_t addr, uint16_t value) {
  uint16_t *ram_word = vm_translate_ram_word(addr);
  if (addr <= VM_ROM_END) {
    return;
  }
  if (ram_word != (uint16_t *)0) {
    *ram_word = value;
    return;
  }
  vm_halt_fault(vm, VM_FAULT_UNMAPPED_WRITE, addr);
}

static uint16_t vm_read_byte(machine_state_t *vm, uint16_t addr) {
  return vm_read_word(vm, addr);
}

static void vm_write_byte(machine_state_t *vm, uint16_t addr, uint16_t value) {
  vm_write_word(vm, addr, value);
}

#endif
