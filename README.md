# tessl-smart-publish

Composite GitHub Action that publishes [tessl](https://tessl.io) tiles with automatic patch versioning.

On every push, the action queries the registry for the latest published version, bumps patch, updates `tile.json`, publishes, and commits the version back (with `[skip ci]`).

## Usage

```yaml
- uses: actions/checkout@v4
- uses: jbaruch/tessl-smart-publish@v1
  with:
    token: ${{ secrets.TESSL_TOKEN }}
```

For tiles in a subdirectory:

```yaml
- uses: jbaruch/tessl-smart-publish@v1
  with:
    token: ${{ secrets.TESSL_TOKEN }}
    path: tiles/my-tile
```

## Inputs

| Input | Description | Required | Default |
|---|---|---|---|
| `token` | Tessl API token | Yes | |
| `path` | Path to the tile directory | No | `.` |

## Outputs

| Output | Description |
|---|---|
| `version` | The version that was published |

## Requirements

- `contents: write` permission — the action commits the bumped version back to `tile.json`
