import os
import requests
from dotenv import load_dotenv

load_dotenv()

AUTH_URL = (
    "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/"
    "protocol/openid-connect/token"
)

CATALOG_URL = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"


def get_access_token():
    data = {
        "client_id": "cdse-public",
        "username": os.getenv("COPERNICUS_USERNAME"),
        "password": os.getenv("COPERNICUS_PASSWORD"),
        "grant_type": "password",
    }

    response = requests.post(AUTH_URL, data=data)
    response.raise_for_status()

    return response.json()["access_token"]


def search_sentinel_products(top=10):

    filter_query = (
        "Collection/Name eq 'SENTINEL-2' "
        "and contains(Name,'MSIL2A')"
    )

    params = {
        "$top": top,
        "$filter": filter_query,
        "$orderby": "ContentDate/Start desc",
    }

    response = requests.get(
        CATALOG_URL,
        params=params,
    )

    response.raise_for_status()

    return response.json()


def search_uae_products(top=20):

    # Approximate UAE bounding box
    bbox = "51.4,22.5,56.7,26.5"

    filter_query = (
        "Collection/Name eq 'SENTINEL-2' "
        "and contains(Name,'MSIL2A')"
    )

    params = {
        "$top": top,
        "$filter": filter_query,
        "$orderby": "ContentDate/Start desc",
        "$expand": "Attributes",
    }

    response = requests.get(
        CATALOG_URL,
        params=params,
    )

    response.raise_for_status()

    return response.json()