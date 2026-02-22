"""
Pull data from pubmed
"""

import json
from pathlib import Path
import requests

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
RESULT_LIMIT = 10000  # limitation of the pubmed api


def get_config() -> tuple[str, str, str]:
    """
    Read values needed for polite api calls
    The api key is not required, but it allows for heavier optimization
    """
    with open(Path(Path(__file__).parent, "config.json"), "r") as f:
        data = json.load(f)
        api_key = None
        if "ncbi-api-key" in data:
            api_key = data["ncbi-api-key"]
        tool_name = data["tool_name"]
        email = data["email"]
    return api_key, tool_name, email


API_KEY, TOOL_NAME, EMAIL = get_config()


def get_search_context(query: str, database="pmc") -> tuple[str, str, str]:
    """
    Send a query to the PubMed api

    :param query: query string to send to the api
    :type query: str
    :param database: database parameter, defaults to pmc=pubmed central
    :return: webenv, querykey, and count
    :rtype: tuple[str, str, str]
    """
    params = {
        "db": database,
        "term": query,
        "retmode": "json",
        "usehistory": "y",
        "retmax": 0,
        "tool": TOOL_NAME,
        "email": EMAIL,
    }
    if API_KEY:
        params["api_key"] = API_KEY

    response = requests.get(f"{BASE_URL}/esearch.fcgi", params=params, timeout=30)
    response.raise_for_status()
    data: dict = response.json().get("esearchresult", {})

    return (
        data.get("webenv", None),
        data.get("querykey", None),
        int(data.get("count", 0)),
    )


def get_fetch_page(webenv: str, query_key: str, retstart: int, retmax: int):
    params = {
        "db": "pmc",
        "rettype": "full",
        "retmode": "xml",
        "webenv": webenv,
        "query_key": query_key,
        "retstart": retstart,
        "retmax": retmax,
        "tool": TOOL_NAME,
        "email": EMAIL,
    }
    if API_KEY:
        params["api_key"] = API_KEY
    response = requests.get(f"{BASE_URL}/efetch.fcgi", params=params, timeout=30)
    try:
        response.raise_for_status()
        return response.text
    except Exception:
        return None
