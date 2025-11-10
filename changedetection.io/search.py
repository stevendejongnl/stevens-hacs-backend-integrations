import requests


def search(base_url: str, api_key: str, query: str, partial: bool = False, tag_name: None | str = None) -> dict:
    params = {"q": query, "partial": str(partial).lower()}
    if tag_name is not None:
        params["tag"] = tag_name

    url = f"{base_url}/api/v1/search"
    response = requests.get(
        url,
        headers={"x-api-key": api_key},
        params=params
    )

    if response.status_code == 200:
        return response.json()

    return {}
