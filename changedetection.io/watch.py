from uuid import UUID

import requests


def watch_uuid(base_url: str, api_key: str, uuid: UUID):
    url = f"{base_url}/api/v1/watch/{uuid}"
    response = requests.get(
        url,
        headers={"x-api-key": api_key},
    )

    if response.status_code == 200:
        return response.json()

    return {}


def watch_uuid_history_timestamp(
        base_url: str,
        api_key: str,
        uuid: UUID,
        timestamp: str,
):
    url = f"{base_url}/api/v1/watch/{uuid}/history/{timestamp}"
    response = requests.get(
        url,
        headers={"x-api-key": api_key},
    )

    if response.status_code == 200:
        return {
            "timestamp": timestamp,
            "content": response.text,
        }

    return {}
