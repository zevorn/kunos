# QEMU Boot

There are two QEMU paths.

## Standard RISC-V QEMU Smoke Test

Use the upstream `qemuriscv64` machine to verify the layer's userspace and image
metadata with standard Yocto tooling:

```bash
source poky/oe-init-build-env build
MACHINE=qemuriscv64 bitbake k230-qemu-image
runqemu qemuriscv64 k230-qemu-image nographic slirp
```

This path uses QEMU's `virt` board. It does not emulate K230 peripherals.

## K230 QEMU Machine

K230 SoC emulation requires a QEMU build that provides `-M k230`. The system
QEMU shipped by many distributions only provides `virt` for RISC-V.

After building the K230 artifacts:

```bash
source poky/oe-init-build-env build
MACHINE=k230-canmv bitbake linux-k230 k230-initramfs-image
```

boot them with:

```bash
QEMU=/path/to/qemu-system-riscv64 \
OPENSBI=/path/to/opensbi-riscv64-generic-fw_dynamic.bin \
DEPLOY_DIR=tmp/deploy/images/k230-canmv \
../meta-k230/scripts/boot-qemu-k230.sh
```

The script checks that the QEMU binary supports `-M k230` before booting.
