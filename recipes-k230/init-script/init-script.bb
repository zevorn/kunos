SUMMARY = "Minimal /init script for K230 initramfs"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "file://init"

S = "${WORKDIR}"

do_install() {
    install -d ${D}
    install -m 0755 ${S}/init ${D}/init
    install -d ${D}${base_sbindir}
    ln -s ../init ${D}${base_sbindir}/init
}

FILES:${PN} = "/init ${base_sbindir}/init"

COMPATIBLE_MACHINE = "k230-canmv"
COMPATIBLE_MACHINE:qemuriscv64 = "qemuriscv64"
