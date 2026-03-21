"""Constants for Speedtest Tracker."""
from __future__ import annotations

DOMAIN = "speedtest_tracker"
PLATFORMS = ["sensor", "binary_sensor", "button"]

CONF_BASE_URL = "base_url"
CONF_BEARER_TOKEN = "bearer_token"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_TIMEOUT = "timeout"
CONF_VERIFY_SSL = "verify_ssl"
CONF_WEBHOOK_ID = "webhook_id"

DEFAULT_SCAN_INTERVAL = 300
DEFAULT_TIMEOUT = 20
RUNNING_RETRY_SECONDS = 10

LATEST_PATH = "/api/v1/results/latest"
STATS_PATH = "/api/v1/stats"
RUN_PATH = "/api/v1/speedtests/run"

ATTR_BYTES_PER_SECOND = "bytes_per_second"
ATTR_DOWNLOAD_BYTES = "download_bytes"
ATTR_UPLOAD_BYTES = "upload_bytes"
ATTR_LAST_TEST_TIME = "last_test_time"
ATTR_RESULT_URL = "result_url"
ATTR_WEBHOOK_URL = "webhook_url"
