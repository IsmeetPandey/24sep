# MergeWeather

**Estimate where a change is likely to collide before the merge gets painful.**

MergeWeather is a local-first CLI that combines the files in your current branch diff with the repository's historical co-change graph. It does not pretend to predict the exact future merge; it exposes historically coupled files so reviewers can inspect likely collision surfaces earlier.

## Why

Traditional conflict checks answer after branches collide. Ownership tools answer who owns a file. MergeWeather answers an earlier question:

> Which parts of this change sit in historically coupled areas of the repository?

That makes the result useful during planning and review without a hosted service or full merge simulation.

## Quick start

```bash
python -m mergeweather main HEAD
python -m mergeweather main HEAD --json
```

The analysis is read-only. Git is invoked with fixed argument vectors and no shell strings.

## How it works

```text
current diff -> changed paths
                    |
Git history ------> co-change sets
                    |
                    v
             explainable score
                    |
                    v
             files + evidence
```

A hotspot is not a guaranteed conflict. It is a historical collision surface: repeated co-change relationships indicate areas worth reviewing together.

## Output

Each finding includes the changed file, an explainable score, historical support, and up to five repeatedly co-changed neighbors. `--json` provides machine-readable output.

## Safety and limitations

- Read-only Git operations; no repository mutation.
- Git refs are validated before use.
- No shell execution and no network access from the CLI.
- History collection is bounded.
- No claim of causality or guaranteed conflict.
- New repositories have weak evidence by design.

## Development

```bash
python -m unittest discover -s tests -v
python -m mergeweather --help
```

No runtime dependencies are required.

## License

MIT
