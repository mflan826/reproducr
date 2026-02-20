"""
Parse raw data output
"""

from pathlib import Path

from lxml import etree


def parse_search_page(results: dict) -> list[dict]:
    """
    Loop through api results
    Extract data from the esummary into a dict
    Add extracted data to a list
    return that list of dict
    """
    output = []
    result_pmids = results.get("uids", [])
    # TODO introduce parallelism here using function `parse_pubmed_esummary`
    # probably want to use threads to avoid copying a potentially large dictionary?
    for pmid in result_pmids:
        result = {}
        result["pmid"] = pmid
        result["sortdate"] = results[pmid].get("sortdate", "")
        output.append(result)
    return output


def parse_pubmed_esummary(results: dict, pmid: str) -> dict:
    """
    Parse the results for one specific pmid
    From the pubmed esummary return
    Return the dictionary of needed data
    """
    output = {}
    output["pmid"] = pmid
    output["sortdate"] = results[pmid].get("sortdate", "")
    # TODO extract the relevant structured data

    return output


def parse_efetch(article) -> tuple[str, str]:
    """
    Extract semi-structured and structured data
    from a single article's lxml object
    Return (pmid, doi, [data availability])
    """
    # Require the pmid for this article
    try:
        pmid = article.findtext(".//article-id[@pub-id-type='pmid']")
    except:
        # if doi is missing, then continue to the next record
        return None

    # get the doi
    doi = article.findtext(".//article-id[@pub-id-type='doi']")

    # Finds the 'p' tag that follows a 'title' containing 'Data Availability'
    data_availability = article.xpath(
        ".//title[re:test(normalize-space(.), '^data\\s*availability:?$', 'i')]/following-sibling::p",
        namespaces={"re": "http://exslt.org/regular-expressions"},
    )

    return (pmid, doi, ["".join(da.itertext()) for da in data_availability])


def parse_efetch_page(results: str) -> list[dict]:
    output = []

    tree = etree.fromstring(results)

    for article in tree.xpath("//*[local-name()='article']"):

        record = parse_efetch(article)
        if record:
            output.append(record)

    return output


def parse_jmir_xml_file(xml_file_path: str | Path) -> tuple[str, list[str]]:
    """
    Extract data from xml file

    :param xml_file_path: Path to xml file with raw data
    :type xml_file_path: str | Path
    :return: tuple of the doi and a list of strings describing data availability.
    :rtype: tuple[ str, list[str]]
    """
    tree = etree.parse(xml_file_path)

    # Require the doi for this article
    try:
        doi = tree.xpath("//article-id[@pub-id-type='doi']/text()")[0]
    except:
        # if doi is missing, then pass an empty tuple
        return (None, [])

    data_results = []

    # Finds the 'p' tag that follows a 'title' containing 'Data Availability'
    data_availability = tree.xpath(
        "//title[re:test(normalize-space(.), '^data\\s*availability:?$', 'i')]/following-sibling::p",
        namespaces={"re": "http://exslt.org/regular-expressions"},
    )
    for result in data_availability:
        data_results.append(result.text)

    return doi, data_results
