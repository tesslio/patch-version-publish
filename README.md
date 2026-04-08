# tessl-smart-publish

Composite GitHub Action that publishes [tessl](https://tessl.io) tiles with automatic patch versioning.

## What this does

Every push changes the tile's content, and distinct content should have a distinct version. This action handles that automatically: it queries the registry for the latest published version, bumps patch, updates `tile.json`, publishes, and commits the version back (with `[skip ci]`).

## What this doesn't do

This is not a replacement for proper version management. It's a catch-all for chore commits and routine changes where you don't intend to craft a new release. There's no option for minor or major bumps on purpose.

For a real release — bump the version in `tile.json` yourself. The action will detect that the local version is ahead of the registry and publish it as-is.

## Usage

```yaml
- uses: actions/checkout@v4
- uses: tesslio/tessl-smart-publish@v1
  with:
    token: ${{ secrets.TESSL_TOKEN }}
```

For tiles in a subdirectory:

```yaml
- uses: tesslio/tessl-smart-publish@v1
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
