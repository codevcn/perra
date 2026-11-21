"""Self-update and non-blocking GitHub release check for Perra CLI."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import requests

from .__version__ import __version__
from .db_updater import PERRA_HOME, _proxies

DEFAULT_CLI_REPO = "codevcn/perra"
CLI_UPDATE_STATE_PATH = os.path.join(PERRA_HOME, "cli_update_state.json")
USER_AGENT = f"perra-cli/{__version__}"


def parse_semver(version_str: str) -> Tuple[Tuple[int, ...], int, str]:
    """Parse version string like 'v0.1.0' or '0.2.0-rc1' for comparison.

    Returns ``(numeric_tuple, stability_rank, prerelease_tag)`` where
    ``stability_rank`` is ``1`` for final releases and ``0`` for prereleases,
    so ``0.2.0 > 0.2.0-rc1 > 0.1.0``.
    """
    cleaned = (version_str or "").strip().lstrip("vV")
    if not cleaned:
        return ((0, 0, 0), 1, "")
    main_part, sep, pre_part = cleaned.partition("-")
    # Also handle PEP 440 style prerelease like 0.2.0a1 / 0.2.0rc1
    if not sep:
        m = re.match(r"^(\d+(?:\.\d+)*)([a-zA-Z].*)$", main_part)
        if m:
            main_part, pre_part = m.group(1), m.group(2)
    nums = []
    for piece in main_part.split("."):
        digits = re.match(r"^(\d+)", piece)
        if not digits:
            return ((0, 0, 0), 0, cleaned)
        nums.append(int(digits.group(1)))
    while len(nums) < 3:
        nums.append(0)
    stability = 0 if pre_part else 1
    return (tuple(nums), stability, pre_part.lower())


def is_newer_version(candidate: str, current: str) -> bool:
    """Return True if ``candidate`` is strictly newer than ``current``."""
    return parse_semver(candidate) > parse_semver(current)


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_cli_update_state(state_path: str = CLI_UPDATE_STATE_PATH) -> Dict[str, Any]:
    try:
        with open(state_path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def save_cli_update_state(
    state: Dict[str, Any], state_path: str = CLI_UPDATE_STATE_PATH
) -> None:
    parent = os.path.dirname(state_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    tmp_path = state_path + ".tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, state_path)
    except OSError:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def _request_headers(accept: str = "application/vnd.github+json") -> Dict[str, str]:
    return {
        "User-Agent": USER_AGENT,
        "Accept": accept,
    }


def _extract_assets_from_release(release_json: Dict[str, Any], repo: str, tag: str) -> Dict[str, Any]:
    version = tag.lstrip("vV")
    installer_name = None
    installer_url = None
    checksums_url = None

    for asset in release_json.get("assets") or []:
        name = asset.get("name") or ""
        url = asset.get("browser_download_url") or ""
        if not url:
            continue
        lower = name.lower()
        if lower.endswith(".exe") and "perrasetup" in lower:
            installer_name = name
            installer_url = url
        elif lower in ("sha256sums.txt", "checksums.sha256", "sha256sums"):
            checksums_url = url

    return {
        "status": "ok",
        "repo": repo,
        "tag_name": tag,
        "version": version,
        "prerelease": bool(release_json.get("prerelease", False)),
        "release_url": release_json.get("html_url")
        or f"https://github.com/{repo}/releases/tag/{tag}",
        "installer_name": installer_name or f"PerraSetup-{version}-win64.exe",
        "installer_url": installer_url
        or f"https://github.com/{repo}/releases/download/{tag}/PerraSetup-{version}-win64.exe",
        "checksums_url": checksums_url
        or f"https://github.com/{repo}/releases/download/{tag}/SHA256SUMS.txt",
        "body": release_json.get("body") or "",
    }


def _check_latest_via_web_redirect(
    repo: str,
    timeout: int = 5,
    proxy: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Fallback release lookup via github.com/releases/latest redirect (no API quota)."""
    url = f"https://github.com/{repo}/releases/latest"
    try:
        resp = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=timeout,
            proxies=_proxies(proxy),
            allow_redirects=False,
        )
    except Exception:
        return None

    if resp.status_code in (301, 302, 303, 307, 308):
        loc = resp.headers.get("Location", "")
        m = re.search(r"/releases/tag/([^/?#]+)$", loc)
        if m:
            tag = m.group(1)
            return _extract_assets_from_release({}, repo, tag)
        if loc.rstrip("/").endswith("/releases"):
            return {"status": "no_releases", "repo": repo}
    elif resp.status_code == 404:
        return {"status": "no_releases", "repo": repo}
    return None


