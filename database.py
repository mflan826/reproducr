"""
Build persistent storage for the extracted data

Currently just persistent storage in a csv for easy sharing.

Enforcing the "data model" currently by
programmatically writing to csv files
"""

import csv
from pathlib import Path

"""
Define paths to the set of csv files
"""
output_dir = Path(Path(__file__).parent, "output")
data_available_file_path = Path(output_dir, "data-available.csv")
keyword_file_path = Path(output_dir, "keyword.csv")

"""
Make the files and directories is they don't exist
"""
output_dir.mkdir(parents=True, exist_ok=True)
data_available_file_path.touch(exist_ok=True)
keyword_file_path.touch(exist_ok=True)

"""
Common parameters for working with this set of csv files
"""
csv_params = {
    "delimiter": ",",
    "quotechar": '"',
    "quoting": csv.QUOTE_ALL,
}


def write_data_available(doi: str, value: str) -> None:
    """
    Write output about availability to a csv file

    :param doi: DOI of the paper
    :type doi: str
    :param value: Text pulled from the relevant xml
    :type value: str
    """
    with open(data_available_file_path, "a") as f:
        csv_writer = csv.writer(f, **csv_params)
        csv_writer.writerow([doi, value])


def write_keyword(doi: str, keyword: str) -> None:
    """
    Write output from keyworkds to a csv file

    :param doi: DOI of the paper
    :type doi: str
    :param value: one keyword pulled from the paper
    :type value: str
    """
    with open(keyword_file_path, "a") as f:
        csv_writer = csv.writer(f, **csv_params)
        csv_writer.writerow([doi, keyword])
