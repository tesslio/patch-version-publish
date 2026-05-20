# patch-version-publish

Composite GitHub Action that publishes [tessl](https://tessl.io) tiles with automatic patch versioning.

## What this does

Every push changes the tile's content, and distinct content should have a distinct version. This action handles that automatically: it queries the registry for the latest published version, bumps patch, updates `tile.json`, publishes, and commits the version back (with `[skip ci]`).

## What this doesn't do

This is not a replacement for proper version management. It's a catch-all for chore commits and routine changes where you don't intend to craft a new release. There's no option for minor or major bumps on purpose.

For a real release — bump the version in `tile.json` yourself. The action will detect that the local version is ahead of the registry and publish it as-is.

## Usage

```yaml
name: Publish
on:
  push:
    branches: [main]

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: write
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
      - uses: tesslio/patch-version-publish@v1
        with:
          token: ${{ secrets.TESSL_TOKEN }}
```

For tiles in a subdirectory:

```yaml
name: Publish
on:
  push:
    branches: [main]

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: write
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
      - uses: tesslio/patch-version-publish@v1
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

The action must be run from a job that declares the following `permissions:` (see the "Usage" examples above for placement — `permissions:` is a job-level key and can't be set by the action itself):

- `id-token: write` permission — lets the Tessl CLI fetch a GitHub OIDC token and present it to the registry so the published tile is linked back to its source repo. Without it, `tessl tile publish` still reports `Published <name>@<version>` and the workflow goes green, but the tile is published **unlinked** — there is no signal in the logs that anything is wrong.
- `contents: write` permission — the action commits the bumped version back to `tile.json`
- `pull-requests: write` permission — if branch protection blocks direct push, the action falls back to creating a PR with the version bump. This permission alone is not enough: the repository (or organization) must also have **Settings → Actions → General → Workflow permissions → "Allow GitHub Actions to create and approve pull requests"** enabled. Without that setting, `gh pr create` fails with `Resource not accessible by integration`. If both direct push and PR creation are blocked, the action publishes successfully and emits a warning rather than failing the workflow — the next run will re-bump from the registry.
