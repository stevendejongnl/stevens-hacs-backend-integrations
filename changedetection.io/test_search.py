import os

import pytest

from search import search


@pytest.mark.vcr()
def test_search_with_basic_query():
    base_url = os.environ.get("CHANGEDETECTION_BASE_URL", "https://changedetection.io")
    api_key = os.environ.get("CHANGEDETECTION_API_KEY", "test-api-key")

    query = "snacks"

    response = search(
        base_url=base_url,
        api_key=api_key,
        query=query,
    )

    assert {} == response


@pytest.mark.vcr()
def test_search_with_partial_match():
    base_url = os.environ.get("CHANGEDETECTION_BASE_URL", "https://changedetection.io")
    api_key = os.environ.get("CHANGEDETECTION_API_KEY", "test-api-key")

    query = "snacks"
    partial = True

    response = search(
        base_url=base_url,
        api_key=api_key,
        query=query,
        partial=partial,
    )

    assert 'Frikandel Broodje' in [item['title'] for item in response.values()]
    assert 'Paprika Chips' in [item['title'] for item in response.values()]
