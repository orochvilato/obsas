#!/home/www-data/web2py/applications/obsas/.pyenv/bin/python
# -*- coding: utf-8 -*-

import scrapy
import requests
import json
import re
from fuzzywuzzy import fuzz
from scrapy.crawler import CrawlerProcess

with open('/home/www-data/web2py/applications/obsas_dev/private/lexique2.json','r') as f:
    lexique = json.loads(f.read())

class WordCount:
    def __init__(self,lexique):
        self.words = {}
        self.lexique = lexique
        self._lex = set(lexique.keys())
    def addWords(self,item,txt):
        txt = txt.replace('\n',' ').replace('.',' ').replace(':',' ').replace(',',' ').replace(';',' ').replace('-',' ').replace('  ',' ').lower().split(' ')
        words = [ self.lexique[x] for x in txt if x in self._lex ]
        if not item in self.words.keys():
            self.words[item] = {}
        for w in words:
            if not w.strip():
                continue
            if not w in self.words[item].keys():
                self.words[item][w] = 1
            else:
                self.words[item][w] += 1
    def getWords(self,item):
        return self.words[item]

wc = WordCount(lexique)


leg = 15


import unicodedata
def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')
def normalize(s):
    return strip_accents(s).encode('utf8').replace(' ','').replace('-','').replace('\x0a','').replace('\xc5\x93','oe').lower() if s else s

def clean_ctx(ctx):
    return [e for e in ctx if e!='']

sessions = {}
interventions = []
class SessionsSpider(scrapy.Spider):
    name = "sessions"
    base_url = 'http://www.assemblee-nationale.fr'
    start_url = base_url+'/%s/debats/index.asp' % leg
    def start_requests(self):
        urls = [ self.start_url]


        for url in urls:
            request = scrapy.Request(url=url, callback=self.parse_main)
            yield request



    def parse_main(self, response):
        for periode in response.xpath('//ul[@class="liens-liste"]/li/a/@href'):
            url = self.base_url + periode.extract()
            request = scrapy.Request(url=url, callback=self.parse_periode)
            request.meta['url'] = url
            yield request
            #break

    def parse_periode(self, response):
        for session in response.xpath('//h1[@class="seance"]/a/@href'):
            url = response.meta['url'] + session.extract()

            request = scrapy.Request(url=url, callback=self.parse_session)
            yield request
            #break
    def parse_session(self, response):
        if not response.url in sessions.keys():
            sessions[response.url] = {}
        for balise in response.xpath('//p[@class="sommaigre" and contains(.,"Amendement")]/a'):
            try:
                anums = [ n.strip().split(' ')[0] for n in balise.xpath('text()').extract()[0].split(',') ]
                bnum = balise.xpath('@href').extract()[0].split('#')[1]
                for anum in anums:
                    sessions[response.url][anum] = bnum
            except:
                pass

        # analyse lexicale
        sommaire = response.xpath('//h1[@class="seance"]|//p[@class="somtitre"]|//p[@class="sompetcap"]|//p[@class="somtpetcap"]|//p[@class="sommaigre"]')
        path = ['','','','','']
        contexte = {}
        for elt in sommaire:
            if 'seance' in elt.extract():
                path = ['','','','','']
                path[0] = elt.xpath('text()').extract()[0]
            if 'somtitre' in elt.extract():
                path[1:] = ['','','','']
                path[1] = elt.xpath('.//a/text()').extract()[0]
            if 'somtpetcap' in elt.extract():
                path[2:] = ['','','']
                path[2] = elt.xpath('.//a/text()').extract()[0]
            if 'sompetcap' in elt.extract():
                path[3:] = ['','']
                path[3] = elt.xpath('.//a/text()').extract()[0]
            if 'sommaigre' in elt.extract():
                txt = elt.xpath('text()').extract()
                txt = txt[0].strip() if txt and len(txt[0].strip())>0 else None

                for a in elt.xpath('.//a'):
                    if txt:
                        if 'Amendement' in txt:
                            amds = a.xpath('text()').extract()
                            if amds:
                                amds = amds[0]
                                if len(amds.split(','))>1:
                                    txt = "Amendements nos"
                                else:
                                    txt = "Amendement no"

                                contexte[a.xpath('@href').extract()[0].split('#')[1]] = clean_ctx(path[:4]+[txt+' '+a.xpath('text()').extract()[0]])
                    else:
                        contexte[a.xpath('@href').extract()[0].split('#')[1]] = clean_ctx(path)
                if txt:
                    path[4] = elt.xpath('normalize-space(.)').extract()[0]
                else:
                    path[4] = ''
        #print [ x.extract() for x in sommaire]
        for itv in response.xpath('//div[@class="intervention"]'):
            for ancre in itv.xpath('p/a/@id').extract():
                if ancre in contexte.keys():
                    ctx = contexte[ancre]
                    ctx_idx = 0
                    break
            i = 0
            for p in itv.xpath('p'):
                acteur = p.xpath('b/a/@href')
                if acteur:
                    ancre = p.xpath('a/@id').extract()[0]
                    url = acteur.extract()[0]
                    if 'tribun' in url:
                        acteur = 'PA'+url.split('/')[-1].split('.')[0]
                    else:
                        acteur = url.split('/')[-1].split('_')[-1]
                    if acteur[0:2]!='PA':
                        print url, response.url, ctx
                    wc.addWords(acteur,' '.join(p.xpath('text()').extract()))
                    interventions.append({
                        'url':response.url+'#'+ancre,
                        'contexte':ctx,
                        'ctx_idx':ctx_idx,
                        'acteur':acteur,
                        'contenu':re.sub(r'<a name=.*\.  ','',p.extract())
                    })

process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)','DOWNLOAD_DELAY':0.25
})


process.crawl(SessionsSpider)
process.start() # the script will block here until the crawling is finished
#print interventions

import json
with open('/tmp/mots.json','w') as f:
    f.write(json.dumps(wc.words))

with open('/tmp/interventions.json','w') as f:
    f.write(json.dumps(interventions))


import json
with open('/tmp/sessions.json','w') as f:
    f.write(json.dumps(sessions))
