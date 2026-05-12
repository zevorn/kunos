# meta-k230

OpenEmbedded/Yocto BSP layer for the Canaan Kendryte K230 CanMV board and
K230-oriented boot experiments.

The layer is intentionally small. It provides:

* `k230-canmv`, a K230 CanMV machine configuration.
* `linux-k230`, a mainline Linux kernel recipe with a minimal K230 DTB.
* `k230-initramfs-image`, a BusyBox initramfs for K230 bring-up.
* `k230-qemu-image`, a small QEMU-bootable root filesystem for RISC-V smoke
  testing with `qemuriscv64`.
* helper scripts and documentation for build, QEMU, and board boot flows.

## Dependencies

This layer depends on:

* `poky` / OpenEmbedded-Core, `scarthgap`
* `meta-riscv`, `scarthgap`

The layer has no runtime dependency on proprietary binaries. Real hardware boot
still depends on a board-specific first-stage boot chain supplied outside this
repository.

## Quick Start

From a Yocto workspace containing `poky`, `meta-riscv`, and `meta-k230`:

```bash
source poky/oe-init-build-env build
bitbake-layers add-layer ../meta-riscv
bitbake-layers add-layer ../meta-k230
```

Build the K230 initramfs artifacts:

```bash
MACHINE=k230-canmv bitbake linux-k230 k230-initramfs-image
```

Build the QEMU smoke image:

```bash
MACHINE=qemuriscv64 bitbake k230-qemu-image
runqemu qemuriscv64 k230-qemu-image nographic slirp
```

Run the layer checks:

```bash
scripts/check-layer.sh
```

## Boot Outputs

For `MACHINE=k230-canmv`, BitBake deploys the main boot artifacts under:

```text
tmp/deploy/images/k230-canmv/
```

The important files are:

* `Image`
* `k230-canmv.dtb`
* `k230-initramfs-image-k230-canmv.rootfs.cpio.gz`

See [docs/boot-k230-canmv.md](docs/boot-k230-canmv.md) for board boot notes and
[docs/boot-qemu.md](docs/boot-qemu.md) for QEMU boot notes.

## Project Policy

`meta-k230` is a BSP layer. Keep hardware support, distribution policy, and
binary artifacts separate. Recipes should fetch source through BitBake fetchers
and should not access the network outside `do_fetch`.
