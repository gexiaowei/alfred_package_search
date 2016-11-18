#!/usr/bin/python

from __future__ import print_function
import sys
import urllib
import json
import requests
from workflow import Workflow

__author__ = "gexiaowei"
__version__ = "1.2"
__email__ = "gandxiaowei@gmail.com"
__status__ = "Development"

path = "/search"
NPM_URL = "https://www.npmjs.com"


def search(wf):
    args = wf.args
    domain = urllib.quote_plus(args[0].encode('utf-8'))
    keyword = urllib.quote_plus(args[1].encode('utf-8'))

    result = []

    if domain == "bower":
        result = bower(keyword)
    elif domain == "npm":
        result = npm(keyword)
    elif domain == "passport":
        result = passport(keyword)

    if len(result) == 0:
        wf.add_item('No Packages found.')
        wf.send_feedback()
        return 0

    for item in result:
        wf.add_item(item["name"],
                    subtitle=item["subtitle"],
                    valid=True,
                    arg=item["url"])
    wf.send_feedback()
    return 0


def bower(keywords):
    response = requests.request("GET",
                                'https://libraries.io/api/bower-search',
                                headers={}, params={"q": keywords})
    result = json.loads(response.text)
    return map(lambda item: dict(name=item["name"], subtitle=item["description"], url=item["homepage"] or item["repository_url"]), result)


def npm(keywords):
    key = "CD06z4gVeqSXRiDL2ZNK"
    response = requests.request("GET",
                                'https://ac.cnstrc.com/autocomplete/' + keywords,
                                headers={}, params={"query": keywords, "autocomplete_key": key, "callback": "callback"})
    result = json.loads(response.text.replace("typeof callback === 'function' && callback(", "").replace(");", ""))
    return map(lambda item: dict(name=item["value"], subtitle=item["data"]["description"], url=NPM_URL + item["data"]["url"]), result["sections"]["packages"])


def passport(keywords):
    response = requests.request('GET', 'http://passportjs.org/data.json')
    result = json.loads(response.text)
    before = filter(lambda item: item['label'].find(keywords) != -1, result)
    after = map(lambda item: dict(name=item['label'], subtitle=item['desc'], url=item['url']), before)
    return after

passport('token')

def main(wf):
    search(wf)


if __name__ == u"__main__":
    wf = Workflow()
    sys.exit(wf.run(main))
