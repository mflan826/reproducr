"""
Collection of webpage scrapers
"""

from pathlib import (
    Path,
    PurePosixPath,
)
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from robots import (
    resolve_and_check,
    HEADERS,
)

scraper_data_path = Path(Path(__file__).parent, "scraper_data")
xml_data_path = Path(scraper_data_path, "xml")
bib_data_path = Path(scraper_data_path, "bib")

xml_data_path.mkdir(parents=True, exist_ok=True)
bib_data_path.mkdir(parents=True, exist_ok=True)


def build_xml_file_name(url: str) -> Path:
    """

    :param url: url of the xml file to download
    :type url: str
    :return: transformed url into an xml file name
    :rtype: str
    """
    raw_path = urlparse(url).path
    return Path(xml_data_path, raw_path.lstrip("/").replace("/", "_") + ".xml")


def build_bibtex_file_name(url: str) -> Path:
    """

    :param url: url of the bibtex file to download
    :type url: str
    :return: full path of location of the bibtex file to write.
    :rtype: Path
    """
    return Path(bib_data_path, PurePosixPath(urlparse(url).path).name + ".bib")


def download(url: str, output_path: str) -> None:
    """
    Download a url to an output path

    :param url: url of the file content to download
    :type url: str
    :param output_path: local file path to save
    :type output_path: str
    """

    with requests.get(url=url, stream=True, timeout=9) as r:
        r.raise_for_status()
        with open(output_path, "wb+") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    print(f"Downloaded {url} to {output_path}")


def jmir_article(url: str):
    """
    Scrape relevant information from a jmir page

    :param url: url of the article
    :type url: str
    """
    final_url, allowed = resolve_and_check(url=url)
    if not allowed:
        return
    page = requests.get(final_url, headers=HEADERS)
    page.raise_for_status()
    soup = BeautifulSoup(page.content, "html.parser")

    xml_links = soup.find_all("a", attrs={"aria-label": "Download XML"})
    for xml_link in xml_links:
        xml_url, xml_allowed = resolve_and_check(url=xml_link.get("href"))
        if xml_allowed:
            download(xml_url, build_xml_file_name(url))

    bibtex_links = soup.find_all("a", attrs={"aria-label": "Export metadata in BibTeX"})
    for bibtex_link in bibtex_links:
        bibtex_url, bibtex_allowed = resolve_and_check(url=bibtex_link.get("href"))
        if bibtex_allowed:
            download(bibtex_url, build_bibtex_file_name(url))
