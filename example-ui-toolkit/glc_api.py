"""Small client for the Graylog Cloud API (https://api.graylog.cloud/openapi.json).

Auth flow:
  POST /v1/auth/_token    {"username", "password"}  -> envelope.data.{access_token, refresh_token}
  POST /v1/auth/_refresh  {"refresh_token"}         -> envelope.data.{access_token, ...}
  Protected calls send   Authorization: Bearer <access_token>
"""

import random
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import cast

import httpx

Tenant = dict[str, object]

HIDDEN_FIELDS = {
    "graylog_trial_license_base64",
    "db_hosts",
    "db_username",
    "db_name",
    "db_replicaset_name",
    "os_master_user_name",
    "okta_api_user_email",
    "okta_application_client_id",
}
HIDDEN_MARKERS = ("token", "password", "secret")


def is_hidden_field(name: str) -> bool:
    return name in HIDDEN_FIELDS or any(marker in name for marker in HIDDEN_MARKERS)


def _public(tenant: Tenant) -> Tenant:
    return {k: v for k, v in tenant.items() if not is_hidden_field(k)}


@dataclass(frozen=True)
class TenantFetch:
    """The tenant list, plus whether this call went to the API or was served from the cache."""

    tenants: list[Tenant]
    live: bool  # True: fetched from the API on this call. False: served from the in-memory cache.
    age: float  # Seconds since the API answered.
    api_seconds: float  # How long that API answer took (login or token refresh included).


class GlcApiError(Exception):
    pass


def _json(response: httpx.Response) -> object:
    return cast(object, response.json())


def _error_detail(response: httpx.Response) -> str:
    try:
        body = _json(response)
    except ValueError:
        return response.text[:200] or response.reason_phrase
    if isinstance(body, dict):
        body = cast(dict[str, object], body)
        return str(body.get("detail") or body.get("message") or body)
    return str(body)


def _unwrap(response: httpx.Response) -> object:
    """Return `data` from the API's {status, message, data} envelope."""
    if response.status_code >= 400:
        request = response.request
        detail = _error_detail(response)
        raise GlcApiError(f"{request.method} {request.url.path} failed ({response.status_code}): {detail}")
    body = _json(response)
    if isinstance(body, dict):
        envelope = cast(dict[str, object], body)
        return envelope.get("data", envelope)
    return body


def _tenant_rows(data: object) -> list[Tenant]:
    shape = type(data).__name__
    if isinstance(data, list):
        return cast(list[Tenant], data)
    if isinstance(data, dict):
        for value in cast(dict[str, object], data).values():
            if isinstance(value, list):
                return cast(list[Tenant], value)
    raise GlcApiError(f"Unexpected tenant list shape: {shape}")


class GlcClient:
    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        environment: str,
        cache_ttl: float = 60,
        timeout: float = 20,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ):
        self._http: httpx.Client = httpx.Client(base_url=base_url, timeout=timeout)
        self._username: str = username
        self._password: str = password
        self.environment: str = environment
        self._cache_ttl: float = cache_ttl
        self._clock: Callable[[], float] = clock
        self._sleep: Callable[[float], None] = sleep
        self._lock: threading.Lock = threading.Lock()
        self._access_token: str | None = None
        self._refresh_token: str | None = None
        self._cache: list[Tenant] | None = None
        self._cache_at: float = 0.0
        self._cache_took: float = 0.0

    # --- auth -------------------------------------------------------------

    def _store_tokens(self, data: object) -> None:
        fields = cast(dict[str, object], data) if isinstance(data, dict) else {}
        access = fields.get("access_token")
        if not isinstance(access, str) or not access:
            raise GlcApiError(f"Auth response has no access_token (got: {data!r:.200})")
        self._access_token = access
        refresh = fields.get("refresh_token")
        if isinstance(refresh, str):
            self._refresh_token = refresh

    def _login(self) -> None:
        response = self._http.post("/v1/auth/_token", json={"username": self._username, "password": self._password})
        self._store_tokens(_unwrap(response))

    def _refresh(self) -> bool:
        if not self._refresh_token:
            return False
        response = self._http.post("/v1/auth/_refresh", json={"refresh_token": self._refresh_token})
        if response.status_code >= 400:
            return False
        self._store_tokens(_unwrap(response))
        return True

    def _get(self, path: str, params: dict[str, str]) -> object:
        if not self._access_token:
            self._login()
        response = self._http.get(path, params=params, headers=self._auth_header())
        if response.status_code == 401:
            if not self._refresh():
                self._login()
            response = self._http.get(path, params=params, headers=self._auth_header())
        return _unwrap(response)

    def _auth_header(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._access_token}"}

    # --- tenants ----------------------------------------------------------

    def fetch_tenants(self) -> TenantFetch:
        """All tenants with every public field, cached for `cache_ttl` seconds."""
        with self._lock:
            started = self._clock()
            live = self._cache is None or started - self._cache_at >= self._cache_ttl
            if live:
                if self._cache_ttl == 0:
                    self._sleep(random.uniform(0.25, 0.7))
                data = self._get(
                    "/v1/tenants/_details",
                    {"tenant_environment": self.environment, "fields": "*"},
                )
                self._cache = [_public(t) for t in _tenant_rows(data)]
                self._cache_at = self._clock()
                self._cache_took = self._cache_at - started
            tenants = cast(list[Tenant], self._cache)
            return TenantFetch(tenants, live, self._clock() - self._cache_at, self._cache_took)
