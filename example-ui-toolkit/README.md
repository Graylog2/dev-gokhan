# GLC UI Sketch

A small Starlette + htmx + Pico CSS page that lists Graylog Cloud tenants.

## 1. Set your credentials

Open `config.py` and fill in:

```python
GLC_USERNAME = "..."
GLC_PASSWORD = "..."
```

Optional environment variables: `GLC_API_URL`, `GLC_TENANT_ENVIRONMENT` (default `prod`),
`GLC_CACHE_TTL_SECONDS` (default `20`), `GLC_HTTP_TIMEOUT_SECONDS` (default `20`).

## 2. Run

```bash
uv sync
uv run uvicorn app:app
```

Open http://127.0.0.1:8000

## 3. Unlock the drawer

Clicking a tenant first shows a "drawer is missing" message. To get the detail panel:

```bash
mv templates/drawer.html.tpl templates/drawer.html
```

Restart the app and click any tenant again.
