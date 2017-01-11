#!/usr/bin/python

from __future__ import print_function
import sys
import urllib
import json
import requests
import requests_cache
from workflow import Workflow

__author__ = "gexiaowei"
__version__ = "1.3"
__email__ = "gandxiaowei@gmail.com"
__status__ = "Development"

requests_cache.install_cache('packages')

base = {
    bower: 'https://libraries.io/api/bower-search',
    npm: 'https://ac.cnstrc.com/autocomplete/{0}',
    passport: 'http://passportjs.org/data.json',
    yeoman: 'https://cdn.rawgit.com/yeoman/yeoman-generator-list/a8e5052236d77f0e0f1a6e453e81b3718f2fa270/cache.json'
}


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
    elif domain == 'yeoman':
        result = yeoman(keyword)
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
                                base['bower'],
                                headers={}, params={"q": keywords})
    result = json.loads(response.text)
    return map(lambda item: dict(name=item["name"], subtitle=item["description"], url=item["homepage"] or item["repository_url"]), result)


def npm(keywords):
    key = "CD06z4gVeqSXRiDL2ZNK"
    home = "https://www.npmjs.com"
    response = requests.request("GET",
                                base['npm'].format(keywords),
                                headers={}, params={"query": keywords, "autocomplete_key": key, "callback": "callback"})
    result = json.loads(response.text.replace(
        "typeof callback === 'function' && callback(", "").replace(");", ""))
    return map(lambda item: dict(name=item["value"],
                                 subtitle=item["data"][
                                     'description'] if 'description' in item["data"] else '',
                                 url=home + item["data"]["url"]), result["sections"]["packages"])


def yeoman(keywords):
    response = requests.request('GET', base['yeoman'])
    result = json.loads(response.text)
    before = filter(lambda item: item['name'].find(keywords) != -1, result)
    after = map(lambda item: dict(name=item['name'], subtitle=item[
                'description'], url=item['site']), before)
    return after


def passport(keywords):
    response = requests.request('GET', base['passport'])
    result = json.loads(response.text)
    before = filter(lambda item: item['label'].find(keywords) != -1, result)
    after = map(lambda item: dict(name=item['label'], subtitle=item[
                'desc'], url=item['url']), before)
    return after


def main(wf):
    search(wf)


if __name__ == u"__main__":
    wf = Workflow()
    sys.exit(wf.run(main))
