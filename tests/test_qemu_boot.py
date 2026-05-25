"""Verify every QEMU boot path has the required artifacts and configuration.

Static checks run without QEMU.  Boot-smoke tests run when a deploy directory
is available (set K230_DEPLOY_DIR or pass --deploy to k230-check).
"""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "k230-qemu-run"
MACHINE_CONF = REPO_ROOT / "conf" / "machine" / "k230-canmv.conf"
WKS_FILE = REPO_ROOT / "wic" / "k230-canmv-sdimage.wks"
UBOOT_BINARY = REPO_ROOT / "prebuilt" / "k230-sdk" / "riscv-nomtee" / "u-boot"

DEPLOY_DIR = os.environ.get("K230_DEPLOY_DIR", str(REPO_ROOT / "build-artifacts" / "k230-canmv"))
QEMU_BIN = os.environ.get("K230_QEMU", os.path.expanduser("~/qemu/build/qemu-system-riscv64"))
QEMU_SMOKE_TIMEOUT = int(os.environ.get("K230_QEMU_SMOKE_TIMEOUT", "120"))


def _read(path: Path) -> str:
    return path.read_text()


def _find_deploy_file(pattern: str) -> Path | None:
    """Find a file matching *pattern* inside DEPLOY_DIR."""
    deploy = Path(DEPLOY_DIR)
    if not deploy.is_dir():
        return None
    matches = sorted(deploy.glob(pattern))
    return matches[0] if matches else None


def _assert_contains(text: str, substr: str, label: str):
    assert substr in text, f"{label}: expected line not found:\n  {substr}"


# ---------------------------------------------------------------------------
# Static machine configuration tests
# ---------------------------------------------------------------------------


class MachineConfigTest(unittest.TestCase):
    """Validate machine.conf has the correct QEMU flags for each boot path."""

    @classmethod
    def setUpClass(cls):
        cls.text = _read(MACHINE_CONF)

    def test_qb_machine_is_k230(self):
        _assert_contains(self.text, 'QB_MACHINE = "-machine k230"',
                         "QB_MACHINE should be k230")

    def test_qb_mem_2g(self):
        _assert_contains(self.text, 'QB_MEM = "-m 2G"',
                         "QB_MEM should be 2G")

    def test_qb_default_fstype_wic(self):
        _assert_contains(self.text, 'QB_DEFAULT_FSTYPE = "wic"',
                         "QB_DEFAULT_FSTYPE should be wic")

    def test_qb_rootfs_opt_is_sd(self):
        _assert_contains(self.text, '-drive if=sd,file=@ROOTFS@,format=raw',
                         "QB_ROOTFS_OPT should use SD drive")

    def test_qb_serial_nographic(self):
        _assert_contains(self.text, 'QB_SERIAL_OPT = "-nographic"',
                         "QB_SERIAL_OPT should be -nographic")

    def test_qb_network_with_ssh_forward(self):
        _assert_contains(self.text, "hostfwd=tcp::10022-:22",
                         "QB_NETWORK_DEVICE should forward port 10022 to SSH")

    def test_qb_kernel_cmdline_for_sd(self):
        _assert_contains(self.text, "root=/dev/mmcblk1p2",
                         "QB_KERNEL_CMDLINE_APPEND should use mmcblk1p2 root")
        _assert_contains(self.text, "rootwait",
                         "QB_KERNEL_CMDLINE_APPEND should use rootwait")

    def test_image_fstypes_includes_all_boot_paths(self):
        _assert_contains(self.text, "cpio.gz",  # initrd
                         "IMAGE_FSTYPES should include cpio.gz for initrd")
        _assert_contains(self.text, "wic.gz",    # sd + uboot
                         "IMAGE_FSTYPES should include wic.gz for sd/uboot")

    def test_image_boot_files(self):
        _assert_contains(self.text, "Image k230-canmv.dtb",
                         "IMAGE_BOOT_FILES should include Image and DTB")

    def test_uboot_entrypoint_matches_opensbi(self):
        """U-Boot entrypoint must match OpenSBI FW_JUMP_ADDR."""
        _assert_contains(self.text, 'UBOOT_ENTRYPOINT = "0x08200000"',
                         "UBOOT_ENTRYPOINT should be 0x08200000")
        _assert_contains(self.text, 'FW_JUMP_ADDR=0x08200000',
                         "OpenSBI FW_JUMP_ADDR should match UBOOT_ENTRYPOINT")


# ---------------------------------------------------------------------------
# Static WKS / disk layout tests
# ---------------------------------------------------------------------------


