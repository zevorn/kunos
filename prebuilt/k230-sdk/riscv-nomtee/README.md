# K230 SDK U-Boot Binary

`u-boot` is the K230 SDK U-Boot binary used by `scripts/k230-qemu-run --sd --uboot`.

It is included so the QEMU boot path is reproducible from this repository
without depending on `~/k230-project/images/riscv-nomtee/u-boot`. The binary is
not covered by this layer's `COPYING.MIT`; keep its provenance tied to the K230
SDK source and license terms.

The SDK-compatible Yocto SD image still requires a K230-tuned OpenSBI payload.
When available, `scripts/k230-sdk-image` builds that payload from:

```text
~/k230-project/sdk/k230_sdk/src/common/opensbi
```
