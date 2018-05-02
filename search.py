#!/usr/bin/python

from __future__ import print_function
import sys
import urllib
import json
import requests
import requests_cache
import urllib2
from workflow import Workflow

__author__ = "gexiaowei"
__version__ = "1.4"
__email__ = "gandxiaowei@gmail.com"
__status__ = "Development"

requests_cache.install_cache('packages')

path = {
    'bower': 'https://libraries.io/api/bower-search',
    'npm': 'https://ac.cnstrc.com/autocomplete/{0}',
    'passport': 'http://passportjs.org/data.json',
    'yeoman': 'https://cdn.rawgit.com/yeoman/yeoman-generator-list/a8e5052236d77f0e0f1a6e453e81b3718f2fa270/cache.json',
    'yarn': 'https://ofcncog2cu-2.algolianet.com/1/indexes/*/queries'
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
    elif domain == 'yarn':
        result = yarn(keyword)

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
                                path['bower'],
                                headers={}, params={"q": keywords})
    result = json.loads(response.text)
    return map(lambda item: dict(name=item["name"], subtitle=item["description"], url=item["homepage"] or item["repository_url"]), result)


def npm(keywords):
    key = "CD06z4gVeqSXRiDL2ZNK"
    home = "https://www.npmjs.com"
    response = requests.request("GET",
                                path['npm'].format(keywords),
                                headers={}, params={"query": keywords, "autocomplete_key": key, "callback": "callback"})
    result = json.loads(response.text.replace(
        "typeof callback === 'function' && callback(", "").replace(");", ""))
    return map(lambda item: dict(name=item["value"],
                                 subtitle=item["data"][
                                     'description'] if 'description' in item["data"] else '',
                                 url=home + item["data"]["url"]), result["sections"]["packages"])


def yeoman(keywords):
    response = requests.request('GET', path['yeoman'])
    result = json.loads(response.text)
    before = filter(lambda item: item['name'].find(keywords) != -1, result)
    after = map(lambda item: dict(name=item['name'], subtitle=item[
                'description'], url=item['site']), before)
    return after


def passport(keywords):
    response = requests.request('GET', path['passport'])
    result = json.loads(response.text)
    before = filter(lambda item: item['label'].find(keywords) != -1, result)
    after = map(lambda item: dict(name=item['label'], subtitle=item[
                'desc'], url=item['url']), before)
    return after


def yarn(keywords):
    home = 'https://yarnpkg.com/zh-Hans/package/'
    query_string = {
        "x-algolia-agent": "Algolia for vanilla JavaScript (lite) 3.25.1;react-instantsearch 5.0.0;JS Helper 2.23.2",
        "x-algolia-application-id": "OFCNCOG2CU",
        "x-algolia-api-key": "f54e21fa3a2a0160595bb058179bfb1e"
    }
    payload = {"requests": [{"indexName": "npm-search",
                             "params": "query=" + keywords + "&hitsPerPage=5&maxValuesPerFacet=10&page=0&attributesToRetrieve=%5B%22deprecated%22%2C%22description%22%2C%22downloadsLast30Days%22%2C%22repository%22%2C%22homepage%22%2C%22humanDownloadsLast30Days%22%2C%22keywords%22%2C%22license%22%2C%22modified%22%2C%22name%22%2C%22owner%22%2C%22version%22%5D&attributesToHighlight=%5B%22name%22%2C%22description%22%2C%22keywords%22%5D&highlightPreTag=%3Cais-highlight%3E&highlightPostTag=%3C%2Fais-highlight%3E&facets=%5B%22keywords%22%2C%22keywords%22%2C%22owner.name%22%5D&tagFilters=&optionalFacetFilters=%5B%5B%22_searchInternal.concatenatedName%3Areact%22%5D%5D"}]}
    response = requests.request(
        "POST", path['yarn'], data=json.dumps(payload), params=query_string)
    result = json.loads(response.text)
    return map(lambda item: dict(name=item["name"],
                                 subtitle=item["description"],
                                 url=home + item["name"]), result["results"][0]['hits'])


def main(wf):
    search(wf)

if __name__ == u"__main__":
    wf = Workflow()
    sys.exit(wf.run(main))
