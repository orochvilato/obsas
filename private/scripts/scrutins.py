#!/home/www-data/web2py/applications/obsas/.pyenv/bin/python

import scrapy
import requests
import json
import re

from scrapy.crawler import CrawlerProcess


leg = 15
scrutins = {}
dossiers = {}
types = {}

import unicodedata
def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')
def normalize(s):
    return strip_accents(s).encode('utf8').replace(' ','').replace('-','').replace('\x0a','').replace('\xc5\x93','oe').lower() if s else s






class ScrutinsSpider(scrapy.Spider):
    name = "scrutins"
    base_url = 'http://www2.assemblee-nationale.fr/scrutins/liste/(legislature)/%s/' % leg
    detail_url = 'http://www2.assemblee-nationale.fr/scrutins/detail/(legislature)/%s/' % leg
    def start_requests(self):
        urls = [ self.base_url+'(type)/TOUS/(idDossier)/TOUS']


        for url in urls:
            request = scrapy.Request(url=url, callback=self.parse_main)
            yield request


    def parse_main(self, response):
        for _idDossier in response.xpath('//select[@name="idDossier"]/option'):
            ridDossier = _idDossier.xpath('@value').extract()[0]
            rpage = 1
            rtype = 'TOUS'
            if ridDossier!='TOUS' and len(ridDossier)>1:
                dossiers[ridDossier] = _idDossier.xpath('text()').extract()[0]
                request = scrapy.Request(url=self.base_url+'(type)/%s/(idDossier)/%s' % (rtype,ridDossier),
                                     callback=self.parse_page)
                request.meta['page'] = '1'
                request.meta['type'] = 'TOUS'
                request.meta['idDossier'] = ridDossier
                yield request

        for _type in response.xpath('//select[@name="type"]/option'):
            ridDossier = 'TOUS'
            rpage = 1
            rtype = _type.xpath('@value').extract()[0]
            if rtype!='TOUS' and len(rtype)>0:
                types[rtype] = _type.xpath('text()').extract()[0]
                request = scrapy.Request(url=self.base_url+'(type)/%s/(idDossier)/%s' % (rtype,ridDossier),
                                     callback=self.parse_page)
                request.meta['page'] = '1'
                request.meta['type'] = rtype
                request.meta['idDossier'] = 'TOUS'
                yield request



    def parse_page(self, response):
        scrs = response.xpath('//table[@id="listeScrutins"]/tbody/tr')
        for scr in scrs:
            _num = int(scr.xpath('td[contains(@class,"denom")]/text()').extract()[0].replace('*',''))
            _pour = int(scr.xpath('td[contains(@class,"pour")]/text()').extract()[0])
            _contre = int(scr.xpath('td[contains(@class,"contre")]/text()').extract()[0])
            _abs = int(scr.xpath('td[contains(@class,"abs")]/text()').extract()[0])
            _desc = scr.xpath('td[contains(@class,"desc")]/text()').extract()[0].replace('  [','')
            _date = scr.xpath('td/text()').extract()[1]
            if _num not in scrutins.keys():
                scrutins[_num] = {}
            scrutins[_num].update({'num':_num,
                                   'id':'%s_%d' % (leg,_num),
                                  'pour':_pour,
                                  'contre':_contre,
                                  'abs': _abs,
                                  'desc': _desc,
                                  'date': _date})
            if response.meta['idDossier'] != 'TOUS':
                scrutins[_num]['idDossier'] = response.meta['idDossier']
                scrutins[_num]['libelleDossier'] = dossiers[response.meta['idDossier']]
            if response.meta['type'] != 'TOUS':
                scrutins[_num]['type'] = response.meta['type']
                scrutins[_num]['libelleType'] = types[response.meta['type']]
            if 'idDossier' in scrutins[_num].keys() and 'type' in scrutins[_num].keys():
                scrutins[_num]['votes'] = {}
                request = scrapy.Request(url=self.detail_url+'(num)/%d' % _num, callback=self.parse_scrutin)
                request.meta['num'] = _num
                yield request



        lastpage = [x.extract() for x in response.xpath('//div[contains(@class,"pagination-bootstrap")]/ul/li/a/text()')]


        if lastpage and int(lastpage[-1])>int(response.meta['page']):
            page = '%d' % (1+int(response.meta['page']))
            roffset = response.meta['page']+'00'
            rtype = response.meta['type']
            ridDossier = response.meta['idDossier']
            request = scrapy.Request(url=self.base_url+'(offset)/%s/(type)/%s/(idDossier)/%s' % (roffset,rtype,ridDossier),
                                     callback=self.parse_page)
            request.meta['page'] = page
            request.meta['type'] = rtype
            request.meta['idDossier'] = ridDossier
            yield request

    def parse_scrutin(self, response):
        positions ={'pour':'Pour','contre':'Contre','abstention':'Abstention'}
        num = response.meta['num']
        votants  = int(response.xpath('//p[@id="total"]/b/text()').extract()[0])
        pour = int(response.xpath('//p[@id="pour"]/b/text()').extract()[0])
        contre = int(response.xpath('//p[@id="contre"]/b/text()').extract()[0])
        abstention = votants - pour - contre
        ctrl= {'Pour':pour, 'Contre':contre, 'Abstention':abstention}

        for pos in positions:
            p = response.xpath('//div[@class="%s"]/ul[@class="deputes"]/li' % positions[pos])
            for dep in p:
                prenom = dep.xpath('text()').extract()[0][:-1]
                nom = dep.xpath('b/text()').extract()[0]
                scrutins[num]['votes'][pos] = scrutins[num]['votes'].get(pos,[])+[normalize(prenom+nom)]

            if pos in ctrl.keys() and len(p)<>ctrl[pos]:
                print "PB COHERENCE"
                scrutins[num]['ok']=False;
        # non votants
        for nv in response.xpath('//div[@class="Non-votant" or @class="Non-votants"]/ul[@class="deputes"]').extract():
            noms = re.sub(r'\xa0|\n|\t|</b>|<b>|<ul[^>]+>|</ul>|\([^\)]+\)',r'',nv).replace(' et ',',').replace(' ','')[:-1].split(',')
            scrutins[num]['votes']['nonVotant'] = scrutins[num]['votes'].get('nonVotant',[]) + [ normalize(n) for n in noms ]

        if not 'ok' in scrutins[num].keys():
            scrutins[num]['ok']=True;


process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)','DOWNLOAD_DELAY':0.25
})


process.crawl(ScrutinsSpider)
process.start() # the script will block here until the crawling is finished


import json
with open('/tmp/scrutins.json','w') as f:
    f.write(json.dumps(scrutins))
