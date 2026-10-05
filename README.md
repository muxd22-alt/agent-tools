# agent-tools

Part of the muxd22-alt monorepo consolidation (50 repos -> 5).

Every member lives in `repos/<name>/` and stays self-contained.
Identical CI configs across the old repos were replaced by the single,
shared workflow set in `.github/workflows/`:

- **CI** — structure, oversized-file, secret and syntax checks on every push/PR
- **Daily Digest** — scheduled 06:00 UTC, publishes a per-member activity table
  to the `Daily Digest` issue and the job summary

## Members

| folder | language | files | size | merged (absorbed repos) |
|---|---|---:|---:|---|
| `AGI_Track` | JavaScript | 104 | 5.4 MB | — |
| `CLI-Anything` | Python | 320 | 8.8 MB | — |
| `MSA` | Python | 40 | 1.3 MB | — |
| `OpenViking` | Python | 1497 | 21.0 MB | — |
| `Signal-OS` | Python | 19 | 0.1 MB | — |
| `autoresearch` | Python | 15 | 0.8 MB | `autoresearch-amd`, `autoresearch-amd-copy` |
| `jobs` | HTML | 362 | 44.0 MB | — |
| `laya-coreml` | Python | 154 | 37.7 MB | — |
| `newsjack` | Go | 4313 | 55.1 MB | — |
| `reseaech` | Python | 13 | 0.4 MB | — |
| `superpowers` | Shell | 125 | 0.7 MB | — |

See `SOURCE_MAP.md` for the old-repo -> new-path mapping, including files
kept under `repos/<x>/_variants/` (conflicting versions from absorbed repos).

## Dashboard

Live combined dashboard: **[https://muxd22-alt.github.io](https://muxd22-alt.github.io)** (aggregates this monorepo with the other dashboards-type monorepos).
