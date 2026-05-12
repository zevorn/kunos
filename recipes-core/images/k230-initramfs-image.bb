SUMMARY = "K230 CanMV initramfs image with busybox and minimal init"
LICENSE = "MIT"

inherit image

IMAGE_INSTALL = "busybox init-script"

IMAGE_FSTYPES = "cpio.gz"

IMAGE_ROOTFS_SIZE = "8192"

COMPATIBLE_MACHINE = "k230-canmv"

IMAGE_LINGUAS = ""

