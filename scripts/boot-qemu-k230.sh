#!/bin/sh
# SPDX-License-Identifier: MIT

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
YOCTO_DIR=$(CDPATH= cd -- "$REPO_DIR/.." && pwd)

QEMU=${QEMU:-qemu-system-riscv64}
DEPLOY_DIR=${DEPLOY_DIR:-"$YOCTO_DIR/build/tmp/deploy/images/k230-canmv"}
KERNEL=${KERNEL:-"$DEPLOY_DIR/Image"}
DTB=${DTB:-"$DEPLOY_DIR/k230-canmv.dtb"}
INITRD=${INITRD:-"$DEPLOY_DIR/k230-initramfs-image-k230-canmv.rootfs.cpio.gz"}
OPENSBI=${OPENSBI:-}

if ! command -v "$QEMU" >/dev/null 2>&1 && [ ! -x "$QEMU" ]; then
    echo "ERROR: QEMU binary not found: $QEMU" >&2
    exit 1
fi

if ! "$QEMU" -machine help | grep -Eq '(^|[[:space:]])k230([[:space:]]|$)'; then
    echo "ERROR: $QEMU does not support '-M k230'." >&2
    echo "Build or install a QEMU with Canaan K230 machine support." >&2
    exit 1
fi

if [ -z "$OPENSBI" ]; then
    echo "ERROR: set OPENSBI to opensbi-riscv64-generic-fw_dynamic.bin." >&2
    exit 1
fi

for artifact in "$OPENSBI" "$KERNEL" "$DTB" "$INITRD"; do
    if [ ! -r "$artifact" ]; then
        echo "ERROR: missing artifact: $artifact" >&2
        exit 1
    fi
done

exec "$QEMU" -M k230 \
    -bios "$OPENSBI" \
    -kernel "$KERNEL" \
    -dtb "$DTB" \
    -initrd "$INITRD" \
    -append "console=ttyS0,115200 earlycon=sbi" \
    -nographic -no-reboot
