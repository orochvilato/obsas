# -*- coding: utf-8 -*-
# essayez quelque chose comme
def index():
    return dict(message="hello from fiches.py")
import json
def depute():
    a_id = request.vars.get('uid','welou')
    dep = mdb.acteurs.find_one({'uid':a_id})

    if not dep:
        redirect(URL(c='default',f='notfound'))
    del dep['_id']
    votes = mdb.votes.find({'uid':a_id})
    positions = {}
    dossiers= {'tous':{'n':0,'votefi':0,'voteem':0}}
    stats = {'n':votes.count(),'pour':0,'contre':0,'abstention':0,'nonVotant':0,'absent':0}
    for v in votes:
        if v['position'] in ['pour','contre','abstention']:
            positions[v['scrutin_id']] = v['position']
        stats[v['position']] += 1
   
    scrutins = sorted(list(mdb.scrutins.find({'scrutin_id':{'$in':positions.keys()}})),key=lambda x:x['scrutin_num'],reverse=True)
    from collections import OrderedDict
    scrutins_dossiers = OrderedDict()
    for s in scrutins:
        dosid = (s['scrutin_dossier'],s['scrutin_dossierLibelle'])
        if not dosid in scrutins_dossiers.keys():
            scrutins_dossiers[dosid] = []
        
        s['sort'] = 'adopté' if s['vote']['assemblee']['sort']=='pour' else 'rejeté'
        if not s['scrutin_dossier'] in dossiers.keys():
            dossiers[s['scrutin_dossier']]={'n':0,'votefi':0,'voteem':0}
        dossiers[s['scrutin_dossier']]['n'] += 1
        dossiers['tous']['n'] += 1

        for p in ['votefi','voteem']:
            if positions[s['scrutin_id']] == s[p]:
                dossiers[s['scrutin_dossier']][p] += 1
                dossiers['tous'][p] += 1
        
        s['flag'] = ( positions[s['scrutin_id']] != s['vote'][dep['groupe_abrev']]['sort'])
        scrutins_dossiers[dosid].append(s)
        
    return dict(stats=stats,scrutins=scrutins_dossiers,positions=positions,dossiers=dossiers,**dep)
