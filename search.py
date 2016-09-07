#!/usr/bin/python

from __future__ import print_function
import sys
import urllib
import json
import requests
from workflow import Workflow

__author__ = "gexiaowei"
__version__ = "1.1"
__email__ = "gandxiaowei@gmail.com"
__status__ = "Development"

URL = "https://www.npmjs.com"
KEY = "CD06z4gVeqSXRiDL2ZNK"
path = "/search"


def npm(wf):
    args = wf.args
    query = urllib.quote_plus(args[0].encode('utf-8'))
    response = requests.request("GET",
                                'https://ac.cnstrc.com/autocomplete/' + query,
                                headers={}, params={"query": query, "autocomplete_key": KEY, "callback": "callback"})

    result = json.loads(response.text.replace("typeof callback === 'function' && callback(", "").replace(");", ""))
    print(len(result["sections"]["packages"]))
    if len(result["sections"]["packages"]) == 0:
        wf.add_item('No Packages found.')
        wf.send_feedback()
        return 0

    for item in result["sections"]["packages"]:
        print(item)
        wf.add_item(item["value"],
                    subtitle=item["data"]["description"],
                    valid=True,
                    arg=URL + item["data"]["url"])
    wf.send_feedback()
    return 0


def main(wf):
    npm(wf)


if __name__ == u"__main__":
    wf = Workflow()
    sys.exit(wf.run(main))
