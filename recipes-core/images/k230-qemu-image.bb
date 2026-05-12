SUMMARY = "Small QEMU smoke-test image for meta-k230"
LICENSE = "MIT"

inherit core-image

IMAGE_FEATURES = ""
IMAGE_INSTALL = "busybox init-script"
IMAGE_LINGUAS = ""
IMAGE_ROOTFS_SIZE = "8192"
IMAGE_FSTYPES += "ext4"

COMPATIBLE_MACHINE = "(qemuriscv64)"
