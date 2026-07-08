import requests

STAC_SEARCH_URL = "https://catalogue.dataspace.copernicus.eu/stac/search"


def search_uae_sentinel():

    payload = {
        "collections": ["sentinel-2-l2a"],
        "bbox": [51.4, 22.5, 56.7, 26.5],   # UAE Bounding Box
        "limit": 20
    }

    response = requests.post(
        STAC_SEARCH_URL,
        json=payload
    )

    response.raise_for_status()

    return response.json()