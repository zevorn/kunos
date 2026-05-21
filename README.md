# meta-k230

Yocto BSP layer and helper scripts for building a small RISC-V Linux
distribution for the Canaan K230 CanMV board model supported by the K230 QEMU
branch.

## Repositories and Branches

- meta-k230: `git@github.com:zevorn/meta-k230.git`
- QEMU: `git@github.com:zevorn/qemu.git`, branch `chao-k230-dev`
- Yocto/OpenEmbedded: tested with `poky-wrynose` from `bitbake-setup`
- Linux kernel: `linux-6.18.28` from kernel.org

The layer metadata also declares `scarthgap` compatibility, but the validated
local build uses Wrynose.

## Build QEMU

```bash
git clone git@github.com:zevorn/qemu.git ~/qemu
cd ~/qemu
git checkout chao-k230-dev
./configure --target-list=riscv64-softmmu,riscv32-softmmu
ninja -C build
```

The expected binary is:

```text
~/qemu/build/qemu-system-riscv64
```

It must support:

```bash
~/qemu/build/qemu-system-riscv64 -machine help | grep k230
```

## Build Yocto Image

From this repository:

```bash
./scripts/yocto-build-image
./scripts/yocto-init
./scripts/yocto-k230-setup
./scripts/yocto-bitbake k230-core-image
./scripts/yocto-export-deploy
```

The exported artifacts are written to:

```text
build-artifacts/k230-canmv/
```

The image includes BusyBox plus common shell, file, process, network, storage,
debugging, and package-management tools, including `bash`, GNU core tools,
`find`, `grep`, `sed`, `awk`, `tar`, `xz`, `iproute2`, `net-tools`, Dropbear,
`curl`, `wget`, Vim, `rsync`, `socat`, `lsof`, `sudo`, `parted`, `opkg`,
`file`, `which`, `ethtool`, `strace`, `usbutils`, `pciutils`, `e2fsprogs`, and
`dosfstools`.

## SDK U-Boot Boot Image

SDK U-Boot does not boot a normal Yocto WIC layout through its default
`bootcmd`. It runs `k230_boot`, which expects a GPT SD image with a K230-headed
`linux_system.bin` in the `linux` partition at 30MiB.

This repository includes the SDK U-Boot binary used for QEMU:

```text
prebuilt/k230-sdk/riscv-nomtee/u-boot
```

Generate the SDK-compatible SD image after building Yocto:

```bash
./scripts/k230-sdk-image --deploy build-artifacts/k230-canmv
```

When available, the packer builds the K230-tuned SDK OpenSBI payload from:

```text
~/k230-project/sdk/k230_sdk/src/common/opensbi
```

The generated image is:

```text
build-artifacts/k230-canmv/k230-core-image-k230-canmv.sdk-sdcard.img
```

## Run

SDK U-Boot path:

```bash
./scripts/k230-qemu-run --deploy build-artifacts/k230-canmv --sd --uboot
```

Direct SD/WIC path:

```bash
./scripts/k230-qemu-run --deploy build-artifacts/k230-canmv --sd
```

Direct initramfs path:

```bash
./scripts/k230-qemu-run --deploy build-artifacts/k230-canmv --initrd
```

SSH:

```bash
ssh -p 10022 root@127.0.0.1
```

The development image permits root login with an empty password.

## Verified Boot Results

The current build was verified with:

- SDK U-Boot -> SDK OpenSBI v0.9 -> Yocto Linux 6.18.28
- direct QEMU/OpenSBI SD boot
- direct QEMU/OpenSBI initramfs boot
- `eth0` via QEMU user networking and `usb-rtl8152`
- SSH forwarding on host port `10022`
- SDK rootfs mounted from `/dev/mmcblk1p3`
- direct WIC rootfs mounted from `/dev/mmcblk1p2`, with `/boot` on `/dev/mmcblk1p1`

## Agent Skills

Repository-local agent skills live under `.agents/skills/`. They cover the
K230 Yocto build, QEMU dependency build, QEMU boot modes, smoke tests, Docker
workflow, and configuration explanation.

## Notes

- Build outputs under `build-artifacts/` are ignored and should not be
  committed.
- The bundled U-Boot binary is not covered by `COPYING.MIT`; see
  `prebuilt/k230-sdk/riscv-nomtee/README.md`.
- If BitBake reports `linux-k230:do_unpack is tainted from a forced run`, it
  means the task was manually forced previously. It is not a boot failure. Use
  `./scripts/yocto-bitbake -c clean linux-k230` followed by a rebuild if a clean
  log is required.
