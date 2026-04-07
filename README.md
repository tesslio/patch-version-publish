# tessl-smart-publish

Composite GitHub Action that publishes [tessl](https://tessl.io) tiles with smart version handling.

- If `tile.json` version was **manually bumped** in the commit — publishes as-is
- If version is **unchanged** — auto-bumps patch before publishing

## Usage

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 2  # required to detect version changes
- uses: tesslio/setup-tessl@v2
  with:
    token: ${{ secrets.TESSL_API_TOKEN }}
- run: tessl skill review --threshold 85  # optional
- uses: jbaruch/tessl-smart-publish@v1
```

## Requirements

- `tessl` must be on PATH (use `tesslio/setup-tessl`)
- `fetch-depth: 2` on checkout (to compare with previous commit)
- `TESSL_TOKEN` env var set (handled by `tesslio/setup-tessl`)
