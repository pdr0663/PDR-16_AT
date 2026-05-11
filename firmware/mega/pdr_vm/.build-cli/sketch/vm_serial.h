#line 1 "C:\\Users\\pdr0663\\PDR-16_XT\\firmware\\mega\\pdr_vm\\vm_serial.h"
#ifndef PDR_VM_SERIAL_H
#define PDR_VM_SERIAL_H

#include <Arduino.h>
#include <stdint.h>

#include "vm_config.h"

static void vm_serial_init(void) {
  Serial.begin(VM_BAUD_RATE);
  unsigned long start_ms = millis();
  while (!Serial && (millis() - start_ms) < 2000ul) {
  }
}

static uint8_t vm_serial_readable(void) {
  return (uint8_t)(Serial.available() > 0);
}

static int vm_serial_peek(void) {
  return Serial.peek();
}

static uint8_t vm_serial_read(void) {
  int value = Serial.read();
  if (value < 0) {
    return 0u;
  }
  return (uint8_t)value;
}

static void vm_serial_write(uint8_t value) {
  Serial.write(value);
}

static void vm_serial_print_hex16(uint16_t value) {
  static const char hex_digits[] = "0123456789ABCDEF";
  char buffer[4];
  buffer[0] = hex_digits[(value >> 12) & 0x0Fu];
  buffer[1] = hex_digits[(value >> 8) & 0x0Fu];
  buffer[2] = hex_digits[(value >> 4) & 0x0Fu];
  buffer[3] = hex_digits[value & 0x0Fu];
  Serial.write(buffer, sizeof(buffer));
}

static void vm_serial_print_hex8(uint8_t value) {
  static const char hex_digits[] = "0123456789ABCDEF";
  char buffer[2];
  buffer[0] = hex_digits[(value >> 4) & 0x0Fu];
  buffer[1] = hex_digits[value & 0x0Fu];
  Serial.write(buffer, sizeof(buffer));
}

#endif
