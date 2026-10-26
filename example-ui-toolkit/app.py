"""GLC UI Sketch, Pico edition: Graylog Cloud tenant browser.

index.html is the page with the tenant table, drawer.html is the detail panel. drawer.html ships
as drawer.html.tpl. Until it is renamed, clicking a tenant shows drawer_missing.html instead.
Sorting is a plain link that reloads the page. htmx is only used to open and close the detail panel.
"""

import json
from pathlib import Path
from urllib.parse import urlencode

from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

import config
from glc_api import GlcApiError, GlcClient, Tenant, TenantFetch

DRAWER_SECTIONS = [
    (
        "Overview",
        [
            "tenant_name",
            "tenant_id",
            "tenant_type",
            "tenant_environment",
            "tenant_region",
            "status",
            "lifecycle",
            "locked",
            "workflow_inprogress",
            "product_type",
            "license_size",
            "owner_name",
            "responsible_customer_rep",
            "tenant_creator",
            "infra_provider",
            "tenant_creation_timestamp",
            "status_change_timestamp",
        ],
    ),
    ("Endpoints", ["domain", "frontend_subdomain", "forwarder_subdomain", "namespace"]),
    ("Graylog", ["graylog_"]),
    ("Okta", ["okta_", "build_okta_account"]),
]

BADGE_COLUMNS = {"status", "lifecycle", "tenant_type"}

# Sent on every response, static files included: the browser and any proxy must never keep a copy.
NO_CACHE_HEADERS = {
    "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
    "Pragma": "no-cache",  # HTTP/1.0 caches
    "Expires": "0",  # proxies that ignore Cache-Control
}

SETUP_MESSAGE = "API credentials are not set. Fill in GLC_USERNAME and GLC_PASSWORD in config.py, then restart the app."

Section = tuple[str, list[tuple[str, object]]]


def label(field: str) -> str:
    return field.replace("_", " ").capitalize()


def show(value: object) -> str:
    """How a value is printed in a cell: a dash when empty, JSON for lists and dicts."""
    if value in (None, ""):
        return "—"
    if isinstance(value, (dict, list)):
        return json.dumps(value, indent=2)
    return str(value)


def badge_tone(value: object) -> str:
    text = str(value or "").lower()
    if any(w in text for w in ("fail", "error", "deprovision", "delet", "terminat")):
        return "bad"
    if any(w in text for w in ("suspend", "stop", "lock", "pending", "progress", "trial")):
        return "warn"
    if any(w in text for w in ("active", "running", "ready", "ok", "prod", "healthy")):
        return "good"
    return "neutral"


def data_source_headers_for(fetch: TenantFetch) -> dict[str, str]:
    """Server-Timing shows up in DevTools. X-Data-Source is easy to read with curl -I."""
    if fetch.live:
        timing = f'api;dur={fetch.api_seconds * 1000:.1f};desc="live from GLC API"'
    else:
        timing = f'cache;dur=0;desc="from app cache, {fetch.age:.1f}s old"'
    return {"Server-Timing": timing, "X-Data-Source": "live" if fetch.live else "cache"}


def source_text(fetch: TenantFetch) -> str:
    if fetch.live:
        return f"live from the API, {fetch.api_seconds * 1000:.0f} ms"
    return f"from cache, {fetch.age:.1f} s old"


def sort_key(value: object) -> tuple[int, float | str]:
    """Numbers sort as numbers, text ignores case, empty values go last."""
    if value in (None, ""):
        return (2, "")
    try:
        return (0, float(str(value)))
    except ValueError:
        return (1, str(value).lower())


def sort_rows(tenants: list[Tenant], sort: str, desc: bool) -> list[Tenant]:
    present = [t for t in tenants if t.get(sort) not in (None, "")]
    empty = [t for t in tenants if t.get(sort) in (None, "")]
    present.sort(key=lambda t: sort_key(t.get(sort)), reverse=desc)
    return present + empty


