import hashlib
import os
import shutil
import subprocess
import sys

import pytest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HOOK = os.path.join(REPO, "harness", "poc-vendor-neutral", "bin", "harness-events.py")

pytestmark = pytest.mark.skipif(not os.path.isfile(HOOK), reason="harness hook not present")


def _manifest(root):
    out = {}
    for r, _, fs in os.walk(root):
        for f in fs:
            p = os.path.join(r, f)
            with open(p, "rb") as fh:
                out[os.path.relpath(p, root)] = hashlib.sha1(fh.read()).hexdigest()
    return out


def _run_hook(kl_home, project):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(project), KNOWLEDGELIB_HOME=str(kl_home))
    return subprocess.run(
        [sys.executable, HOOK, "knowledgelib-sync"], env=env, input="{}", capture_output=True, text=True, timeout=60
    )


@pytest.fixture
def kl_home(tmp_path):
    home = tmp_path / "kl"
    (home / "src").mkdir(parents=True)
    (home / "self-docs").mkdir()
    for name in ("extract_tech_notes.py", "validate_canonical.py"):
        shutil.copy(os.path.join(REPO, "src", name), home / "src" / name)
    return home


def _project_with_note(tmp_path):
    proj = tmp_path / "other-project"
    (proj / "self-docs").mkdir(parents=True)
    (proj / "self-docs" / "adapter_note.md").write_text(
        "# Adapter note\n\nTích hợp api workday adapter, nội dung 98765.\n", encoding="utf-8"
    )
    return proj


def test_hook_imports_once_then_is_idempotent(tmp_path, kl_home):
    proj = _project_with_note(tmp_path)
    r = _run_hook(kl_home, proj)
    assert r.returncode == 0
    imported = kl_home / "self-docs" / "integration" / "adapter-note.md"
    assert imported.exists()

    before = _manifest(kl_home)
    mtime = imported.stat().st_mtime_ns
    for _ in range(2):
        assert _run_hook(kl_home, proj).returncode == 0
    assert _manifest(kl_home) == before, "chạy lại không được ghi đè/sinh file"
    assert imported.stat().st_mtime_ns == mtime


def test_hook_noop_when_project_is_the_knowledgelib_repo(tmp_path, kl_home):
    (kl_home / "self-docs" / "MEMORY_INDEX.md").write_text("# index\n", encoding="utf-8")
    (kl_home / "self-docs" / "root_note.md").write_text("# Root note\n\napi adapter\n", encoding="utf-8")
    before = _manifest(kl_home)
    assert _run_hook(kl_home, kl_home).returncode == 0
    assert _manifest(kl_home) == before, "self->self không được phân loại lại file ở gốc self-docs"
