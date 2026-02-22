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


def parse_efetch(article) -> dict | None:
    """
    Extract semi-structured and structured data
    from a single article's lxml object
    Returns a dict or None if pmid is missing
    """
    pmid = article.findtext(".//article-id[@pub-id-type='pmid']")
    if not pmid:
        return None

    doi = article.findtext(".//article-id[@pub-id-type='doi']")

    article_type = article.get("article-type", "")

    title_el = article.find(".//article-title")
    article_title = "".join(title_el.itertext()) if title_el is not None else ""

    # Prefer epub date, fall back to ppub, then first available
    pub_date_el = (
        article.find(".//pub-date[@pub-type='epub']")
        or article.find(".//pub-date[@date-type='pub']")
        or article.find(".//pub-date")
    )
    pub_date = ""
    if pub_date_el is not None:
        parts = [
            pub_date_el.findtext("year", ""),
            pub_date_el.findtext("month", ""),
            pub_date_el.findtext("day", ""),
        ]
        pub_date = "-".join(p for p in parts if p)

    keywords = ["".join(kwd.itertext()) for kwd in article.findall(".//kwd")]

    funding_els = article.findall(".//funding-statement") or article.findall(".//funding-source")
    funding = ["".join(f.itertext()) for f in funding_els]

    ns = {"re": "http://exslt.org/regular-expressions"}

    data_availability = article.xpath(
        ".//title[re:test(normalize-space(.), '^data\\s*availability:?$', 'i')]/following-sibling::p",
        namespaces=ns,
    )

    code_availability = article.xpath(
        ".//title[re:test(normalize-space(.), '^code\\s*availability:?$', 'i')]/following-sibling::p",
        namespaces=ns,
    )

    return {
        "pmid": pmid,
        "doi": doi,
        "article_type": article_type,
        "article_title": article_title,
        "pub_date": pub_date,
        "keywords": keywords,
        "funding": funding,
        "data_availability": ["".join(da.itertext()) for da in data_availability],
        "code_availability": ["".join(ca.itertext()) for ca in code_availability],
    }


def parse_efetch_page(results: str) -> list[dict]:
    output = []

    tree = etree.fromstring(results)

    for article in tree.xpath("//*[local-name()='article']"):

        record = parse_efetch(article)
        if record:
            output.append(record)

    return output
