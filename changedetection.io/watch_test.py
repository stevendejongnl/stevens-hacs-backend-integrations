import os
from uuid import UUID

import pytest

from watch import watch_uuid, watch_uuid_history_timestamp


@pytest.mark.vcr()
def test_watch_uuid():
    base_url = os.environ.get("CHANGEDETECTION_BASE_URL", "https://changedetection.io")
    api_key = os.environ.get("CHANGEDETECTION_API_KEY", "test-api-key")

    uuid = UUID("02370013-3bac-499e-acd5-958f57c51aeb")  # Frikandel Broodje UUID

    response = watch_uuid(
        base_url=base_url,
        api_key=api_key,
        uuid=uuid,
    )

    assert 'Frikandel Broodje' == response.get('title')

@pytest.mark.vcr()
def test_watch_uuid_not_found():
    base_url = os.environ.get("CHANGEDETECTION_BASE_URL", "https://changedetection.io")
    api_key = os.environ.get("CHANGEDETECTION_API_KEY", "test-api-key")

    uuid = UUID("00000000-0000-0000-0000-000000000000")  # Non-existent UUID

    response = watch_uuid(
        base_url=base_url,
        api_key=api_key,
        uuid=uuid,
    )

    assert response == {}


@pytest.mark.vcr()
def test_watch_uuid_history_timestamp():
    base_url = os.environ.get("CHANGEDETECTION_BASE_URL", "https://changedetection.io")
    api_key = os.environ.get("CHANGEDETECTION_API_KEY", "test-api-key")

    uuid = UUID("02370013-3bac-499e-acd5-958f57c51aeb")  # Frikandel Broodje UUID
    timestamp = "1762678195"  # last_changed

    response = watch_uuid_history_timestamp(
        base_url=base_url,
        api_key=api_key,
        uuid=uuid,
        timestamp=timestamp,
    )

    assert '1762678195' in response.get('timestamp')
    assert '€21,99\n€20,67' in response.get('content')
