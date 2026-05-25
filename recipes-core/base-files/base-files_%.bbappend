# SPDX-License-Identifier: MIT
#
# kunOS embedded customizations: fstab with tmpfs mounts and noatime, sysctl
# tuning, shell profile, issue, and motd.

FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SRC_URI += " \
    file://fstab \
    file://profile \
    file://issue \
    file://motd \
"

do_install:append() {
    install -m 0644 ${UNPACKDIR}/fstab       ${D}${sysconfdir}/fstab
    install -m 0644 ${UNPACKDIR}/profile      ${D}${sysconfdir}/profile
    install -m 0644 ${UNPACKDIR}/issue        ${D}${sysconfdir}/issue
    install -m 0644 ${UNPACKDIR}/motd         ${D}${sysconfdir}/motd
}
