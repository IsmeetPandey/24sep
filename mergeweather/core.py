from __future__ import annotations
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
import subprocess

@dataclass(frozen=True)
class Hotspot:
    path: str
    score: float
    changed_with: tuple[tuple[str, int], ...]
    evidence_commits: int

def _git(root: Path, *args: str) -> str:
    if any("\x00" in a for a in args):
        raise ValueError("NUL byte in git argument")
    p = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False)
    if p.returncode:
        raise RuntimeError(p.stderr.strip() or "git command failed")
    return p.stdout

def validate_ref(ref: str) -> str:
    if not ref or ref.startswith("-") or "\x00" in ref or len(ref) > 256:
        raise ValueError("invalid git ref")
    return ref

def changed_files(root: Path, base: str, head: str) -> list[str]:
    base, head = validate_ref(base), validate_ref(head)
    out = _git(root, "diff", "--name-only", "--diff-filter=ACMR", f"{base}...{head}")
    return sorted({line for line in out.splitlines() if line.strip()})

def history_sets(root: Path, max_commits: int = 200) -> list[set[str]]:
    if not 1 <= max_commits <= 5000:
        raise ValueError("max_commits must be between 1 and 5000")
    out = _git(root, "log", f"-n{max_commits}", "--name-only", "--format=%x1e")
    return [{line.strip() for line in block.splitlines() if line.strip()} for block in out.split("\x1e") if block.strip()]

def rank_hotspots(changed: list[str], histories: list[set[str]], *, min_cochanges: int = 2) -> list[Hotspot]:
    if min_cochanges < 1:
        raise ValueError("min_cochanges must be positive")
    target = set(changed)
    pair_counts: dict[str, Counter[str]] = defaultdict(Counter)
    support = Counter()
    for files in histories:
        overlap = files & target
        for path in overlap:
            support[path] += 1
            for other in files - {path}:
                pair_counts[path][other] += 1
    results = []
    for path in sorted(target):
        neighbors = sorted(((other, n) for other, n in pair_counts[path].items() if n >= min_cochanges), key=lambda x: (-x[1], x[0]))[:5]
        score = round(sum(n for _, n in neighbors) / max(support[path], 1), 2)
        results.append(Hotspot(path, score, tuple(neighbors), support[path]))
    return sorted(results, key=lambda h: (-h.score, h.path))

def analyze(root: Path, base: str, head: str, *, max_commits: int = 200, min_cochanges: int = 2) -> list[Hotspot]:
    return rank_hotspots(changed_files(root, base, head), history_sets(root, max_commits), min_cochanges=min_cochanges)
