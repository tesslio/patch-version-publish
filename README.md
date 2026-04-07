# tessl-smart-publish

Composite GitHub Action that publishes [tessl](https://tessl.io) tiles with smart version handling.

- If `tile.json` version was **manually bumped** in the commit — publishes as-is
- If version is **unchanged** — auto-bumps patch before publishing

## Usage

```yaml
- uses: actions/checkout@v4
- uses: tesslio/setup-tessl@v2
  with:
    token: ${{ secrets.TESSL_TOKEN }}
- uses: jbaruch/tessl-smart-publish@v1
```

## Requirements

- `tessl` must be on PATH (use `tesslio/setup-tessl`)
- `TESSL_TOKEN` env var set (handled by `tesslio/setup-tessl`)
- The action runs `git fetch --deepen=1` to retrieve the parent commit, so it can compare `tile.json` version between the current and previous commit to detect manual bumps
