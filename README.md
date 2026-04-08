# tessl-smart-publish

Composite GitHub Action that publishes [tessl](https://tessl.io) tiles with automatic patch versioning.

On every push, the action queries the registry for the latest published version, bumps patch, updates `tile.json`, publishes, and commits the version back (with `[skip ci]`).

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
| `version` | The version that was published |

## Requirements

- `tessl` must be on PATH (use `tesslio/setup-tessl`)
- `TESSL_TOKEN` env var set (handled by `tesslio/setup-tessl`)
- `contents: write` permission — the action commits the bumped version back to `tile.json`
