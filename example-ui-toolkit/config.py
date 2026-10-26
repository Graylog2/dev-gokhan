"""Runtime configuration.

API credentials are set directly below in GLC_USERNAME and GLC_PASSWORD.
"""

import os

GLC_API_URL = os.environ.get("GLC_API_URL", "https://api.graylog.cloud")
GLC_USERNAME = ""
GLC_PASSWORD = ""

TENANT_ENVIRONMENT = os.environ.get("GLC_TENANT_ENVIRONMENT", "prod")
CACHE_TTL_SECONDS = int(os.environ.get("GLC_CACHE_TTL_SECONDS", "20"))
HTTP_TIMEOUT_SECONDS = float(os.environ.get("GLC_HTTP_TIMEOUT_SECONDS", "20"))

DEFAULT_COLUMNS = [
    "tenant_name",
    "tenant_region",
    "tenant_type",
    "status",
    "license_size",
    "graylog_application_image",
]


def credentials_configured() -> bool:
    return all((GLC_USERNAME, GLC_PASSWORD))