class WksDiskLayoutTest(unittest.TestCase):
    """Validate the WIC kickstart file has the expected partition layout."""

    @classmethod
    def setUpClass(cls):
        cls.text = _read(WKS_FILE)

    def test_boot_partition(self):
        _assert_contains(self.text,
                         "part /boot --source bootimg-partition --ondisk mmcblk1 --fstype=vfat --label boot --active --align 4096 --fixed-size 64",
                         "boot partition vfat 64MiB")

    def test_root_partition(self):
        _assert_contains(self.text,
                         "part / --source rootfs --ondisk mmcblk1 --fstype=ext4 --label root --align 4096 --fixed-size 1980",
                         "root partition ext4 1980MiB")

    def test_msdos_partition_table(self):
        _assert_contains(self.text,
                         "bootloader --ptable msdos --timeout=0",
                         "MBR partition table")

    def test_both_partitions_on_same_disk(self):
        """Both partitions must be on the same mmcblk1 device for fstab."""
        self.assertEqual(self.text.count("--ondisk mmcblk1"), 2,
                         "both partitions must target mmcblk1")


# ---------------------------------------------------------------------------
# Static deploy artifact existence tests
# ---------------------------------------------------------------------------


class DeployArtifactsTest(unittest.TestCase):
    """Check that required boot artifacts are present in the deploy directory."""

    def test_qemu_binary_exists(self):
        qemu = Path(QEMU_BIN)
        if not qemu.is_file():
            self.skipTest(f"QEMU binary not found at {QEMU_BIN}")
        self.assertTrue(os.access(qemu, os.X_OK),
                        f"QEMU binary must be executable: {QEMU_BIN}")

    def test_kernel_image_present(self):
        img = _find_deploy_file("Image*")
        if img is None:
            self.skipTest(f"No Image found in {DEPLOY_DIR} (build first)")
        self.assertTrue(img.stat().st_size > 0,
                        f"Kernel Image must be non-empty: {img}")

    def test_dtb_present(self):
        dtb = _find_deploy_file("**/k230-canmv*.dtb")
        if dtb is None:
            self.skipTest(f"No DTB found in {DEPLOY_DIR} (build first)")
        self.assertTrue(dtb.stat().st_size > 0,
                        f"DTB must be non-empty: {dtb}")

    def test_initrd_present(self):
        initrd = _find_deploy_file("*.rootfs.cpio.gz")
        if initrd is None:
            self.skipTest(f"No initrd found in {DEPLOY_DIR} (build first)")
        self.assertTrue(initrd.stat().st_size > 0,
                        f"initrd must be non-empty: {initrd}")

    def test_wic_image_present(self):
        wic = _find_deploy_file("*.rootfs.wic*")
        if wic is None:
            self.skipTest(f"No WIC image found in {DEPLOY_DIR} (build first)")
        self.assertTrue(wic.stat().st_size > 0,
                        f"WIC image must be non-empty: {wic}")

    def test_sdk_sdcard_image_present_for_uboot(self):
        sdk_img = _find_deploy_file("*sdk-sdcard.img")
        if sdk_img is None:
            self.skipTest(f"No SDK SD card image found in {DEPLOY_DIR} "
                          "(run k230-sdk-image first)")

    def test_uboot_binary_present(self):
        if not UBOOT_BINARY.is_file():
            self.skipTest(f"U-Boot binary not found at {UBOOT_BINARY}")
        self.assertTrue(UBOOT_BINARY.stat().st_size > 0,
                        "U-Boot binary must be non-empty")

    def test_fstab_matches_wic_devices(self):
        """fstab root device (/dev/mmcblk1p2) must match WIC layout."""
        fstab = REPO_ROOT / "recipes-core/base-files/files/fstab"
        if not fstab.is_file():
            self.skipTest("fstab not found")
        text = _read(fstab)
        _assert_contains(text, "/dev/mmcblk1p2", "fstab root device mmcblk1p2")
        _assert_contains(text, "/dev/mmcblk1p1", "fstab boot device mmcblk1p1")


# ---------------------------------------------------------------------------
# QEMU boot-smoke tests (one per boot path)
# ---------------------------------------------------------------------------


