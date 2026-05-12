# K230 CanMV Boot

`k230-canmv` targets the Linux-capable little core on Canaan K230 CanMV boards.
The layer builds the Linux payload and initramfs only; it does not replace the
board's first-stage boot chain.

## Build

```bash
source poky/oe-init-build-env build
MACHINE=k230-canmv bitbake linux-k230 k230-initramfs-image
```

Expected deploy artifacts:

```text
tmp/deploy/images/k230-canmv/Image
tmp/deploy/images/k230-canmv/k230-canmv.dtb
tmp/deploy/images/k230-canmv/k230-initramfs-image-k230-canmv.rootfs.cpio.gz
```

## Kernel Command Line

Use a serial console:

```text
console=ttyS0,115200 earlycon=sbi
```

The initramfs starts `/init`, mounts `/proc`, `/sys`, and `/dev`, then drops to
a BusyBox shell. A successful boot prints:

```text
meta-k230 initramfs starting...
Dropping to shell...
```

## Boot Loader Integration

Load the artifacts with the board boot loader using addresses that do not
overlap the boot chain, kernel, DTB, or initramfs. If the boot loader requires
explicit initramfs properties, set:

```text
/chosen/linux,initrd-start
/chosen/linux,initrd-end
```

The exact flashing and load-address procedure is board firmware specific and is
kept outside this layer.
