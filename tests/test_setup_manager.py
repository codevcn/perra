"""Tests for scripts/setup_manager.py."""

from __future__ import annotations

import hashlib
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

from scripts import setup_manager


def test_agent_skill_targets_points_to_three_agents(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    targets = setup_manager.agent_skill_targets()

    assert set(targets.keys()) == {"antigravity", "codex", "claude"}
    assert targets["antigravity"] == tmp_path / ".gemini" / "config" / "skills" / "perra"
    assert targets["codex"] == tmp_path / ".codex" / "skills" / "perra"
    assert targets["claude"] == tmp_path / ".claude" / "skills" / "perra"


def test_cmd_install_skills_copies_skill_for_all_agents(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    rc = setup_manager.cmd_install_skills(Namespace(agents=""))

    assert rc == 0
    for agent_dir in setup_manager.agent_skill_targets().values():
        assert (agent_dir / "SKILL.md").is_file()
        assert "perra" in (agent_dir / "SKILL.md").read_text(encoding="utf-8").lower()


def test_cmd_install_skills_filters_agent_and_rejects_unknown(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    assert setup_manager.cmd_install_skills(Namespace(agents="codex")) == 0
    assert (tmp_path / ".codex" / "skills" / "perra" / "SKILL.md").is_file()
    assert not (tmp_path / ".claude" / "skills" / "perra" / "SKILL.md").exists()

    assert setup_manager.cmd_install_skills(Namespace(agents="unknown-agent")) == 2


def test_write_sha256sums_records_all_artifacts(tmp_path):
    exe_file = tmp_path / "PerraSetup-0.1.0-win64.exe"
    exe_file.write_bytes(b"binary-content")
    # Pre-existing SHA256SUMS.txt must be overwritten and not self-hashed.
    (tmp_path / "SHA256SUMS.txt").write_text("stale\n", encoding="utf-8")

    sums_path = setup_manager._write_sha256sums(tmp_path)
    expected = hashlib.sha256(b"binary-content").hexdigest()
    content = sums_path.read_text(encoding="utf-8").strip()

    assert content == f"{expected}  PerraSetup-0.1.0-win64.exe"


def test_find_iscc_uses_path_or_env(tmp_path, monkeypatch):
    fake_iscc = tmp_path / "Programs" / "Inno Setup 6" / "ISCC.exe"
    fake_iscc.parent.mkdir(parents=True)
    fake_iscc.write_bytes(b"")

    with patch("scripts.setup_manager.shutil.which", return_value=None):
        monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
        monkeypatch.setenv("ProgramFiles(x86)", str(tmp_path / "none"))
        monkeypatch.setenv("ProgramFiles", str(tmp_path / "none"))
        found = setup_manager.find_iscc()

    assert found == fake_iscc
