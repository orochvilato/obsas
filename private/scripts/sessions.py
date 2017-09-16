#!/home/www-data/web2py/applications/obsas/.pyenv/bin/python
# -*- coding: utf-8 -*-
# args :
# outputpath
# lexiquespath
# exclude

import scrapy
import requests
import json
import re
from fuzzywuzzy import fuzz
from scrapy.crawler import CrawlerProcess
import locale
locale.setlocale(locale.LC_ALL, 'fr_FR.utf8')

import sys

output_path = sys.argv[1]
exclude = json.loads(sys.argv[2])



leg = 15


import unicodedata
def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')
def normalize(s):
    return strip_accents(s).replace(u'\xa0','').encode('utf8').replace(' ','').replace('-','').replace('\x0a','').replace('\xc5\x93','oe').decode('utf8').lower() if s else s

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
            session_id = session.extract()
            if session_id in exclude:
               
                continue
                
            url = response.meta['url'] + session_id
            request = scrapy.Request(url=url, callback=self.parse_session)
            
            request.meta['session_id'] = session_id
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
        idx = 0
        import datetime
        for elt in sommaire:
            if 'seance' in elt.extract():
                path = ['','','','','']
                path[0] = elt.xpath('text()').extract()[0]
                sdate = datetime.datetime.strptime(' '.join(path[0].split(' ')[-3:]).encode('utf8'),'%d %B %Y').strftime('%Y-%m-%d')

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


            for p in itv.xpath('p'):
                acteur = p.xpath('b/a/@href')

                if acteur:
                    ancre = p.xpath('a/@id').extract()[0]
                    nomnorm = normalize(p.xpath('b/a/text()').extract()[0].replace(' et ','|'))
                    url = acteur.extract()[0]
                    if 'tribun' in url:
                        acteur = 'PA'+url.split('/')[-1].split('.')[0]
                    else:
                        acteur = url.split('/')[-1].split('_')[-1]
                    if acteur[0:2]!='PA':
                        print url, response.url, ctx
                    texte = u' '.join(p.xpath('text()').extract())
                    texte = texte.replace('.  ','').replace(u'\xa0','')
                    print len(interventions),output_path
                    if "La parole est" in texte or u"Quel est l’avis d" in texte:
                        pass
                    else:
                        #wc.setWords('noms',acteur,texte)
                        #wc.setWords('verbs',acteur,texte)
                        idx += 1
                        ctx_idx += 1
                        interventions.append({
                            'itv_n':idx,
                            'itv_date':sdate,
                            'itv_url':response.url+'#'+ancre,
                            'session_id':response.meta['session_id'],
                            'itv_id':response.meta['session_id']+str(idx),
                            'depute_id':nomnorm,
                            'itv_ctx':ctx,
                            'itv_ctx_n':ctx_idx,
                            'depute_uid':acteur,
                            'itv_nbmots':len(texte.split(' ')),
                            'itv_contenu_texte':texte,
                            'itv_contenu':re.sub(r'<a name=.*\.  ','',p.extract())
                        })

process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)','DOWNLOAD_DELAY':0.25
})


process.crawl(SessionsSpider)
process.start() # the script will block here until the crawling is finished
#print interventions

import json
#with open(output_path+'/mots.json','w') as f:
#    f.write(json.dumps({'sessions':sessions_id,'mots':wc.words}))

with open(output_path+'/interventions.json','w') as f:
    f.write(json.dumps(interventions))

with open(output_path+'/sessions.json','w') as f:
    f.write(json.dumps(sessions))
