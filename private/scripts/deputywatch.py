#!/home/www-data/web2py/applications/obsas/.pyenv/bin/python


import scrapy
import requests
import json
from scrapy.crawler import CrawlerProcess

import unicodedata

import sys

output_path = sys.argv[1]

def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')
def normalize(s):
    return strip_accents(s).replace(' ','').replace('-','').lower() if s else s


deputywatch = {}

class DeputyWatchSpider(scrapy.Spider):
    name = "deputywatch"
    base_url = 'https://www.deputywatch.org/'
    def start_requests(self):
        urls = [ self.base_url+'recherches/']

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_main)

    def parse_main(self, response):
        for dep in response.xpath('//select[@id="ListeDepute"]/option/text()'):
            nom = dep.extract()
            request = scrapy.Request(url="%safficherDepute/?nom=%s&prenom=&consulter=" % (self.base_url,nom), callback=self.parse_dep)
            request.meta['nom'] = nom
            yield request

    def parse_dep(self, response):
        nom = response.xpath('(//table)[3]/tr/td[1]/center/b/text()').extract()[0]
        for tr in response.xpath('(//table)[3]/tr'):
            nom = tr.xpath('td[1]/center/b/text()').extract()[0]
            url = self.base_url + 'afficherDepute/'+ tr.xpath('td[5]/center/a/@href').extract()[0]
            deputywatch[normalize(nom)] = {'nom':nom,'url':url}
            request = scrapy.Request(url=url, callback=self.parse_fiche)
            request.meta['nom'] = normalize(nom)
            yield request

    def parse_fiche(self, response):
        if response.status != 404:
            deputywatch[response.meta['nom']]['flag'] = True if (not "Aucun fait notable" in response.text or not "Pas d'Infraction(s)" in response.text) else False



process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
})


process.crawl(DeputyWatchSpider)
process.start() # the script will block here until the crawling is finished

deputywatch =  dict((k,v) for k,v in deputywatch.iteritems() if v.get('flag',False) == True)

with open(output_path+'/deputywatch.json','w') as f:
    f.write(json.dumps(deputywatch))
