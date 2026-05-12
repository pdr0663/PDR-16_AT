# 1 "C:\\Users\\Paul.Riley\\PDR-16_XT\\firmware\\mega\\pdr_vm\\pdr_vm.ino"
# 2 "C:\\Users\\Paul.Riley\\PDR-16_XT\\firmware\\mega\\pdr_vm\\pdr_vm.ino" 2

# 4 "C:\\Users\\Paul.Riley\\PDR-16_XT\\firmware\\mega\\pdr_vm\\pdr_vm.ino" 2
# 5 "C:\\Users\\Paul.Riley\\PDR-16_XT\\firmware\\mega\\pdr_vm\\pdr_vm.ino" 2
# 6 "C:\\Users\\Paul.Riley\\PDR-16_XT\\firmware\\mega\\pdr_vm\\pdr_vm.ino" 2
# 7 "C:\\Users\\Paul.Riley\\PDR-16_XT\\firmware\\mega\\pdr_vm\\pdr_vm.ino" 2

static machine_state_t g_vm;

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
# 49 "C:\\Users\\Paul.Riley\\PDR-16_XT\\firmware\\mega\\pdr_vm\\pdr_vm.ino"
}

void setup(void) {
  vm_serial_init();
  vm_reset(&g_vm);
}

void loop(void) {
  vm_probe_host_serial();
  if (g_vm.running) {
    vm_run_budget(&g_vm, 256u);
    return;
  }
  if (!g_vm.reported_fault) {
    vm_report_status(&g_vm);
    g_vm.reported_fault = 1u;
  }
}