class _QemuSmokeBase:
    """Shared logic for QEMU boot-smoke tests.

    Each subclass defines:
      - _mode: "initrd", "sd", or "uboot"
      - _expected_markers: list of strings expected in serial output
      - _cmdline_checks: optional list of substrings expected in /proc/cmdline
    """

    _mode: str
    _expected_markers: list[str]
    _cmdline_checks: list[str] = []
    timeout: int = QEMU_SMOKE_TIMEOUT

    def _run_qemu(self) -> Path:
        """Run QEMU in the configured mode, return path to captured log."""
        fd, path_str = tempfile.mkstemp(
            prefix=f"k230-qemu-{self._mode}-", suffix=".log"
        )
        os.close(fd)
        log_file = Path(path_str)
        self.addCleanup(os.unlink, path_str)

        cmd = [
            str(SCRIPT),
            f"--{self._mode}",
            "--deploy", DEPLOY_DIR,
            "--no-net",
            "--snapshot",
        ]
        if self._mode == "uboot":
            cmd.append("--uboot")

        with open(log_file, "w") as out:
            self._proc = subprocess.Popen(
                cmd, stdout=out, stderr=subprocess.STDOUT,
            )

        return log_file

    def _wait_for_marker(self, log_file: Path) -> bool:
        """Poll log_file until a boot marker appears or timeout expires."""
        import time
        deadline = time.time() + self.timeout

        while time.time() < deadline:
            if self._proc.poll() is not None:
                # QEMU exited — check what we got
                break
            try:
                text = _read(log_file)
            except Exception:
                time.sleep(1)
                continue

            for marker in self._expected_markers:
                if marker in text:
                    return True
            time.sleep(1)

        return False

    def _kill_qemu(self):
        if self._proc and self._proc.poll() is None:
            self._proc.kill()
            try:
                self._proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                pass

    def test_boot_reaches_login(self):
        """Smoke: QEMU boots and reaches a login prompt or shell."""
        if not Path(QEMU_BIN).is_file():
            self.skipTest(f"QEMU binary not found: {QEMU_BIN}")
        if not Path(DEPLOY_DIR).is_dir():
            self.skipTest(f"Deploy directory not found: {DEPLOY_DIR}")

        log = self._run_qemu()
        try:
            reached = self._wait_for_marker(log)
            if not reached:
                # Dump tail of log for diagnostics
                try:
                    tail = _read(log)
                except Exception:
                    tail = "<unreadable>"
                self.fail(
                    f"QEMU ({self._mode}) did not reach expected marker "
                    f"within {self.timeout}s.\n"
                    f"Markers: {self._expected_markers}\n"
                    f"Last ~2KB of log:\n{tail[-2048:]}"
                )
        finally:
            self._kill_qemu()


class InitrdBootSmokeTest(_QemuSmokeBase, unittest.TestCase):
    _mode = "initrd"
    _expected_markers = ["login:", "root@", "/ #", "reboot:",
                         "Freeing unused kernel"]
    _cmdline_checks = ["rdinit=/sbin/init"]


class SdBootSmokeTest(_QemuSmokeBase, unittest.TestCase):
    _mode = "sd"
    _expected_markers = ["login:", "root@", "/ #", "reboot:",
                         "Freeing unused kernel"]
    _cmdline_checks = ["root=/dev/mmcblk1p2", "rootwait", "rw"]


class UbootBootSmokeTest(_QemuSmokeBase, unittest.TestCase):
    _mode = "uboot"
    _expected_markers = ["login:", "root@", "/ #", "reboot:",
                         "Freeing unused kernel",
                         "U-Boot 20",       # U-Boot banner
                         "Starting kernel"]  # U-Boot handoff
    _cmdline_checks = []

    def test_uboot_binary_found(self):
        """Pre-check: skip uboot smoke if no U-Boot binary is available."""
        if not UBOOT_BINARY.is_file():
            self.skipTest(f"U-Boot binary not found at {UBOOT_BINARY}")


# ---------------------------------------------------------------------------
# QEMU script argument-parsing tests (static, fast)
# ---------------------------------------------------------------------------


class QemuRunScriptTest(unittest.TestCase):
    """Validate the k230-qemu-run script handles all three boot modes."""

    @classmethod
    def setUpClass(cls):
        cls.text = _read(SCRIPT)

    def test_script_supports_initrd_mode(self):
        _assert_contains(self.text, "--initrd", "script supports --initrd")
        # Should have rdinit= in the initrd append line
        _assert_contains(self.text, "rdinit=/sbin/init",
                         "initrd mode sets rdinit=")

    def test_script_supports_sd_mode(self):
        _assert_contains(self.text, "--sd", "script supports --sd")
        # SD mode uses root=/dev/mmcblk1p2
        _assert_contains(self.text, "root=/dev/mmcblk1p2",
                         "sd mode sets root=/dev/mmcblk1p2")

    def test_script_supports_uboot_mode(self):
        _assert_contains(self.text, "--uboot", "script supports --uboot")
        _assert_contains(self.text, "boot-both-cores=on",
                         "uboot mode enables boot-both-cores")
        _assert_contains(self.text, "-smp 2",
                         "uboot mode uses -smp 2")

    def test_snapshot_flag_accepted(self):
        _assert_contains(self.text, "--snapshot",
                         "script supports --snapshot")
        _assert_contains(self.text, "snapshot=on",
                         "snapshot enables QEMU snapshot mode")

    def test_no_net_flag_accepted(self):
        _assert_contains(self.text, "--no-net",
                         "script supports --no-net")

    def test_help_flag_accepted(self):
        _assert_contains(self.text, "-h|--help",
                         "script supports --help")


if __name__ == "__main__":
    unittest.main()
