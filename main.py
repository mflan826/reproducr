from database import write_data_detailed, create_connection, close_connection
from parser import parse_efetch_page
from pubmed import (
    get_search_context,
    get_fetch_page,
    RESULT_LIMIT,
)


def load_xml_data(webenv, query_key, chunksize: int, count: int, limit=10000) -> None:
    """
    Iterate through the results of a query and
    Load all of those results to the database
    """
    start = 0

    # set the max retrieval to not go over the max results of the api
    retmax = min(chunksize, limit - start)

    db_connection = create_connection() # SQL Alchemy handler

    results = get_fetch_page(
        webenv=webenv, query_key=query_key, retstart=start, retmax=retmax
    )

    while results and start < limit:

        data = parse_efetch_page(results=results)
        write_data_detailed(data, db_connection)

        start += chunksize

        # set the max retrieval to not go over the max results of the api
        retmax = min(chunksize, count, limit - start)

        results = get_fetch_page(
            webenv=webenv, query_key=query_key, retstart=start, retmax=retmax
        )

    close_connection(db_connection)


def main():
    queries = ["retrospective AND informatics AND (secondary OR ehr) AND 2025[pdat] AND open access[filter]"]

    for query in queries:
        webenv, query_key, count = get_search_context(query=query)

        if count > RESULT_LIMIT:
            print(f"count > limit | {count} > {RESULT_LIMIT}\n")
            print("Results will be truncated")

        load_xml_data(webenv, query_key, chunksize=20, count=count, limit=RESULT_LIMIT)


if __name__ == "__main__":
    main()
