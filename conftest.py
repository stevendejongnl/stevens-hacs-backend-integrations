import os
import secrets
from urllib.parse import urlparse, urlunparse

import pytest


@pytest.fixture(scope="session")
def vcr_config():
    headers_to_filter = [
        "x-api-key",
        "CF-RAY",
        "Nel",
        "Report-To",
        "Server",
        "cf-cache-status",
    ]

    # Determine the env base URL (if set) so we can detect requests that
    # originated from that configuration and obfuscate their hostname.
    env_base = os.environ.get("CHANGEDETECTION_BASE_URL")
    env_netloc = None
    if env_base:
        try:
            parsed_env = urlparse(env_base)
            env_netloc = parsed_env.netloc
        except Exception:
            env_netloc = None

    def _before_record_response(response):
        if response is None:
            return None
        headers = response.get("headers")
        if not headers:
            return response

        lower_to_keep = {h.lower() for h in headers_to_filter}

        new_headers = {}
        for name, values in headers.items():
            if name.lower() in lower_to_keep:
                new_headers[name] = ["FILTERED"]
            else:
                new_headers[name] = values

        response["headers"] = new_headers
        return response

    def _before_record_request(request):
        """Obfuscate the request URI host when the request originates from
        the configured environment base URL. Keep path and query intact.

        This replaces the netloc (host[:port]) with a random token so the
        cassette doesn't leak the real host. The Host header and
        request.host (if present) are also updated.
        """
        # Only operate on absolute URIs with scheme
        uri = getattr(request, "uri", None)
        if not uri or not (uri.startswith("http://") or uri.startswith("https://")):
            return request

        try:
            parsed = urlparse(uri)
        except Exception:
            return request

        # If an env base is configured and the request host matches it,
        # replace the netloc with a randomized placeholder but keep path/query
        if env_netloc and parsed.netloc == env_netloc:
            # Create a short random token; keep it DNS-friendly
            token = secrets.token_hex(6)
            random_netloc = f"{token}.redacted.local"

            # Rebuild the URL with the new netloc
            new_parsed = parsed._replace(netloc=random_netloc)
            new_uri = urlunparse(new_parsed)

            request.uri = new_uri

            # Update request.host if present
            if hasattr(request, "host"):
                try:
                    request.host = random_netloc
                except Exception:
                    pass

            # Update Host header if present (case-insensitive)
            try:
                headers = getattr(request, "headers", None)
                if headers is not None:
                    # Find actual Host key name (preserve case) if present
                    host_key = None
                    for k in list(headers.keys()):
                        if k.lower() == "host":
                            host_key = k
                            break
                    if host_key:
                        headers[host_key] = random_netloc
                    else:
                        headers["Host"] = random_netloc
                    request.headers = headers
            except Exception:
                # Best-effort only
                pass

        return request

    return {
        "record_mode": "once",
        "filter_headers": headers_to_filter,
        "before_record_response": _before_record_response,
        "before_record_request": _before_record_request,
        # Match ignoring host/port so playback works even if host was anonymized
        # during recording. Keep path and query as matching keys.
        "match_on": ("method", "scheme", "path", "query"),
    }
