"""
Parse raw data output
"""

from lxml import etree


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
