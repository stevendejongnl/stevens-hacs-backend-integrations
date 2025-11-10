import os
import secrets
from urllib.parse import urlparse, urlunparse, ParseResult

import pytest
from _pytest.fixtures import FixtureRequest


class RedactError(Exception):
    pass


def default_headers_to_filter() -> list[str]:
    return [
        "x-api-key",
        "CF-RAY",
        "Nel",
        "Report-To",
        "Server",
        "cf-cache-status",
    ]


def determine_env_base_url() -> str | None:
    env_base = os.environ.get("CHANGEDETECTION_BASE_URL")
    if env_base:
        try:
            parsed_env = urlparse(env_base)
            return parsed_env.netloc
        except Exception:
            return None
    return None


def before_record_response(response: dict | None) -> dict | None:
    if response is None:
        return None
    headers = response.get("headers")
    if not headers:
        return response

    headers_to_filter = default_headers_to_filter()
    lower_to_keep = {h.lower() for h in headers_to_filter}

    new_headers = {}
    for name, values in headers.items():
        if name.lower() in lower_to_keep:
            new_headers[name] = ["FILTERED"]
        else:
            new_headers[name] = values

    response["headers"] = new_headers
    return response


def absolute_uri(uri: str) -> bool:
    if not uri:
        return False
    return uri.startswith("http://") or uri.startswith("https://")


def get_random_netloc() -> str:
    token = secrets.token_hex(6)
    return f"{token}.redacted.local"


def rebuild_url_with_new_netloc(request: FixtureRequest, parsed: ParseResult, random_netloc: str) -> FixtureRequest:
    new_parsed = parsed._replace(netloc=random_netloc)
    new_uri = urlunparse(new_parsed)

    request.uri = new_uri

    return request


def update_host(request: FixtureRequest, random_netloc: str) -> FixtureRequest:
    if hasattr(request, "host"):
        try:
            # Some Request implementations (e.g. vcr.Request) expose `host` as a
            # read-only property derived from `uri`. Attempting to set it will
            # raise AttributeError — treat this as a best-effort operation.
            request.host = random_netloc
        except (RedactError, AttributeError):
            # Best-effort only; if host can't be set, skip it.
            pass

    return request


def update_host_header(request: FixtureRequest, random_netloc: str) -> FixtureRequest:
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
    except RedactError:
        # Best-effort only
        pass

    return request


def randomize_netloc(request: FixtureRequest, parsed: ParseResult, env_netloc: str) -> FixtureRequest:
    if env_netloc and parsed.netloc == env_netloc:
        random_netloc = get_random_netloc()

        request = rebuild_url_with_new_netloc(request, parsed, random_netloc)
        request = update_host(request, random_netloc)
        request = update_host_header(request, random_netloc)

    return request


def before_record_request(request: FixtureRequest, env_netloc: str | None) -> FixtureRequest:
    uri = getattr(request, "uri", None)
    absolute = absolute_uri(uri)
    if not absolute:
        return request

    try:
        parsed = urlparse(uri)
    except RedactError:
        return request

    return randomize_netloc(
        request=request,
        parsed=parsed,
        env_netloc=env_netloc,
    )


@pytest.fixture(scope="session")
def vcr_config():
    headers_to_filter = default_headers_to_filter()
    env_netloc = determine_env_base_url()
    before_record_response_func = before_record_response
    before_record_request_func = lambda req: before_record_request(req, env_netloc)

    return {
        "record_mode": "once",
        "filter_headers": headers_to_filter,
        "before_record_response": before_record_response_func,
        "before_record_request": before_record_request_func,

        # Match ignoring host/port so playback works even if host was anonymized
        # during recording. Keep path and query as matching keys.
        "match_on": ("method", "scheme", "path", "query"),
    }
