#!/home/www-data/web2py/applications/obsas/.pyenv/bin/python
# -*- coding: utf-8 -*-

import scrapy
import requests
import json
import re
from fuzzywuzzy import fuzz
from scrapy.crawler import CrawlerProcess

import sys

output_path = sys.argv[1]
exclude = json.loads(sys.argv[2])

leg = 15
scrutins = {}
dossiers = {}
types = {}
dossiers_vu = []
scrutins_txts = {}
amends_txts = {}
amds = {}

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
            request.meta['page'] = '1'
            request.meta['type'] = 'TOUS'
            request.meta['idDossier'] = 'TOUS'
            yield request



    def parse_main(self, response):

        request = scrapy.Request(url=response.url, callback=self.parse_page, dont_filter=True)
        request.meta['page'] = '1'
        request.meta['type'] = 'TOUS'
        request.meta['idDossier'] = 'TOUS'
        yield request


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



    def parse_dossier(self,response):
        votesloi = [ a.extract() for a in response.xpath('//a[contains(@href,"/ta/") or contains(@href,"/scrutins/jo")]/@href')]
        amendements = [ a.extract() for a in response.xpath('//a[contains(@href,"/ta/") or contains(@href,"/scrutins/jo") or (contains(@href,"/amendements/") and contains(@href,"ORGANE=&"))]/@href')]

        if len(votesloi)==1 and '/ta/' in votesloi[0] and response.meta['typedetail']=='loi':
            scrutins_txts[response.meta['snum']] = votesloi[0][-8:-4]
        else:
            i = 0
            while i<len(votesloi)-1:
                if '/scrutins/' in votesloi[i] and '/ta/' in votesloi[i+1]:
                    snum = int(votesloi[i][-8:-4])
                    sl = votesloi[i+1][-8:-4]
                    scrutins_txts[snum] = sl
                    i += 2
                else:
                    i += 1
        i = 0

        import requests
        while i<len(amendements):
            if '/amendements/' in amendements[i]:
                r = requests.get('http://www.assemblee-nationale.fr'+amendements[i])
                iddl = re.match(r'.*&idDossierLegislatif=([0-9]+)&.*',r.url)
                if iddl:
                    iddl = iddl.groups()[0]
                    loadamds = json.loads(requests.get('http://www2.assemblee-nationale.fr/recherche/query_amendements?typeDocument=amendement&leg=15&idDossierLegislatif='+iddl+'&premierSignataire=true&rows=100000&format=json&tri=ordreTexteasc&start=1&typeRes=liste').content)
                    fields = loadamds['infoGenerales']['description_schema'].split('|')+['autre','autre1','autre2']


                    _amds = [ dict((fields[i],v) for i,v in enumerate(elt.split('|'))) for elt in loadamds['data_table'] ]
                    _amdsdict = dict((_a['numAmend'].split(' ')[0],_a) for _a in _amds)

                amds[response.meta['sdossier']].append(_amdsdict)

            i += 1
        # http://www2.assemblee-nationale.fr/recherche/query_amendements?typeDocument=amendement&leg=15&idDossierLegislatif=35825&premierSignataire=true&rows=100000&format=json&tri=ordreTexteasc&start=1&typeRes=liste
        # http://www2.assemblee-nationale.fr/recherche/query_amendements?id=S-AMANR5L15PO717460B106N80&leg=15&typeRes=doc

    def parse_page(self, response):

        scrs = response.xpath('//table[@id="listeScrutins"]/tbody/tr')
        for scr in scrs:
            _num = int(scr.xpath('td[contains(@class,"denom")]/text()').extract()[0].replace('*',''))
            _pour = int(scr.xpath('td[contains(@class,"pour")]/text()').extract()[0])
            _contre = int(scr.xpath('td[contains(@class,"contre")]/text()').extract()[0])
            _scrutinlien = scr.xpath('td[contains(@class,"desc")]/a[contains(@href,"scrutins")]/@href')[0].extract()
            _dossierlien = scr.xpath('td[contains(@class,"desc")]/a[contains(@href,"dossiers")]/@href')

            if _dossierlien:
                _dossierlien = _dossierlien[0].extract()
            else:
                _dossierlien = None

            _abs = int(scr.xpath('td[contains(@class,"abs")]/text()').extract()[0])
            _desc = scr.xpath('td[contains(@class,"desc")]/text()').extract()[0].replace('  [','')
            _date = scr.xpath('td/text()').extract()[1]
            if _desc[:12]=="l'amendement":
                _typedetail = 'amendement'
            elif _desc[:9]=="la motion":
                _typedetail = 'motion'
            elif _desc[:27] =="l'ensemble du projet de loi":
                _typedetail = 'loi'
            elif _desc[:9] =="l'article":
                _typedetail = 'article'
            elif _desc[:14] ==u'la déclaration':
                _typedetail = 'declaration'
            else:
                _typedetail = 'autre'


            if _dossierlien and not _dossierlien in amds.keys():
                amds[_dossierlien] = []
                request = scrapy.Request(url=_dossierlien, callback=self.parse_dossier)
                request.meta['snum']=_num
                request.meta['sdossier']=_dossierlien
                request.meta['typedetail'] = _typedetail
                yield request

            if  "%s_%d" % (leg,_num) in exclude:
                continue
            if _num not in scrutins.keys():
                scrutins[_num] = {}

            scrutins[_num].update({'num':_num,
                                   'id':'%s_%d' % (leg,_num),
                                  'pour':_pour,
                                  'contre':_contre,
                                  'abs': _abs,
                                  'desc': _desc,
                                  'typedetail': _typedetail,
                                  'date': _date,
                                  'dossierlien':_dossierlien,
                                  'scrutinlien':_scrutinlien})
            if response.meta['idDossier'] != 'TOUS':
                scrutins[_num]['idDossier'] = response.meta['idDossier']
                scrutins[_num]['libelleDossier'] = dossiers[response.meta['idDossier']]
            if response.meta['type'] != 'TOUS':
                scrutins[_num]['type'] = response.meta['type']
                scrutins[_num]['libelleType'] = types[response.meta['type']]
            #if 'idDossier' in scrutins[_num].keys() and 'type' in scrutins[_num].keys():
            if not 'votes' in scrutins[_num].keys():
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

        # corrections
        corrections = {}
        for corr in response.xpath('//aside/div/div/div/div[contains(@class,"titre-contenu")]/span[contains(.,"Mises au point")]/../following-sibling::div[contains(@class,"corps-contenu")]/p[contains(@class,"itemmap")]').extract():
            cv = re.split(r'qui .tai',corr)
            if len(cv)<2:
                continue
            newpos = None
            if u'voter pour' in cv[1]:
                newpos = 'pour'
            elif u'voter contre' in cv[1]:
                newpos = 'contre'
            elif u'abstention' in cv[1] or u'abstenir' in cv[1]:
                newpos = 'abstention'
            noms = re.sub(r'\xa0|\n|\t|</b>|<b>|<p[^>]+>|</p>|\([^\)]+\)',r'',cv[0]).replace(' et ',',').replace(' ','').split(',')
            for nom in noms:
                corrections[normalize(nom)] = newpos

        for pos in positions:
            p = response.xpath('//div[contains(@class,"%s")]/ul[contains(@class,"deputes")]/li' % positions[pos])
            for dep in p:
                prenom = dep.xpath('text()').extract()[0][:-1]
                nom = dep.xpath('b/text()').extract()[0]
                nid = normalize(prenom+nom)

                scrutins[num]['votes'][pos] = scrutins[num]['votes'].get(pos,[])+[nid]

            if pos in ctrl.keys() and len(p)<>ctrl[pos]:
                print "PB COHERENCE"
                scrutins[num]['ok']=False;
        # non votants
        for nv in response.xpath('//div[contains(@class,"Non-votant") or contains(@class,"Non-votants")]/ul[contains(@class,"deputes")]').extract():
            noms = re.sub(r'\xa0|\n|\t|</b>|<b>|<ul[^>]+>|</ul>|\([^\)]+\)',r'',nv).replace(' et ',',').replace(' ','')[:-1].split(',')
            scrutins[num]['votes']['nonVotant'] = scrutins[num]['votes'].get('nonVotant',[]) + [ normalize(n) for n in noms ]

        scrutins[num]['corrections'] = corrections
        if not 'ok' in scrutins[num].keys():
            scrutins[num]['ok']=True;


