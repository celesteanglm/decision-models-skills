"""Environment-only authentication and bounded standard-library HTTP transport."""
import json
import urllib.error
import urllib.request
import socket
from .contracts import DecisionError


def http_transport(endpoint, payload, api_key, timeout=20):
    request = urllib.request.Request(endpoint, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json",
                 "Accept": "application/json", "User-Agent": "decision-models-skills/0.1.0"}, method="POST")
    # Refuse redirects so credentials never follow an unexpected host.
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None
    try:
        with urllib.request.build_opener(NoRedirect).open(request, timeout=timeout) as response:
            body = response.read(4_000_001)
            if len(body) > 4_000_000:
                raise DecisionError("invalid_response", "response exceeds 4 MB")
            try:
                value = json.loads(body)
            except (ValueError, UnicodeError) as exc:
                raise DecisionError("invalid_response", "provider returned non-JSON content") from exc
            if not isinstance(value, dict):
                raise DecisionError("invalid_response", "provider returned a non-object")
            return value
    except urllib.error.HTTPError as exc:
        code = {400: "invalid_request", 401: "authentication", 402: "insufficient_credits",
                403: "permission", 404: "endpoint_unavailable", 413: "invalid_request",
                422: "invalid_request", 429: "rate_limited"}.get(exc.code, "upstream_failure")
        raise DecisionError(code, f"provider HTTP {exc.code}", status=exc.code,
                            retryable=exc.code == 429) from exc
    except (TimeoutError, socket.timeout) as exc:
        raise DecisionError("timeout", "provider request timed out; charge status is unknown") from exc
    except urllib.error.URLError as exc:
        code = "timeout" if isinstance(exc.reason, (TimeoutError, socket.timeout)) else "network"
        raise DecisionError(code, "provider connection failed; charge status may be unknown") from exc

