# -*- coding: utf-8 -*-
# essayez quelque chose comme
def index():
    return dict(message="hello from fiches.py")
import json
def deputes():
    deps = list(mdb.acteurs.find())
    
    return dict(deputes=deps)


def circo():
    deps = list(mdb.acteurs.find())
    return dict(deputes=deps)

def depute():
    a_id = request.vars.get('uid','welou')
    dep = mdb.acteurs.find_one({'uid':a_id})

    if not dep:
        redirect(URL(c='default',f='notfound'))
    del dep['_id']
    votes = mdb.votes.find({'uid':a_id})
    positions = {}
    dossiers= {'tous':{'n':0,'votefi':0,'voteem':0}}
    stats = {'n':votes.count(),'pour':0,'contre':0,'abstention':0,'nonVotant':0,'absent':0,'votefi':0,'voteem':0,'diss':0,'exprime':0,'voteempct':0,'votefipct':0,'disspct':0}
    for v in votes:
        if v['position'] in ['pour','contre','abstention']:
            #positions[v['scrutin_id']] = v['position']
            stats['exprime'] += 1
        positions[v['scrutin_id']] = v['position']
        stats[v['position']] += 1
    
    stats['exprimepct'] = int(100*float(stats['exprime'])/stats['n'])
    scrutins = sorted(list(mdb.scrutins.find({'scrutin_id':{'$in':positions.keys()}})),key=lambda x:x['scrutin_num'],reverse=True)
    
    from collections import OrderedDict
    scrutins_dossiers = OrderedDict()
    for s in scrutins:
        diss = ( positions[s['scrutin_id']] != s['vote'][dep['groupe_abrev']]['sort']) and (not positions[s['scrutin_id']] in ['absent','nonVotant'])
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
        stats['disspct'] =  int(100*float(stats['diss'])/stats['exprime']) if stats['exprime']>0 else '-'
        stats['votefipct'] =  int(100*float(stats['votefi'])/stats['exprime']) if stats['exprime']>0 else '-'
        stats['voteempct'] =  int(100*float(stats['voteem'])/stats['exprime']) if stats['exprime']>0 else '-'
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
        posscr = ""
        if s['votefi']==positions[s['scrutin_id']]:
            posscr += '_votefi'
        if s['voteem']==positions[s['scrutin_id']]:
            posscr += '_voteem'
        if s['flag']:
            posscr += '_dissidence'
        if positions[s['scrutin_id']]=='abstention':
            posscr += 'abstention'
        if positions[s['scrutin_id']] in ['absent','nonVotant']:
            posscr += 'absentnv'
        s['posscr'] = posscr
        s['absent'] =  (positions[s['scrutin_id']] in ['absent','nonVotant'])
    return dict(stats=dep['statsvote'],scrutins=scrutins_dossiers,positions=positions,dossiers=dossiers,**dep)
