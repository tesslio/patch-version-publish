# tessl-smart-publish

Composite GitHub Action that publishes [tessl](https://tessl.io) tiles with smart version handling.

- If `tile.json` version was **manually bumped** in the commit — publishes as-is
- If version is **unchanged** — queries the registry for the latest published version and bumps patch from that

## Usage

```yaml
- uses: actions/checkout@v4
- uses: tesslio/setup-tessl@v2
  with:
    token: ${{ secrets.TESSL_TOKEN }}
- uses: jbaruch/tessl-smart-publish@v1
```

For tiles in a subdirectory:

```yaml
- uses: jbaruch/tessl-smart-publish@v1
  with:
    path: tiles/my-tile
```

## Inputs

| Input | Description | Default |
|---|---|---|
| `path` | Path to the tile directory | `.` |

## Outputs

| Output | Description |
|---|---|
| `version` | The version that was published (including auto-bumped) |

## Requirements

- `tessl` must be on PATH (use `tesslio/setup-tessl`)
- `TESSL_TOKEN` env var set (handled by `tesslio/setup-tessl`)
- `contents: write` permission — when auto-bumping, the action commits the new version back to `tile.json` (with `[skip ci]`) so the repo stays in sync with the registry
- The action runs `git fetch --deepen=1` to retrieve the parent commit, so it can compare `tile.json` version between the current and previous commit to detect manual bumps
