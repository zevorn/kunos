SUMMARY = "Mainline Linux kernel for Canaan K230 CanMV"
LICENSE = "GPL-2.0-only"
LIC_FILES_CHKSUM = "file://COPYING;md5=6bc538ed5bd9a7fc9398086aedcd7e46"

LINUX_VERSION = "6.18.28"
PV = "6.18.28"

SRC_URI = "https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-${PV}.tar.xz \
           file://k230-canmv.cfg \
           file://k230-canmv.dts \
          "
SRC_URI[sha256sum] = "f360789483586cf8a20b4ab2bffe76ead6b62c0db1eeb0d917294456c4d77b74"

inherit kernel

S = "${WORKDIR}/linux-${PV}"

KBUILD_DEFCONFIG:k230-canmv = "defconfig"

COMPATIBLE_MACHINE = "k230-canmv"

do_configure:append() {
    install -m 0644 ${WORKDIR}/k230-canmv.dts ${S}/arch/riscv/boot/dts/canaan/
    grep -qxF 'dtb-$$(CONFIG_ARCH_CANAAN) += k230-canmv.dtb' ${S}/arch/riscv/boot/dts/canaan/Makefile || \
        echo 'dtb-$$(CONFIG_ARCH_CANAAN) += k230-canmv.dtb' >> ${S}/arch/riscv/boot/dts/canaan/Makefile
}
