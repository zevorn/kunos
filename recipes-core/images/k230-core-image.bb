# SPDX-License-Identifier: MIT

SUMMARY = "K230 RISC-V Linux image with common command-line tools"
LICENSE = "MIT"

inherit core-image

IMAGE_FEATURES += "allow-empty-password empty-root-password allow-root-login package-management"

IMAGE_INSTALL = " \
    packagegroup-k230-common \
"

IMAGE_ROOTFS_SIZE ?= "262144"
IMAGE_ROOTFS_EXTRA_SPACE ?= "65536"

ROOTFS_POSTPROCESS_COMMAND += "k230_serial_autologin_root; k230_network_interfaces_cleanup; "

k230_serial_autologin_root() {
    inittab="${IMAGE_ROOTFS}${sysconfdir}/inittab"
    if [ -e "$inittab" ] && ! grep -q "ttyS0::respawn:.*--autologin root" "$inittab"; then
        sed -i '\#^ttyS0::respawn:.*/usr/sbin/getty #s#/usr/sbin/getty #/usr/sbin/getty --autologin root #' "$inittab"
    fi
}

k230_network_interfaces_cleanup() {
    interfaces="${IMAGE_ROOTFS}${sysconfdir}/network/interfaces"
    if [ -e "$interfaces" ]; then
        sed -i "/^# Busybox ifupdown won't process \\/en\\* correctly$/,/^iface eth inet dhcp$/d" "$interfaces"
    fi
}
