# patch-version-publish

Composite GitHub Action that publishes [tessl](https://tessl.io) plugins with automatic patch versioning.

## What this does

Every push changes the plugin's content, and distinct content should have a distinct version. This action handles that automatically: it runs `tessl plugin publish --bump patch`, which publishes the manifest version or bumps one patch when that version already exists in the registry, then commits the version back (with `[skip ci]`).

The manifest is `.tessl-plugin/plugin.json` when present (the authoritative plugin form), falling back to the legacy `tile.json`. No configuration needed — the action detects which one the repo uses.

## What this doesn't do

This is not a replacement for proper version management. It's a catch-all for chore commits and routine changes where you don't intend to craft a new release. There's no option for minor or major bumps on purpose.

For a real release — bump the version in the manifest yourself. As long as that version isn't already in the registry, it's published as-is.

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

For plugins in a subdirectory:

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
          path: plugins/my-plugin
```

## Inputs

| Input | Description | Required | Default |
|---|---|---|---|
| `token` | Tessl API token | Yes | |
| `path` | Path to the plugin directory | No | `.` |

## Outputs

| Output | Description |
|---|---|
| `version` | The version that was published |

## Requirements

The action must be run from a job that declares the following `permissions:` (see the "Usage" examples above for placement — `permissions:` is a job-level key and can't be set by the action itself):

- `id-token: write` permission — lets the Tessl CLI fetch a GitHub OIDC token and present it to the registry so the published plugin is linked back to its source repo. The CLI would otherwise publish the plugin **unlinked** while still reporting success, so the action checks for the token up front and **fails the job** when it is missing rather than letting an unlinked publish through.
- `contents: write` permission — the action commits the bumped version back to the manifest
- `pull-requests: write` permission — if branch protection blocks direct push, the action falls back to creating a PR with the version bump
