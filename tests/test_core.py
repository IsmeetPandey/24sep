import subprocess
from pathlib import Path
from mergeweather.core import changed_files, history_sets, rank_hotspots, validate_ref

def git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)

def commit(repo, message):
    git(repo, "add", ".")
    git(repo, "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-m", message)

def test_history_coupling(tmp_path):
    git(tmp_path, "init", "-b", "main")
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.txt").write_text("b")
    commit(tmp_path, "base")
    git(tmp_path, "checkout", "-b", "feature")
    (tmp_path / "a.txt").write_text("a2")
    (tmp_path / "b.txt").write_text("b2")
    commit(tmp_path, "coupled")
    assert changed_files(tmp_path, "main", "HEAD") == ["a.txt", "b.txt"]
    ranked = rank_hotspots(["a.txt"], history_sets(tmp_path, 10), min_cochanges=1)
    assert ranked[0].changed_with[0] == ("b.txt", 1)

def test_empty_change_is_safe():
    assert rank_hotspots([], [{"a.txt"}]) == []

def test_ref_rejects_option_injection():
    try:
        validate_ref("--upload-pack=bad")
    except ValueError:
        pass
    else:
        raise AssertionError("unsafe ref accepted")
