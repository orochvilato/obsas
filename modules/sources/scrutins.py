#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import *

def getScrutins(acteurs,deja=[]):
    import os
    import json
    fp = os.path.join(current.request.folder, 'private/scripts', 'scrutins.py')
    
    did_scrape = True if os.system(fp) else False

    _scrutins = json.loads(open('/tmp/scrutins.json','r').read())

    votes = []
    scrutins = []
    
    def act_votedata(id,position):
        act = acteurs[id]
        return {'uid':act['uid'],
                'nom':act['nomcomplet'],
                'commissions': act['commissions'],
                'organes': act['organes'],
                'groupe': act['groupe'],
                'classeage':act['classeage'],
                'region':act['region'],
                'typeregion':act['typeregion'],
                'departement':act['departement'],
                'csp':act['csp'],
                'sexe':act['sexe'],
                'position':position}
    
    for s in _scrutins.values():
        if s['id'] in deja:
            continue
            
        scrutin = { 'scrutin_num':s['num'],
                    'scrutin_id':s['id'],
                    'scrutin_desc':s['desc'],
                    'scrutin_date':s['date'],
                    'scrutin_type':s['type'],
                    'scrutin_typeLibelle':s['libelleType'],
                    'scrutin_dossier':s['idDossier'],
                    'scrutin_dossierLibelle':s['libelleDossier'],
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
                    vote.update(act_votedata(acteur['id'],p))
                    vote['vote_id'] = "%d_%s" % (s['num'],acteur['id'])
                    votes.append(vote)
                    
        for id in list(set(acteurs.keys())-set(exprimes)):
            vote = dict(s)
            vote.update(act_votedata(id,'absent'))
            vote['vote_id'] = "%d_%s" % (s['num'],id)
            votes.append(vote)
        
        scrutins.append(scrutin)
    return {'votes':votes,'scrutins':scrutins}