def fetch_latest_release_info(
    repo: str = DEFAULT_CLI_REPO,
    include_prerelease: bool = False,
    timeout: int = 10,
    proxy: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Query GitHub for the latest release of ``repo``.

    Returns:
      - dict with ``status == 'ok'`` and release/asset info
      - dict with ``status == 'no_releases'`` if repo exists with no published releases
      - ``None`` on network/transport failure
    """
    proxies = _proxies(proxy)
    headers = _request_headers()

    if not include_prerelease:
        api_url = f"https://api.github.com/repos/{repo}/releases/latest"
        try:
            resp = requests.get(api_url, headers=headers, timeout=timeout, proxies=proxies)
            if resp.status_code == 200:
                data = resp.json()
                tag = data.get("tag_name")
                if tag:
                    return _extract_assets_from_release(data, repo, tag)
            elif resp.status_code == 404:
                return {"status": "no_releases", "repo": repo}
            # On 403/429 (API rate limit) or unexpected status, try redirect check
            return _check_latest_via_web_redirect(repo, timeout=timeout, proxy=proxy)
        except Exception:
            return _check_latest_via_web_redirect(repo, timeout=timeout, proxy=proxy)

    api_list_url = f"https://api.github.com/repos/{repo}/releases?per_page=10"
    try:
        resp = requests.get(api_list_url, headers=headers, timeout=timeout, proxies=proxies)
        if resp.status_code == 200:
            releases = resp.json()
            for rel in releases:
                if rel.get("draft"):
                    continue
                tag = rel.get("tag_name")
                if tag:
                    return _extract_assets_from_release(rel, repo, tag)
            return {"status": "no_releases", "repo": repo}
        if resp.status_code == 404:
            return {"status": "no_releases", "repo": repo}
    except Exception:
        pass
    return None


def check_and_record_update(
    repo: str = DEFAULT_CLI_REPO,
    timeout: int = 5,
    proxy: Optional[str] = None,
    state_path: str = CLI_UPDATE_STATE_PATH,
) -> Dict[str, Any]:
    """Check GitHub for a newer Perra release and persist result locally."""
    info = fetch_latest_release_info(repo=repo, timeout=timeout, proxy=proxy)
    state = load_cli_update_state(state_path)
    state["last_check_at"] = _now_iso()
    state["repo"] = repo
    state["current_version"] = __version__

    if info is None:
        state["last_status"] = "unreachable"
        save_cli_update_state(state, state_path)
        return state

    if info.get("status") == "no_releases":
        state["last_status"] = "no_releases"
        state.pop("latest_version", None)
        state.pop("tag_name", None)
        state.pop("release_url", None)
        save_cli_update_state(state, state_path)
        return state

    state["last_status"] = "ok"
    state["latest_version"] = info["version"]
    state["tag_name"] = info["tag_name"]
    state["release_url"] = info["release_url"]
    save_cli_update_state(state, state_path)
    return state


def get_cached_update_notice(
    current_version: str = __version__,
    state_path: str = CLI_UPDATE_STATE_PATH,
) -> Optional[str]:
    """Read cached CLI update state (no network I/O) and format notice if newer."""
    state = load_cli_update_state(state_path)
    latest = state.get("latest_version")
    if not latest or not is_newer_version(latest, current_version):
        return None
    release_url = state.get("release_url") or f"https://github.com/{DEFAULT_CLI_REPO}/releases"
    return (
        f"[!] Perra v{latest} is available (you have v{current_version}). "
        f"Run 'perra update' to upgrade ({release_url})."
    )


def spawn_background_update_check(
    repo: str = DEFAULT_CLI_REPO,
    proxy: Optional[str] = None,
) -> bool:
    """Launch a detached background process to check GitHub releases non-blockingly.

    Returns True if the background worker was spawned, False otherwise.
    Never blocks the caller or shares stdio handles.
    """
    if getattr(sys, "frozen", False):
        cmd = [sys.executable, "--_bg-update-check"]
    else:
        cmd = [sys.executable, "-m", "perra", "--_bg-update-check"]

    if repo and repo != DEFAULT_CLI_REPO:
        cmd.extend(["--_bg-update-repo", repo])
    if proxy:
        cmd.extend(["--_bg-update-proxy", proxy])

    popen_kwargs: Dict[str, Any] = {
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
        "close_fds": True,
    }
    if platform.system() == "Windows":
        detached = getattr(subprocess, "DETACHED_PROCESS", 0x00000008)
        new_group = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)
        no_window = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
        popen_kwargs["creationflags"] = detached | new_group | no_window
    else:
        popen_kwargs["start_new_session"] = True

    try:
        subprocess.Popen(cmd, **popen_kwargs)
        return True
    except Exception:
        return False


def _parse_sha256sums(text: str) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^([0-9a-fA-F]{64})\s+\*?(.+)$", line)
        if m:
            mapping[os.path.basename(m.group(2).strip())] = m.group(1).lower()
    return mapping


def _download_file(
    url: str,
    dest_path: Path,
    timeout: int = 120,
    proxy: Optional[str] = None,
) -> None:
    resp = requests.get(
        url,
        headers={"User-Agent": USER_AGENT},
        timeout=timeout,
        proxies=_proxies(proxy),
        stream=True,
    )
    resp.raise_for_status()
    with open(dest_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=65536):
            if chunk:
                f.write(chunk)


def _verify_sha256(file_path: Path, expected_hex: str) -> bool:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest().lower() == expected_hex.lower()


def _confirm_prompt(prompt: str) -> bool:
    if not sys.stdin or not sys.stdin.isatty():
        return False
    try:
        answer = input(prompt).strip().lower()
    except (EOFError, KeyboardInterrupt):
        return False
    return answer in ("", "y", "yes")


def _update_frozen_windows(info: Dict[str, Any], yes: bool, proxy: Optional[str]) -> int:
    if platform.system() != "Windows":
        print(f"[!] Self-update installer is currently Windows-only. Download from: {info['release_url']}")
        return 1

    if not yes:
        if not sys.stdin or not sys.stdin.isatty():
            print(
                "[!] Confirmation required in non-interactive mode. Re-run with: perra update --yes",
                file=sys.stderr,
            )
            return 2
        if not _confirm_prompt(
            f"[?] Download and install Perra v{info['version']} silently now? [Y/n] "
        ):
            print("[*] Update cancelled.")
            return 0

    tmp_dir = Path(tempfile.mkdtemp(prefix="perra_update_"))
    installer_path = tmp_dir / info["installer_name"]
    checksums_path = tmp_dir / "SHA256SUMS.txt"

    try:
        print(f"[*] Downloading checksum manifest from {info['checksums_url']}...")
        _download_file(info["checksums_url"], checksums_path, proxy=proxy)
        sums = _parse_sha256sums(checksums_path.read_text(encoding="utf-8", errors="replace"))
        expected_hash = sums.get(info["installer_name"])
        if not expected_hash:
            print(
                f"[!] Checksum for {info['installer_name']} not found in SHA256SUMS.txt; aborting.",
                file=sys.stderr,
            )
            shutil.rmtree(tmp_dir, ignore_errors=True)
            return 1

        print(f"[*] Downloading {info['installer_name']}...")
        _download_file(info["installer_url"], installer_path, proxy=proxy)

        if not _verify_sha256(installer_path, expected_hash):
            print(
                "[!] SHA-256 verification FAILED for downloaded installer; aborting.",
                file=sys.stderr,
            )
            shutil.rmtree(tmp_dir, ignore_errors=True)
            return 1
        print("[+] SHA-256 checksum verified.")
    except Exception as exc:
        print(f"[!] Failed to download or verify update: {exc}", file=sys.stderr)
        shutil.rmtree(tmp_dir, ignore_errors=True)
        return 1

    install_dir = Path(sys.executable).resolve().parent
    cmd = [
        str(installer_path),
        "/VERYSILENT",
        "/SUPPRESSMSGBOXES",
        "/NORESTART",
        "/CLOSEAPPLICATIONS",
        f"/DIR={install_dir}",
    ]
    print(f"[+] Launching installer for Perra v{info['version']} -> {install_dir}")
    print("[*] Exiting current Perra process so files can be replaced...")
    subprocess.Popen(
        cmd,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=getattr(subprocess, "DETACHED_PROCESS", 0x00000008)
        | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200),
        close_fds=True,
    )
    return 0


def _update_source_install(info: Dict[str, Any], yes: bool) -> int:
    repo = info["repo"]
    tag = info["tag_name"]
    pkg_dir = Path(__file__).resolve().parents[1]
    is_git_repo = (pkg_dir / ".git").exists()

    if not yes:
        print(f"[*] Running from Python environment ({sys.executable}), not a packaged binary.")
        if is_git_repo:
            print(f"[*] To upgrade from source: git pull --ff-only && \"{sys.executable}\" -m pip install -e \".[pdf]\"")
        else:
            print(f"[*] To upgrade via pip: \"{sys.executable}\" -m pip install --upgrade \"git+https://github.com/{repo}.git@{tag}\"")
        print(f"[*] Or download Windows installer: {info['release_url']}")
        if not sys.stdin or not sys.stdin.isatty():
            return 0
        if not _confirm_prompt(f"[?] Upgrade Python installation to {tag} now? [y/N] "):
            return 0

    try:
        if is_git_repo:
            subprocess.run(["git", "-C", str(pkg_dir), "pull", "--ff-only"], check=True)
            subprocess.run([sys.executable, "-m", "pip", "install", "-e", ".[pdf]"], cwd=str(pkg_dir), check=True)
        else:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", f"git+https://github.com/{repo}.git@{tag}"],
                check=True,
            )
        print(f"[+] Successfully upgraded Perra to {tag}.")
        return 0
    except Exception as exc:
        print(f"[!] Upgrade failed: {exc}", file=sys.stderr)
        return 1


def run_cli_update(
    check_only: bool = False,
    yes: bool = False,
    prerelease: bool = False,
    force: bool = False,
    repo: str = DEFAULT_CLI_REPO,
    proxy: Optional[str] = None,
    state_path: str = CLI_UPDATE_STATE_PATH,
) -> int:
    """Execute the `perra update` workflow."""
    print(f"[*] Checking GitHub releases for {repo} (current: v{__version__})...")
    info = fetch_latest_release_info(
        repo=repo,
        include_prerelease=prerelease,
        timeout=15,
        proxy=proxy,
    )

    state = load_cli_update_state(state_path)
    state["last_check_at"] = _now_iso()
    state["repo"] = repo
    state["current_version"] = __version__

    if info is None:
        state["last_status"] = "unreachable"
        save_cli_update_state(state, state_path)
        print(f"[!] Could not reach GitHub releases for {repo}.", file=sys.stderr)
        return 1

    if info.get("status") == "no_releases":
        state["last_status"] = "no_releases"
        state.pop("latest_version", None)
        state.pop("tag_name", None)
        state.pop("release_url", None)
        save_cli_update_state(state, state_path)
        print(f"[*] No published releases found yet on https://github.com/{repo}/releases (current: v{__version__}).")
        return 0

    latest = info["version"]
    state["last_status"] = "ok"
    state["latest_version"] = latest
    state["tag_name"] = info["tag_name"]
    state["release_url"] = info["release_url"]
    save_cli_update_state(state, state_path)

    newer = is_newer_version(latest, __version__)
    if newer:
        print(f"[+] New version available: v{latest} (current: v{__version__})")
        print(f"    Release: {info['release_url']}")
    else:
        print(f"[+] Perra is up to date (current: v{__version__}, latest: v{latest}).")

    if check_only:
        return 0

    if not newer and not force:
        return 0

    if getattr(sys, "frozen", False):
        return _update_frozen_windows(info, yes=yes, proxy=proxy)
    return _update_source_install(info, yes=yes)
