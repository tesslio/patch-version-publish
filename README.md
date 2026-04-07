# tessl-smart-publish

Composite GitHub Action that reviews and publishes [tessl](https://tessl.io) tiles with smart version handling.

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
- uses: jbaruch/tessl-smart-publish@v1
  with:
    review-threshold: 85  # optional, 0 to skip review
```

## Inputs

| Input | Description | Default |
|---|---|---|
| `review-threshold` | Minimum `tessl skill review` score (0-100). `0` skips review. | `0` |

## Requirements

- `tessl` must be on PATH (use `tesslio/setup-tessl`)
- `fetch-depth: 2` on checkout (to compare with previous commit)
- `TESSL_TOKEN` env var set (handled by `tesslio/setup-tessl`)
