#!/bin/bash
# Verify key symbols in K230 kernel .config

set -e

REQUIRED_SYMBOLS=(
    "CONFIG_ARCH_CANAAN=y"
    "CONFIG_SERIAL_8250_DW=y"
    "CONFIG_SERIAL_8250_CONSOLE=y"
    "CONFIG_SERIAL_OF_PLATFORM=y"
    "CONFIG_BLK_DEV_INITRD=y"
)

if [ $# -lt 1 ]; then
    echo "Usage: $0 <.config path>"
    echo "  Example: $0 ~/yocto/build/tmp/work/k230_canmv-poky-linux/linux-k230/6.18.28/linux-6.18.28/.config"
    exit 1
fi

KCONFIG="$1"

if [ ! -f "$KCONFIG" ]; then
    echo "ERROR: .config not found at $KCONFIG"
    exit 1
fi

missing=0
for sym in "${REQUIRED_SYMBOLS[@]}"; do
    if grep -q "^${sym}$" "$KCONFIG"; then
        echo "OK: $sym"
    else
        echo "MISSING: $sym"
        missing=$((missing + 1))
    fi
done

echo "---"
if [ $missing -eq 0 ]; then
    echo "All ${#REQUIRED_SYMBOLS[@]} required symbols present."
    exit 0
else
    echo "ERROR: $missing required symbol(s) missing."
    exit 1
fi
