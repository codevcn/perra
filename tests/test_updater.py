"""Tests for Perra CLI non-blocking update checking and self-update command."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

from perra import updater
from perra.__version__ import __version__


def test_parse_semver_and_ordering():
    assert updater.is_newer_version("0.2.0", "0.1.0") is True
    assert updater.is_newer_version("v0.2.0", "0.1.0") is True
    assert updater.is_newer_version("0.1.0", "0.1.0") is False
    assert updater.is_newer_version("0.0.9", "0.1.0") is False
    assert updater.is_newer_version("0.2.0", "0.2.0-rc1") is True
    assert updater.is_newer_version("0.2.0-rc2", "0.2.0-rc1") is True
    assert updater.is_newer_version("1.0.0", "0.99.9") is True


def test_fetch_latest_release_info_from_github_api():
    payload = {
        "tag_name": "v0.2.0",
        "prerelease": False,
        "html_url": "https://github.com/codevcn/perra/releases/tag/v0.2.0",
        "assets": [
            {
                "name": "PerraSetup-0.2.0-win64.exe",
                "browser_download_url": "https://example.invalid/PerraSetup-0.2.0-win64.exe",
            },
            {
                "name": "SHA256SUMS.txt",
                "browser_download_url": "https://example.invalid/SHA256SUMS.txt",
            },
        ],
    }
    mock_resp = Mock(status_code=200)
    mock_resp.json.return_value = payload

    with patch("perra.updater.requests.get", return_value=mock_resp):
        info = updater.fetch_latest_release_info("codevcn/perra", timeout=3)

    assert info is not None
    assert info["status"] == "ok"
    assert info["version"] == "0.2.0"
    assert info["tag_name"] == "v0.2.0"
    assert info["installer_name"] == "PerraSetup-0.2.0-win64.exe"
    assert info["checksums_url"] == "https://example.invalid/SHA256SUMS.txt"


def test_fetch_latest_release_info_falls_back_on_rate_limit():
    api_403 = Mock(status_code=403)
    web_302 = Mock(
        status_code=302,
        headers={"Location": "https://github.com/codevcn/perra/releases/tag/v0.3.0"},
    )

    with patch("perra.updater.requests.get", side_effect=[api_403, web_302]):
        info = updater.fetch_latest_release_info("codevcn/perra", timeout=3)

    assert info is not None
    assert info["status"] == "ok"
    assert info["version"] == "0.3.0"
    assert info["installer_name"] == "PerraSetup-0.3.0-win64.exe"


def test_fetch_latest_release_info_no_releases_and_network_error():
    not_found = Mock(status_code=404)
    with patch("perra.updater.requests.get", return_value=not_found):
        info = updater.fetch_latest_release_info("codevcn/perra")
    assert info == {"status": "no_releases", "repo": "codevcn/perra"}

    with patch("perra.updater.requests.get", side_effect=OSError("offline")):
        assert updater.fetch_latest_release_info("codevcn/perra") is None


def test_check_and_record_update_persists_state_and_formats_notice(tmp_path):
    state_file = str(tmp_path / "cli_update_state.json")
    release_info = {
        "status": "ok",
        "repo": "codevcn/perra",
        "tag_name": "v99.0.0",
        "version": "99.0.0",
        "prerelease": False,
        "release_url": "https://github.com/codevcn/perra/releases/tag/v99.0.0",
        "installer_name": "PerraSetup-99.0.0-win64.exe",
        "installer_url": "https://example.invalid/setup.exe",
        "checksums_url": "https://example.invalid/SHA256SUMS.txt",
        "body": "",
    }

    with patch("perra.updater.fetch_latest_release_info", return_value=release_info):
        state = updater.check_and_record_update(state_path=state_file)

    assert state["last_status"] == "ok"
    assert state["latest_version"] == "99.0.0"

    # Subsequent reads must stay purely local and surface the notice
    with patch("perra.updater.fetch_latest_release_info", side_effect=AssertionError("must not hit network")):
        notice = updater.get_cached_update_notice(
            current_version="0.1.0", state_path=state_file
        )
        no_notice = updater.get_cached_update_notice(
            current_version="99.0.0", state_path=state_file
        )

    assert notice is not None
    assert "v99.0.0" in notice
    assert "perra update" in notice
    assert no_notice is None


def test_spawn_background_update_check_is_non_blocking():
    proc_mock = Mock()
    with patch("perra.updater.subprocess.Popen", return_value=proc_mock) as popen_mock:
        started = updater.spawn_background_update_check(
            repo="codevcn/perra", proxy="http://127.0.0.1:8080"
        )

    assert started is True
    popen_mock.assert_called_once()
    cmd = popen_mock.call_args.args[0]
    kwargs = popen_mock.call_args.kwargs
    assert "--_bg-update-check" in cmd
    assert "--_bg-update-proxy" in cmd
    assert kwargs["stdin"] is subprocess.DEVNULL
    assert kwargs["stdout"] is subprocess.DEVNULL
    assert kwargs["stderr"] is subprocess.DEVNULL
    proc_mock.wait.assert_not_called()
    proc_mock.communicate.assert_not_called()


def test_run_cli_update_check_only_does_not_install(tmp_path, capsys):
    state_file = str(tmp_path / "state.json")
    info = {
        "status": "ok",
        "repo": "codevcn/perra",
        "tag_name": f"v{__version__}",
        "version": __version__,
        "prerelease": False,
        "release_url": "https://github.com/codevcn/perra/releases/tag/v0.1.0",
        "installer_name": "PerraSetup-0.1.0-win64.exe",
        "installer_url": "https://example.invalid/setup.exe",
        "checksums_url": "https://example.invalid/SHA256SUMS.txt",
        "body": "",
    }
    with patch("perra.updater.fetch_latest_release_info", return_value=info):
        rc = updater.run_cli_update(check_only=True, state_path=state_file)

    assert rc == 0
    captured = capsys.readouterr()
    assert "up to date" in captured.out.lower()


def test_update_frozen_windows_verifies_sha256_and_launches_silent_installer(tmp_path, monkeypatch):
    installer_bytes = b"MZ-fake-inno-installer"
    expected_sha = hashlib.sha256(installer_bytes).hexdigest()
    info = {
        "repo": "codevcn/perra",
        "tag_name": "v99.0.0",
        "version": "99.0.0",
        "release_url": "https://github.com/codevcn/perra/releases/tag/v99.0.0",
        "installer_name": "PerraSetup-99.0.0-win64.exe",
        "installer_url": "https://example.invalid/PerraSetup-99.0.0-win64.exe",
        "checksums_url": "https://example.invalid/SHA256SUMS.txt",
    }

    def fake_download(url: str, dest: Path, timeout: int = 120, proxy=None):
        if url.endswith("SHA256SUMS.txt"):
            dest.write_text(f"{expected_sha}  PerraSetup-99.0.0-win64.exe\n", encoding="utf-8")
        else:
            dest.write_bytes(installer_bytes)

    fake_install_dir = tmp_path / "Programs" / "Perra"
    fake_install_dir.mkdir(parents=True)
    fake_exe = fake_install_dir / "perra.exe"
    fake_exe.write_bytes(b"")

    monkeypatch.setattr(updater.sys, "frozen", True, raising=False)
    monkeypatch.setattr(updater.sys, "executable", str(fake_exe))
    monkeypatch.setattr(updater.platform, "system", lambda: "Windows")
    monkeypatch.setattr(updater, "_download_file", fake_download)

    with patch("perra.updater.subprocess.Popen") as popen_mock:
        rc = updater._update_frozen_windows(info, yes=True, proxy=None)

    assert rc == 0
    popen_mock.assert_called_once()
    cmd = popen_mock.call_args.args[0]
    assert "/VERYSILENT" in cmd
    assert "/CLOSEAPPLICATIONS" in cmd
    assert f"/DIR={fake_install_dir}" in cmd


def test_update_frozen_windows_aborts_on_bad_checksum(tmp_path, monkeypatch, capsys):
    info = {
        "repo": "codevcn/perra",
        "tag_name": "v99.0.0",
        "version": "99.0.0",
        "release_url": "https://github.com/codevcn/perra/releases/tag/v99.0.0",
        "installer_name": "PerraSetup-99.0.0-win64.exe",
        "installer_url": "https://example.invalid/PerraSetup-99.0.0-win64.exe",
        "checksums_url": "https://example.invalid/SHA256SUMS.txt",
    }

    def fake_download(url: str, dest: Path, timeout: int = 120, proxy=None):
        if url.endswith("SHA256SUMS.txt"):
            dest.write_text(("0" * 64) + "  PerraSetup-99.0.0-win64.exe\n", encoding="utf-8")
        else:
            dest.write_bytes(b"tampered-installer")

    monkeypatch.setattr(updater.platform, "system", lambda: "Windows")
    monkeypatch.setattr(updater, "_download_file", fake_download)

    with patch("perra.updater.subprocess.Popen") as popen_mock:
        rc = updater._update_frozen_windows(info, yes=True, proxy=None)

    assert rc == 1
    popen_mock.assert_not_called()
    assert "SHA-256 verification FAILED" in capsys.readouterr().err


def test_frozen_non_interactive_requires_yes_flag(monkeypatch, capsys):
    info = {
        "version": "99.0.0",
        "release_url": "https://github.com/codevcn/perra/releases/tag/v99.0.0",
    }
    fake_stdin = Mock()
    fake_stdin.isatty.return_value = False
    monkeypatch.setattr(updater.platform, "system", lambda: "Windows")
    monkeypatch.setattr(updater.sys, "stdin", fake_stdin)

    rc = updater._update_frozen_windows(info, yes=False, proxy=None)
    assert rc == 2
    assert "--yes" in capsys.readouterr().err
