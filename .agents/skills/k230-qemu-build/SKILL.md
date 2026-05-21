---
name: k230-qemu-build
description: Use when building, checking, or refreshing the K230-capable QEMU dependency used by meta-k230.
license: MIT
---

# K230 QEMU Build

Use the validated QEMU branch before debugging guest Linux.

## Commands

| Task | Command |
|------|---------|
| Clone | `git clone git@github.com:zevorn/qemu.git ~/qemu` |
| Branch | `git -C ~/qemu checkout chao-k230-dev` |
| Configure | `cd ~/qemu && ./configure --target-list=riscv64-softmmu,riscv32-softmmu` |
| Build | `ninja -C ~/qemu/build` |
| Check machine | `~/qemu/build/qemu-system-riscv64 -machine help | grep k230` |

## Rules

- Expected binary: `~/qemu/build/qemu-system-riscv64`.
- Expected branch: `chao-k230-dev`.
- Rebuild QEMU only when the binary is missing, stale, or lacks `-machine k230`.
