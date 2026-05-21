# SPDX-License-Identifier: MIT

SUMMARY = "Common command-line tools for K230 Linux images"
LICENSE = "MIT"

inherit packagegroup

RDEPENDS:${PN} = " \
    packagegroup-core-boot \
    os-release \
    fastfetch \
    busybox \
    bash \
    coreutils \
    file \
    findutils \
    grep \
    sed \
    gawk \
    diffutils \
    which \
    tar \
    gzip \
    bzip2 \
    xz \
    util-linux \
    procps \
    psmisc \
    kmod \
    iproute2 \
    iputils \
    net-tools \
    dhcpcd \
    dropbear \
    ethtool \
    rsync \
    socat \
    curl \
    wget \
    less \
    vim \
    strace \
    lsof \
    sudo \
    usbutils \
    pciutils \
    e2fsprogs \
    dosfstools \
    parted \
    mtd-utils \
    opkg \
"
