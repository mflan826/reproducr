from database import write_data
from parser import (
    parse_search_page,
    parse_efetch_page,
)
from pubmed import (
    get_search_context,
    get_search_page,
    get_fetch_page,
    RESULT_LIMIT,
)


def load_structured_data(
    webenv, query_key, chunksize: int, count: int, limit=10000
) -> None:
    """
    Iterate through the results of a query and
    Load all of those results to the database
    """
    start = 0
    n_results = chunksize

    # set the max retrieval to not go over the max results of the api
    retmax = min(chunksize, count, limit - start)

    results = get_search_page(
        webenv=webenv, query_key=query_key, retstart=start, retmax=retmax
    )
    n_results = len(results)

    while n_results > 0 and start < limit:

        data = parse_search_page(results=results)
        # print(data)
        write_data(data)  # TODO tailor this to write structured data

        start += chunksize

        # set the max retrieval to not go over the max results of the api
        retmax = min(chunksize, count, limit - start)

        results = get_search_page(
            webenv=webenv, query_key=query_key, retstart=start, retmax=retmax
        )
        n_results = len(results)


def load_xml_data(webenv, query_key, chunksize: int, count: int, limit=10000) -> None:
    """
    Iterate through the results of a query and
    Load all of those results to the database
    """
    start = 0
    n_results = chunksize

    # set the max retrieval to not go over the max results of the api
    retmax = min(chunksize, limit - start)

    results = get_fetch_page(
        webenv=webenv, query_key=query_key, retstart=start, retmax=retmax
    )

    while results and start < limit:

        data = parse_efetch_page(results=results)
        # print(data)
        write_data(data)  # TODO tailor this to write xml results

        start += chunksize

        # set the max retrieval to not go over the max results of the api
        retmax = min(chunksize, count, limit - start)

        results = get_fetch_page(
            webenv=webenv, query_key=query_key, retstart=start, retmax=retmax
        )


def main():
    queries = ["informatics AND open access[filter]"]

    for query in queries:
        webenv, query_key, count = get_search_context(query=query)

        if count > RESULT_LIMIT:
            print(f"count > limit | {count} > {RESULT_LIMIT}\n")
            print("Results will be truncated")

        load_structured_data(
            webenv, query_key, chunksize=350, count=count, limit=RESULT_LIMIT
        )

        load_xml_data(webenv, query_key, chunksize=20, count=count, limit=RESULT_LIMIT)


if __name__ == "__main__":
    main()
