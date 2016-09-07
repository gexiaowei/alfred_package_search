#!/usr/bin/python

from __future__ import print_function
import sys
import urllib
import requests
from bs4 import BeautifulSoup
from workflow import Workflow

__author__ = "gexiaowei"
__version__ = "1.0"
__email__ = "gandxiaowei@gmail.com"
__status__ = "Development"

URL = "https://www.npmjs.com"
path = "/search"


def npm(wf):
    args = wf.args
    query = urllib.quote_plus(args[0].encode('utf-8'))
    response = requests.request("GET", URL + path, headers={}, params={"q": query, "page": 1})
    soup = BeautifulSoup(response.text, "html.parser")
    elements = soup.find_all("div", class_='package-details')

    if len(elements) == 0:
        wf.add_item('No torrents found with this query found.')
        wf.send_feedback()
        return 0

    for item in elements:
        name_element = item.find("a", class_="name")
        name = name_element.get_text()
        url = URL + name_element["href"]
        author = item.find("a", class_="author").get_text()
        description = item.find("p", class_="description").get_text()
        stars = item.find("span", class_="stars").get_text()
        version = item.find("span", class_="version").get_text()
        wf.add_item(name + '(by ' + author + ')',
                    subtitle=(description + ' version:' + version),
                    valid=True,
                    arg=url)
    wf.send_feedback()
    return 0


def main(wf):
    npm(wf)


if __name__ == u"__main__":
    wf = Workflow()
    sys.exit(wf.run(main))
