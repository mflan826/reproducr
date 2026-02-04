"""
Check the robots.txt file for relevant sites,
considering redirects and the name of our agent
"""

import json
import requests
import urllib.robotparser as robotparser
from urllib.parse import urlparse

"""
robots_cache stores base_url: robots.txt content pairs
for later retrieval
"""
robots_cache = {}

"""
Configure headers for requests from a config file
with personal contact info
"""
HEADERS = {}
with open("config.json", "r") as f:
    HEADERS["User-Agent"] = json.load(f)["User-Agent"]


def get_robot_parser(base_url: str) -> robotparser.RobotFileParser:
    """
    Connect to the site and return the robots.txt file

    :param base_url: base url for the address
    :type base_url: str
    :return: RobotFileParser object for that base url
    :rtype: robotparser.RobotFileParser
    """
    if base_url not in robots_cache:
        rp = robotparser.RobotFileParser()
        rp.set_url(f"{base_url}/robots.txt")
        rp.read()
        robots_cache[base_url] = rp

    return robots_cache[base_url]


def is_allowed(target_url: str) -> bool:
    """
    Docstring for is_allowed

    :param target_url: url to validate
    :type target_url: str
    :return: link can be crawled = True
    :rtype: bool
    """
    base_url = f"{urlparse(target_url).scheme}://{urlparse(target_url).netloc}"

    return get_robot_parser(base_url=base_url).can_fetch(
        HEADERS["User-Agent"], target_url
    )


def resolve_and_check(url: str) -> tuple[str, bool]:
    """
    Follow redirects for a link, then
    validate that final link can be crawled per its robots.txt file

    :param url: Initial url to investigate
    :type url: str
    :return: link, can be crawled = True
    :rtype: tuple[str, bool]
    """

    response = requests.get(url=url, allow_redirects=True, stream=True, headers=HEADERS)
    final_url = response.url

    allowed = is_allowed(final_url)

    return final_url, allowed
