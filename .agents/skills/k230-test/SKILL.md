---
name: k230-test
description: Use when validating meta-k230 scripts, BitBake metadata, generated artifacts, QEMU boot, SSH access, or runtime tools.
license: MIT
---

# K230 Test

Test the narrowest thing first, then boot.

## Static Checks

| Scope | Command |
|-------|---------|
| Shell syntax | `bash -n scripts/*` |
| DTS syntax | `dtc -I dts -O dtb -o /tmp/k230-canmv.dtb recipes-kernel/linux/files/k230-canmv.dts` |
| BitBake image | `./scripts/yocto-bitbake k230-core-image` |
| Deploy export | `./scripts/yocto-export-deploy` |

## Runtime Smoke

After boot and SSH:

```bash
cat /etc/os-release
uname -a
mount
ip addr
ping -c 3 10.0.2.2
command -v bash vim rsync opkg file ethtool strace
```

## Rules

- Validate SDK U-Boot and direct WIC separately when boot paths changed.
- Record the exact root device when reporting boot results.
- Stop QEMU after tests; leave no stale guest process behind.