process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)','DOWNLOAD_DELAY':0.25
})


process.crawl(ScrutinsSpider)
process.start() # the script will block here until the crawling is finished


from fuzzywuzzy import fuzz
import re
for s in scrutins.values():
    estamd = re.match(r'.*l\'amendement n. *([0-9]+) de (.*)',s['desc'])
    if estamd:
        namd = estamd.groups()[0]
        sig = estamd.groups()[1]
        dos = amds[s['dossierlien']]

        candidats = []
        for _amds in dos:
            if namd in _amds.keys():
                candidats.append((fuzz.token_set_ratio(sig,_amds[namd]['signataires'].split(',')[0]),_amds[namd]))

        _amds = sorted(candidats,key=lambda x:x[0], reverse=True)[0][1]
        amd_detail = json.loads(requests.get('http://www2.assemblee-nationale.fr/recherche/query_amendements?id='+_amds['id']+'&leg=15&typeRes=doc').content)
        fields = amd_detail['infoGenerales']['description_schema'].split('|')+['autre','autre1','autre2']
        _amdscompl = [ dict((fields[i],v) for i,v in enumerate(elt.split('|'))) for elt in amd_detail['data_table'] ][0]
        _amdscompl.update(_amds)
        s['reference'] = _amdscompl
    elif s['num'] in scrutins_txts.keys():
        s['reference'] = scrutins_txts[s['num']]

import json
with open(output_path+'/scrutins.json','w') as f:
    f.write(json.dumps(scrutins))
