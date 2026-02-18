from database import write_data
from parser import parse_search_page
from pubmed import (
    get_search_context,
    get_search_page,
)


def main():
    queries = ["informatics AND open access[filter]"]

    limit = 10000 # limitation of the pubmed api
    chunksize = 350  # max functional batch size

    for query in queries:
        webenv, querykey, count = get_search_context(query=query)

        if int(count) > limit:
            print(f"count > limit | {count} > {limit}\n")
            print("Results will be truncated")

        start = 0
        n_results = chunksize
        while n_results > 0 and start < limit:
            # set the max retrieval to not go over the max results of the api
            retmax = min(chunksize, limit - start)

            results = get_search_page(
                webenv=webenv, query_key=querykey, retstart=start, retmax=retmax
            )
            n_results = len(results)

            data = parse_search_page(results=results)
            print(data)
            write_data(data)

            start += chunksize


if __name__ == "__main__":
    main()
