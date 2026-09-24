from __future__ import annotations
import argparse
import json
from pathlib import Path
from .core import changed_files, history_sets, rank_hotspots

def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="mergeweather", description="Estimate merge-conflict hotspots from Git history.")
    p.add_argument("base")
    p.add_argument("head")
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--max-commits", type=int, default=200)
    p.add_argument("--min-cochanges", type=int, default=2)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    try:
        changed = changed_files(args.root, args.base, args.head)
        findings = rank_hotspots(changed, history_sets(args.root, args.max_commits), min_cochanges=args.min_cochanges)
    except (RuntimeError, ValueError, OSError) as exc:
        print(f"mergeweather: error: {exc}")
        return 2
    if args.json:
        print(json.dumps([h.__dict__ for h in findings], indent=2))
    elif not findings:
        print("No changed files found.")
    else:
        print("Merge weather\n=============")
        for h in findings:
            label = "HIGH" if h.score >= 4 else "MED" if h.score >= 2 else "LOW"
            print(f"{label:4} {h.path}  score={h.score:.2f}  history_commits={h.evidence_commits}")
            for other, count in h.changed_with:
                print(f"      ↳ co-changed with {other} ({count} commits)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
