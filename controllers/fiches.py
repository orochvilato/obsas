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
    stats = {'n':votes.count(),'pour':0,'contre':0,'abstention':0,'nonVotant':0,'absent':0,'votefi':0,'voteem':0,'diss':0,'exprime':0}
    for v in votes:
        if v['position'] in ['pour','contre','abstention']:
            positions[v['scrutin_id']] = v['position']
            stats['exprime'] += 1
        stats[v['position']] += 1
    
    stats['exprimepct'] = int(100*float(stats['exprime'])/stats['n'])
    scrutins = sorted(list(mdb.scrutins.find({'scrutin_id':{'$in':positions.keys()}})),key=lambda x:x['scrutin_num'],reverse=True)
    from collections import OrderedDict
    scrutins_dossiers = OrderedDict()
    for s in scrutins:
        diss = ( positions[s['scrutin_id']] != s['vote'][dep['groupe_abrev']]['sort'])
        if diss:
            stats['diss'] += 1
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
                stats[p] += 1
        
        s['flag'] = diss
        scrutins_dossiers[dosid].append(s)
        stats['disspct'] =  int(100*float(stats['diss'])/stats['exprime'])
        stats['votefipct'] =  int(100*float(stats['votefi'])/stats['exprime'])
        stats['voteempct'] =  int(100*float(stats['voteem'])/stats['exprime'])
        if s['scrutin_desc'][:12]=="l'amendement":
            s['typedetail'] = 'amendement'
        elif s['scrutin_desc'][:9] =="la motion":
            s['typedetail'] = 'motion'
        elif s['scrutin_desc'][:27] =="l'ensemble du projet de loi":
            s['typedetail'] = 'loi'
        elif s['scrutin_desc'][:9] =="l'article":
            s['typedetail'] = 'article'
        elif s['scrutin_desc'][:14] ==u'la déclaration':
            s['typedetail'] = 'declaration'
        else:
            s['typedetail'] = 'autre'
                        
    return dict(stats=stats,scrutins=scrutins_dossiers,positions=positions,dossiers=dossiers,**dep)
