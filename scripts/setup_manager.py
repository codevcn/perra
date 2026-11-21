#!/usr/bin/env python3
"""Setup Manager for Perra (Persona Radar).

Manages environment checks, virtual environment creation, Python dependencies
(including optional [pdf], dev/test, and PyInstaller build packages), Inno Setup 6
provisioning on Windows, AI agent skill installation, and standalone packaging.

Uses only the Python standard library so it can run on a fresh Python 3.10+
installation before any third-party dependency is installed.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
VENV_DIR = REPO_ROOT / ".venv"
PYINSTALLER_SPEC = REPO_ROOT / "pyinstaller" / "perra_standalone.spec"
PYINSTALLER_REQS = REPO_ROOT / "pyinstaller" / "requirements.txt"
INNO_SCRIPT = REPO_ROOT / "installer" / "perra.iss"
SKILL_SOURCE = REPO_ROOT / "skills" / "perra"
VERSION_FILE = REPO_ROOT / "perra" / "__version__.py"

DEV_PACKAGES = [
    "pytest>=8.3.4,<10.0.0",
    "pytest-asyncio>=1.0.0",
    "pytest-cov>=6,<8",
    "pytest-httpserver>=1.0.0",
    "pytest-rerunfailures>=15.1,<17.0",
    "flake8>=7.1.1",
    "mypy>=1.14.1,<3.0.0",
    "black>=25.1,<27.0",
    "pyyaml>=6.0",
]


def _venv_python(venv_dir: Path = VENV_DIR) -> Path:
    if platform.system() == "Windows":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _active_python() -> Path:
    vp = _venv_python()
    return vp if vp.is_file() else Path(sys.executable)


def _read_version() -> str:
    if VERSION_FILE.is_file():
        for line in VERSION_FILE.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("__version__"):
                _, _, rhs = line.partition("=")
                return rhs.strip().strip("'\"")
    return "0.1.0"


def _run(
    cmd: List[str],
    cwd: Optional[Path] = None,
    check: bool = True,
    capture: bool = False,
) -> subprocess.CompletedProcess:
    print(f"[setup] Running: {' '.join(cmd)}")
    return subprocess.run(
        cmd,
        cwd=str(cwd or REPO_ROOT),
        check=check,
        text=True,
        capture_output=capture,
    )


def find_iscc() -> Optional[Path]:
    """Locate Inno Setup compiler (ISCC.exe) on Windows."""
    from_path = shutil.which("ISCC.exe") or shutil.which("iscc")
    if from_path:
        return Path(from_path)

    candidates = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Inno Setup 6" / "ISCC.exe",
        Path(os.environ.get("ProgramFiles(x86)", "")) / "Inno Setup 6" / "ISCC.exe",
        Path(os.environ.get("ProgramFiles", "")) / "Inno Setup 6" / "ISCC.exe",
        Path("D:/Programs/Inno Setup 6/ISCC.exe"),
        Path("D:/Programs-ver-Later/Inno Setup 6/ISCC.exe"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate

    if platform.system() == "Windows":
        try:
            import winreg

            roots = [
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Inno Setup 6_is1"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Inno Setup 6_is1"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Inno Setup 6_is1"),
            ]
            for hive, subkey in roots:
                try:
                    with winreg.OpenKey(hive, subkey) as key:
                        loc, _ = winreg.QueryValueEx(key, "InstallLocation")
                        exe = Path(loc) / "ISCC.exe"
                        if exe.is_file():
                            return exe
                except OSError:
                    continue
        except ImportError:
            pass
    return None


def agent_skill_targets() -> Dict[str, Path]:
    home = Path.home()
    return {
        "antigravity": home / ".gemini" / "config" / "skills" / "perra",
        "codex": home / ".codex" / "skills" / "perra",
        "claude": home / ".claude" / "skills" / "perra",
    }


def _check_python_module(python_exe: Path, module_name: str) -> bool:
    res = subprocess.run(
        [str(python_exe), "-c", f"import {module_name}"],
        capture_output=True,
        text=True,
    )
    return res.returncode == 0


def cmd_doctor(_args: argparse.Namespace) -> int:
    print(f"=== Perra Setup Doctor (v{_read_version()}) ===")
    print(f"Repo root      : {REPO_ROOT}")
    print(f"Host Python    : {sys.version.split()[0]} ({sys.executable})")

    if sys.version_info < (3, 10):
        print("[FAIL] Python 3.10+ is required.")
        return 1

    venv_py = _venv_python()
    print(f".venv          : {'OK (' + str(venv_py) + ')' if venv_py.is_file() else 'MISSING'}")
    py = _active_python()

    checks: List[Tuple[str, bool]] = [
        ("perra package", _check_python_module(py, "perra")),
        ("aiohttp", _check_python_module(py, "aiohttp")),
        ("curl_cffi", _check_python_module(py, "curl_cffi")),
        ("socid_extractor", _check_python_module(py, "socid_extractor")),
        ("flask", _check_python_module(py, "flask")),
        ("xhtml2pdf [pdf]", _check_python_module(py, "xhtml2pdf")),
        ("pytest", _check_python_module(py, "pytest")),
        ("PyInstaller", _check_python_module(py, "PyInstaller")),
    ]
    for label, ok in checks:
        print(f"  - {label:<18}: {'OK' if ok else 'MISSING'}")

    iscc = find_iscc()
    print(f"Inno Setup 6   : {'OK (' + str(iscc) + ')' if iscc else 'MISSING (install JRSoftware.InnoSetup)'}")
    print(f"git            : {shutil.which('git') or 'MISSING'}")
    print(f"gh             : {shutil.which('gh') or 'MISSING'}")

    print("AI Agent Skills:")
    for agent, dst in agent_skill_targets().items():
        skill_md = dst / "SKILL.md"
        parent_exists = dst.parent.parent.exists()
        status = "INSTALLED" if skill_md.is_file() else ("DIR READY" if parent_exists else "AGENT DIR NOT FOUND")
        print(f"  - {agent:<12}: {status} ({dst})")

    missing_core = [label for label, ok in checks[:5] if not ok]
    if missing_core:
        print("\n[!] Run: python scripts/setup_manager.py install")
        return 1
    return 0


def ensure_venv(recreate: bool = False) -> Path:
    if sys.version_info < (3, 10):
        raise RuntimeError(f"Python 3.10+ is required, found {sys.version.split()[0]}")

    venv_py = _venv_python()
    if recreate and VENV_DIR.exists():
        print(f"[setup] Removing existing venv at {VENV_DIR}")
        shutil.rmtree(VENV_DIR)

    if not venv_py.is_file():
        print(f"[setup] Creating virtual environment at {VENV_DIR}")
        _run([sys.executable, "-m", "venv", str(VENV_DIR)])

    _run([str(venv_py), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
    return venv_py


def install_inno_setup() -> Optional[Path]:
    existing = find_iscc()
    if existing:
        print(f"[setup] Inno Setup 6 already installed: {existing}")
        return existing
    if platform.system() != "Windows":
        print("[setup] Inno Setup installation is only supported on Windows.")
        return None
    winget = shutil.which("winget")
    if not winget:
        print("[setup] winget not found. Download Inno Setup 6 from https://jrsoftware.org/isdl.php")
        return None
    _run(
        [
            winget,
            "install",
            "-e",
            "--id",
            "JRSoftware.InnoSetup",
            "--silent",
            "--accept-package-agreements",
            "--accept-source-agreements",
        ],
        check=False,
    )
    return find_iscc()


def cmd_install(args: argparse.Namespace) -> int:
    venv_py = ensure_venv(recreate=args.recreate_venv)

    target = ".[pdf]" if not args.no_pdf else "."
    _run([str(venv_py), "-m", "pip", "install", "-e", target])

    if not args.no_dev:
        _run([str(venv_py), "-m", "pip", "install", *DEV_PACKAGES])

    if not args.no_pyinstaller:
        if PYINSTALLER_REQS.is_file():
            _run([str(venv_py), "-m", "pip", "install", "-r", str(PYINSTALLER_REQS)])
        else:
            _run([str(venv_py), "-m", "pip", "install", "pyinstaller"])

    if args.with_inno:
        iscc = install_inno_setup()
        if not iscc:
            print("[setup] Warning: ISCC.exe still not found after Inno Setup step.")

    print("[setup] Installation complete.")
    return 0


def cmd_install_skills(args: argparse.Namespace) -> int:
    if not SKILL_SOURCE.is_dir() or not (SKILL_SOURCE / "SKILL.md").is_file():
        print(f"[setup] Skill source missing: {SKILL_SOURCE}", file=sys.stderr)
        return 1

    targets = agent_skill_targets()
    if args.agents:
        selected = [a.strip().lower() for a in args.agents.split(",") if a.strip()]
    else:
        selected = list(targets.keys())

    for agent in selected:
        if agent not in targets:
            print(f"[setup] Unknown agent {agent!r}. Valid: {', '.join(targets)}", file=sys.stderr)
            return 2
        dst = targets[agent]
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(SKILL_SOURCE, dst, dirs_exist_ok=True)
        print(f"[setup] Installed 'perra' skill for {agent} -> {dst}")
    return 0


def cmd_build_onedir(args: argparse.Namespace) -> int:
    py = _venv_python() if _venv_python().is_file() else Path(sys.executable)
    if not PYINSTALLER_SPEC.is_file():
        print(f"[setup] PyInstaller spec not found: {PYINSTALLER_SPEC}", file=sys.stderr)
        return 1

    dist_dir = REPO_ROOT / "dist"
    work_dir = REPO_ROOT / "build"
    if args.clean:
        shutil.rmtree(dist_dir / "perra", ignore_errors=True)
        shutil.rmtree(work_dir, ignore_errors=True)

    _run(
        [
            str(py),
            "-m",
            "PyInstaller",
            "--clean",
            "--noconfirm",
            "--distpath",
            str(dist_dir),
            "--workpath",
            str(work_dir),
            str(PYINSTALLER_SPEC),
        ]
    )
    exe_path = dist_dir / "perra" / ("perra.exe" if platform.system() == "Windows" else "perra")
    if not exe_path.is_file():
        print(f"[setup] Expected binary not found: {exe_path}", file=sys.stderr)
        return 1
    print(f"[setup] PyInstaller --onedir build succeeded: {exe_path}")
    return 0


def _write_sha256sums(installer_dir: Path) -> Path:
    sums_path = installer_dir / "SHA256SUMS.txt"
    lines = []
    for file_path in sorted(installer_dir.iterdir()):
        if not file_path.is_file() or file_path.name == "SHA256SUMS.txt":
            continue
        digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {file_path.name}")
    sums_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[setup] Wrote checksums: {sums_path}")
    return sums_path


def cmd_build_installer(args: argparse.Namespace) -> int:
    iscc = find_iscc()
    if not iscc:
        print("[setup] ISCC.exe (Inno Setup 6) not found. Run with --with-inno or install JRSoftware.InnoSetup.", file=sys.stderr)
        return 1
    if not INNO_SCRIPT.is_file():
        print(f"[setup] Inno Setup script not found: {INNO_SCRIPT}", file=sys.stderr)
        return 1
    onedir_exe = REPO_ROOT / "dist" / "perra" / "perra.exe"
    if not onedir_exe.is_file():
        print(f"[setup] Missing --onedir build at {onedir_exe}. Run build-onedir first.", file=sys.stderr)
        return 1

    version = _read_version()
    out_dir = REPO_ROOT / "dist" / "installer"
    out_dir.mkdir(parents=True, exist_ok=True)
    _run(
        [
            str(iscc),
            f"/DMyAppVersion={version}",
            f"/DSourceOnedir={REPO_ROOT / 'dist' / 'perra'}",
            f"/DSkillSource={SKILL_SOURCE}",
            f"/O{out_dir}",
            str(INNO_SCRIPT),
        ]
    )
    _write_sha256sums(out_dir)
    return 0


def cmd_build_all(args: argparse.Namespace) -> int:
    rc = cmd_build_onedir(args)
    if rc != 0:
        return rc
    return cmd_build_installer(args)


def cmd_setup_all(args: argparse.Namespace) -> int:
    rc = cmd_install(args)
    if rc != 0:
        return rc
    rc = cmd_install_skills(args)
    if rc != 0:
        return rc
    return cmd_doctor(args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Setup Manager for Perra (Persona Radar)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_doc = sub.add_parser("doctor", help="Inspect Python, dependencies, Inno Setup, and AI skill paths.")
    p_doc.set_defaults(func=cmd_doctor)

    p_inst = sub.add_parser("install", help="Create .venv and install Perra + dependencies.")
    p_inst.add_argument("--no-pdf", action="store_true", help="Skip optional [pdf] dependencies.")
    p_inst.add_argument("--no-dev", action="store_true", help="Skip dev/test dependencies.")
    p_inst.add_argument("--no-pyinstaller", action="store_true", help="Skip PyInstaller build dependencies.")
    p_inst.add_argument("--with-inno", action="store_true", help="Install Inno Setup 6 via winget if missing.")
    p_inst.add_argument("--recreate-venv", action="store_true", help="Recreate .venv from scratch.")
    p_inst.set_defaults(func=cmd_install)

    p_skills = sub.add_parser("install-skills", help="Install the Perra skill for AI agents.")
    p_skills.add_argument("--agents", default="", help="Comma-separated agents: antigravity,codex,claude (default: all).")
    p_skills.set_defaults(func=cmd_install_skills)

    p_one = sub.add_parser("build-onedir", help="Build PyInstaller --onedir distribution into dist/perra.")
    p_one.add_argument("--clean", action="store_true", help="Remove prior dist/perra and build/ before building.")
    p_one.set_defaults(func=cmd_build_onedir)

    p_iss = sub.add_parser("build-installer", help="Compile Inno Setup installer into dist/installer.")
    p_iss.set_defaults(func=cmd_build_installer)

    p_all_build = sub.add_parser("build-all", help="Build --onedir bundle and Inno Setup installer.")
    p_all_build.add_argument("--clean", action="store_true", help="Clean prior build outputs first.")
    p_all_build.set_defaults(func=cmd_build_all)

    p_setup_all = sub.add_parser("setup-all", help="Run install + install-skills + doctor.")
    p_setup_all.add_argument("--no-pdf", action="store_true", help="Skip optional [pdf] dependencies.")
    p_setup_all.add_argument("--no-dev", action="store_true", help="Skip dev/test dependencies.")
    p_setup_all.add_argument("--no-pyinstaller", action="store_true", help="Skip PyInstaller build dependencies.")
    p_setup_all.add_argument("--with-inno", action="store_true", help="Install Inno Setup 6 via winget if missing.")
    p_setup_all.add_argument("--recreate-venv", action="store_true", help="Recreate .venv from scratch.")
    p_setup_all.add_argument("--agents", default="", help="Comma-separated agents for skill installation.")
    p_setup_all.set_defaults(func=cmd_setup_all)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
