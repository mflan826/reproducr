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

    article = results.get("result", {}).get(pmid)
    if not article:
        return {}

    # Authors
    authors = article.get("authors", [])
    author_names = [a.get("name", "") for a in authors if "name" in a]

    # Article IDs
    doi = ""
    pmcid = ""
    pubmed_id = ""

    for aid in article.get("articleids", []):
        if aid.get("idtype") == "doi":
            doi = aid.get("value", "")
        if aid.get("idtype") == "pmcid":
            pmcid = aid.get("value", "")
        if aid.get("idtype") == "pmid":
            pubmed_id = aid.get("value", "")

    # Dates
    pubdate = article.get("pubdate", "")
    epubdate = article.get("epubdate", "")
    printpubdate = article.get("printpubdate", "")
    sortdate = article.get("sortdate", "")
    pmc_live_date = article.get("pmclivedate", "")

    resolved_date = epubdate or pubdate or printpubdate or sortdate

    return {
        "uid": pmid,                 # the key used in esummary
        "pubmed_id": pubmed_id,      # the true PMID from articleids
        "title": article.get("title", ""),
        "journal": article.get("fulljournalname", ""),
        "journal_abbrev": article.get("source", ""),
        "pubdate": pubdate,
        "epubdate": epubdate,
        "printpubdate": printpubdate,
        "sortdate": sortdate,
        "pmc_live_date": pmc_live_date,
        "resolved_pubdate": resolved_date,
        "volume": article.get("volume", ""),
        "issue": article.get("issue", ""),
        "pages": article.get("pages", ""),
        "doi": doi,
        "pmcid": pmcid,
        "authors": "; ".join(author_names),
        "author_count": len(author_names),
        "publication_types": "; ".join(article.get("pubtype", [])),
        "language": "; ".join(article.get("lang", [])),
    }


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
