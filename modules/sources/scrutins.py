#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import *

import pdfminer.high_level
import pdfminer.layout
import sys
from io import BytesIO
import cStringIO, codecs
import json
import re
import requests

from tools import normalize,flatten,strip_accents

legislature = '15'

votes = {'Pour':'pour',
         'Contre':'contre',
         'Abstention': 'abstention',
         'Non-votant(s)': 'nonVotant'
        }


def parseVotePDF(url):
    scrs = {}
    # Create a PDF interpreter object.
    laparams = pdfminer.layout.LAParams(word_margin=0.4, char_margin=3)
    
    
    content = requests.get(url).content
    fp = BytesIO(content)
    # Create a PDF parser object associated with the file object.
    txtfp = BytesIO()

    pdfminer.high_level.extract_text_to_fp(fp, outfp=txtfp,codec='utf-8',laparams = laparams)
    r = txtfp.getvalue().decode('utf8')

    import re
    scrutins = re.split(r'Analyse du scrutin[ n]+. *(\d+)',r)[1:]
    scrutins = [scrutins[x:x+2] for x in xrange(0, len(scrutins), 2)]
    for noscrutin,rscrutin in scrutins:
        print url,noscrutin
        pages = re.split(r'Page \d+ sur \d+[ \n\r\x0c]+',rscrutin)
        synthese,pages = pages[0],strip_accents(''.join(pages[1:]))
        pages = re.split(r'Mises au point', pages)+['']
        pages, miseaupoint = pages[0],pages[1:]
        pages = ''.join(re.split(r'[\w ,:]+\(\d+\) *\n',pages))
        pages = re.split(r'([\w\-\(\)]+) : (\d+)',pages)[1:]
        positions = [pages[x:x+3] for x in xrange(0, len(pages), 3)]

        synthese = synthese.replace('\n',' ').replace('  ',' ')
        #noscrutin = re.search(r'Analyse du scrutin[ n]+. *(\d)',synthese).groups()[0]
        datestr = re.search(r's.ance du \w+ (\d+ [^ ]+ \d+)',synthese).groups()[0]

        import locale
        locale.setlocale(locale.LC_ALL, 'fr_FR.utf8')
        from datetime import datetime
        date = datetime.strptime(datestr,"%d %B %Y")

        libelle = re.search(r'Scrutin public sur (.*). Demand. par :',synthese)
        if libelle:
            libelle = libelle.groups()[0]
        else:
            libelle = re.search(r'Scrutin public sur (.*). Synth',synthese).groups()[0]

        scrutin = { 'num':int(noscrutin),'id':'%s_%s' % (legislature,noscrutin),'desc':libelle,'date':date.strftime('%d/%m/%Y'),'votes':{'pour':[],'contre':[],'abstention':[],'nonVotant':[]}}
        
        pb = False
        avotes={}
        for pos,nb,act in positions:
             act = act.split('\n\n')
             if len(act)>1 and 'au moment du scrutin' in act[-1]:
                del act[-1]
             act = '\n'.join(act)
                
             act = act.replace(' et ',',').replace(' et',',').replace('\net',',').replace('\n','').replace(' ','').replace(u'\u0153','oe')
             act = re.sub(r'\([^\)]+\)',r'',act).split(',')
             if int(nb) != len(act):
                 print int(nb),len(act), "probleme"
                 pb = True
             for a in act:
                avotes[normalize(a)] = votes[pos]
        if not pb:
            for a in avotes.keys():
                scrutin['votes'][avotes[a]].append(a)
            
            scrutin['ok'] = True
            scrs[noscrutin] = scrutin
        return scrs


def get_scrutinsPDFs():
    # recupération page principale assemblée
    an = requests.get('http://www.assemblee-nationale.fr/').content
    import lxml.html
    root = lxml.html.fromstring(an)
    pdfs = root.xpath('//a[contains(@href,"pdf") and contains(text(),"Voir")]/@href')
    scrutins = {}
    for pdf in pdfs:
        scrutins.update(parseVotePDF(pdf))
    return scrutins











def getScrutins(acteurs,deja=[]):
    import os
    import json
    _scrutins = {}
    _scrutins = get_scrutinsPDFs()
    fp = os.path.join(current.request.folder, 'private/scripts', 'scrutins.py')
    did_scrape = True if os.system(fp) else False

    _scrutins.update(json.loads(open('/tmp/scrutins.json','r').read()))

    votes = []
    scrutins = []
    
    def act_votedata(id,position,posori=None):
        act = acteurs[id]
        return {'uid':act['uid'],
                'nom':act['nomcomplet'],
                'commissions': act['commissions'],
                'organes': act['organes'],
                'groupe': act['groupe'],
                'groupeabrev': act['groupe_abrev'],
                'age':act['age'],
                'classeage':act['classeage'],
                'region':act['region'],
                'typeregion':act['typeregion'],
                'departement':act['departement'],
                'csp':act['csp'],
                'sexe':act['sexe'],
                'position':position,
                'position_ori':posori }
    
    for s in _scrutins.values():
        if s['id'] in deja:
            continue
        desc = s['desc'].replace('.[','.')
        types = s.get('libelleType','N/A')
        fulldesc = u"Scrutin n° %d du %s : %s" % (s[u'num'],s[u'date'],desc)
        scrutin = { 'scrutin_num':s['num'],
                    'scrutin_id':s['id'],
                    'scrutin_desc':desc,
                    'scrutin_fulldesc':fulldesc,
                    'scrutin_date':s['date'],
                    'scrutin_type':s.get('type','N/A'),
                    'scrutin_typeLibelle':types,
                    'scrutin_dossier':s.get('idDossier','N/A'),
                    'scrutin_dossierLibelle':s.get('libelleDossier','N/A'),
                    'scrutin_typedetail':s['typedetail'],
                    'scrutin_ok':s['ok']
                   }
        
        exprimes = []
        for p in s['votes']:
            for v in s['votes'][p]:
                vote = dict(scrutin)
                acteur = acteurs.get('m.'+v,acteurs.get('mme'+v,acteurs.get(v,'PB')))
                if acteur == 'PB':
                    print v.encode('utf8')
                else:
                    exprimes.append(acteur['id'])
                    corr = s['corrections'].get('m.'+v,s['corrections'].get('mme'+v,False))
                    if corr:
                        position = corr
                        posori = p
                    else:
                        position = p
                        posori = p
                    vote.update(act_votedata(acteur['id'],position,posori))
                    vote['vote_id'] = "%d_%s" % (s['num'],acteur['id'])
                    votes.append(vote)
                    
        for id in list(set(acteurs.keys())-set(exprimes)):
            vote = dict(scrutin)
            vote.update(act_votedata(id,'absent'))
            vote['vote_id'] = "%d_%s" % (s['num'],id)
            votes.append(vote)
        if 'reference' in s.keys():
            scrutin.update({'scrutin_ref':s['reference']})
        scrutin.update({  'scrutin_lienscrutin':s['scrutinlien'],
                            'scrutin_liendossier':s['dossierlien'] })
        scrutins.append(scrutin)
    return {'votes':votes,'scrutins':scrutins}
