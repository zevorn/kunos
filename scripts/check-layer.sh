#!/bin/sh
# SPDX-License-Identifier: MIT

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)

fail()
{
    echo "ERROR: $*" >&2
    exit 1
}

require_file()
{
    [ -f "$REPO_DIR/$1" ] || fail "missing $1"
}

require_executable()
{
    [ -x "$REPO_DIR/$1" ] || fail "$1 is not executable"
}

require_grep()
{
    pattern=$1
    file=$2
    grep -Eq "$pattern" "$REPO_DIR/$file" || fail "$file does not match: $pattern"
}

require_file COPYING.MIT
require_file README.md
require_file CONTRIBUTING.md
require_file SECURITY.md
require_file MAINTAINERS
require_file conf/layer.conf
require_file conf/machine/k230-canmv.conf
require_file recipes-kernel/linux/linux-k230_6.18.bb
require_file recipes-kernel/linux/files/k230-canmv.dts
require_file recipes-kernel/linux/files/k230-canmv.cfg
require_file recipes-core/images/k230-initramfs-image.bb
require_file recipes-core/images/k230-qemu-image.bb
require_file recipes-k230/init-script/init-script.bb
require_file scripts/boot-qemu-k230.sh
require_executable scripts/boot-qemu-k230.sh

require_grep 'LAYERSERIES_COMPAT_k230.*scarthgap' conf/layer.conf
require_grep 'LAYERDEPENDS_k230.*riscv-layer' conf/layer.conf
require_grep 'PREFERRED_PROVIDER_virtual/kernel.*linux-k230' conf/machine/k230-canmv.conf
require_grep 'COMPATIBLE_MACHINE.*k230-canmv' recipes-kernel/linux/linux-k230_6.18.bb
require_grep 'COMPATIBLE_MACHINE.*k230-canmv' recipes-core/images/k230-initramfs-image.bb
require_grep 'COMPATIBLE_MACHINE.*qemuriscv64' recipes-core/images/k230-qemu-image.bb
require_grep 'SPDX-License-Identifier: GPL-2.0-only' recipes-kernel/linux/files/k230-canmv.dts

if command -v dtc >/dev/null 2>&1; then
    dtc -I dts -O dtb \
        -o /tmp/meta-k230-check-layer.dtb \
        "$REPO_DIR/recipes-kernel/linux/files/k230-canmv.dts" >/dev/null
    rm -f /tmp/meta-k230-check-layer.dtb
fi

if command -v bitbake-layers >/dev/null 2>&1; then
    bitbake-layers show-layers | grep -Eq '(^|[[:space:]])k230([[:space:]]|$)' \
        || fail "bitbake environment does not include meta-k230"
fi

echo "meta-k230 layer checks passed"