def header_links(columns: list[str], sort: str, desc: bool) -> list[tuple[str, str]]:
    """(title, url) per column. Clicking the sorted column flips the direction."""
    links: list[tuple[str, str]] = []
    for col in columns:
        title = label(col)
        flip = "asc"
        if col == sort:
            title += " ▼" if desc else " ▲"
            flip = "asc" if desc else "desc"
        links.append((title, "/?" + urlencode({"sort": col, "dir": flip})))
    return links


def drawer_sections(tenant: Tenant) -> list[Section]:
    """Group fields for the detail dialog. Patterns ending in "_" are prefixes."""
    remaining = dict(tenant)
    sections: list[Section] = []
    for title, patterns in DRAWER_SECTIONS:
        exact = [p for p in patterns if p in remaining]
        prefixed = sorted(
            k for k in remaining if k not in exact and any(p.endswith("_") and k.startswith(p) for p in patterns)
        )
        items = [(k, remaining.pop(k)) for k in exact + prefixed]
        if items:
            sections.append((title, items))
    if remaining:
        sections.append(("Other", sorted(remaining.items())))
    return sections


# --- app -----------------------------------------------------------------------

BASE_DIR = Path(__file__).parent
# Checked once at startup, so renaming drawer.html.tpl needs a restart.
HAS_DRAWER = (BASE_DIR / "templates" / "drawer.html").exists()

templates = Jinja2Templates(directory=BASE_DIR / "templates")
templates.env.filters.update(label=label, badge_tone=badge_tone, show=show)

is_configured = config.credentials_configured()
api = GlcClient(
    config.GLC_API_URL,
    config.GLC_USERNAME,
    config.GLC_PASSWORD,
    config.TENANT_ENVIRONMENT,
    cache_ttl=config.CACHE_TTL_SECONDS,
    timeout=config.HTTP_TIMEOUT_SECONDS,
)


def index(request: Request) -> Response:
    environment = config.TENANT_ENVIRONMENT
    if not is_configured:
        return templates.TemplateResponse(request, "index.html", {"environment": environment, "error": SETUP_MESSAGE})
    try:
        fetch = api.fetch_tenants()
    except GlcApiError as exc:
        return templates.TemplateResponse(request, "index.html", {"environment": environment, "error": str(exc)})
    columns = config.DEFAULT_COLUMNS
    sort = request.query_params.get("sort", "tenant_name")
    if sort not in columns:
        sort = "tenant_name"
    desc = request.query_params.get("dir") == "desc"
    context = {
        "environment": environment,
        "error": None,
        "columns": columns,
        "badges": BADGE_COLUMNS,
        "headers": header_links(columns, sort, desc),
        "rows": sort_rows(fetch.tenants, sort, desc),
        "source": source_text(fetch),
    }
    return templates.TemplateResponse(request, "index.html", context, headers=data_source_headers_for(fetch))


def tenant(request: Request) -> Response:
    if not is_configured:
        raise HTTPException(404)
    if not HAS_DRAWER:
        return templates.TemplateResponse(request, "drawer_missing.html")
    name = request.path_params["name"]
    try:
        fetch = api.fetch_tenants()
    except GlcApiError as exc:
        raise HTTPException(502, str(exc)) from exc
    found = next((t for t in fetch.tenants if t.get("tenant_name") == name), None)
    if found is None:
        raise HTTPException(404)
    context = {"name": name, "sections": drawer_sections(found)}
    return templates.TemplateResponse(request, "drawer.html", context, headers=data_source_headers_for(fetch))


def drawer_close(request: Request) -> Response:
    return HTMLResponse("")


def health(request: Request) -> Response:
    return JSONResponse({"status": "ok"})


async def no_browser_cache(request: Request, call_next: RequestResponseEndpoint) -> Response:
    response = await call_next(request)
    response.headers.update(NO_CACHE_HEADERS)
    return response


app = Starlette(
    routes=[
        Route("/", index),
        Route("/tenants/{name}", tenant),
        Route("/drawer/close", drawer_close),
        Route("/health", health),
        Mount("/static", StaticFiles(directory=BASE_DIR / "static")),
    ],
    middleware=[Middleware(BaseHTTPMiddleware, dispatch=no_browser_cache)],
)
