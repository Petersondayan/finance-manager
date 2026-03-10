"""Build script for Finance Manager — produces a single-file Windows executable.

Usage:
    python build.py            # full build
    python build.py --clean    # remove dist/ and build/ first, then build
    python build.py --no-upx   # skip UPX compression
"""

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent
DIST_DIR = ROOT / "dist"
BUILD_DIR = ROOT / "build"
SPEC_FILE = ROOT / "main.spec"
EXE_NAME = "FinanceManager.exe"


def clean():
    """Remove previous build artefacts."""
    for directory in (DIST_DIR, BUILD_DIR):
        if directory.exists():
            print(f"  Removing {directory} …")
            shutil.rmtree(directory)
    print("  Clean done.\n")


def run_pyinstaller(no_upx: bool = False) -> bool:
    """Invoke PyInstaller with main.spec."""
    cmd = [sys.executable, "-m", "PyInstaller", str(SPEC_FILE), "--noconfirm"]
    if no_upx:
        cmd.append("--noupx")

    print(f"  Running: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=str(ROOT))
    return result.returncode == 0


def verify_output() -> bool:
    """Check that the expected executable was produced."""
    exe = DIST_DIR / EXE_NAME
    if exe.exists():
        size_mb = exe.stat().st_size / (1024 * 1024)
        print(f"\n  Built: {exe}")
        print(f"  Size : {size_mb:.1f} MB")
        return True
    print(f"\n  ERROR: Expected output not found: {exe}")
    return False


def main():
    parser = argparse.ArgumentParser(description="Build Finance Manager executable")
    parser.add_argument("--clean", action="store_true", help="Remove build artefacts before building")
    parser.add_argument("--no-upx", action="store_true", help="Disable UPX compression")
    args = parser.parse_args()

    print("=" * 60)
    print("  Finance Manager — Build Script")
    print("=" * 60)

    if args.clean:
        print("\n[1/3] Cleaning previous build …")
        clean()
    else:
        print("\n[1/3] Skipping clean (use --clean to remove old artefacts)\n")

    print("[2/3] Running PyInstaller …\n")
    start = time.time()
    ok = run_pyinstaller(no_upx=args.no_upx)
    elapsed = time.time() - start

    if not ok:
        print("\n  PyInstaller failed. Check output above.")
        sys.exit(1)

    print(f"\n[3/3] Verifying output … (build took {elapsed:.0f}s)")
    if not verify_output():
        sys.exit(1)

    print("\n" + "=" * 60)
    print("  BUILD SUCCESSFUL")
    print(f"  Executable: dist/{EXE_NAME}")
    print("  Next step : run installer.iss with Inno Setup to create")
    print("              the Windows installer (dist/FinanceManagerSetup.exe)")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
