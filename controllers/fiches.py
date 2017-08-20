# -*- coding: utf-8 -*-
# essayez quelque chose comme
# TODO : page député les scrutins avec votes identiques FI/EM doivent apparaitre de la couleur du groupe du député si EM/FI

def index():
    return dict(message="hello from fiches.py")
import json

def scrutin():
    vpositions = ['pour','contre','abstention']
    id = request.vars.get('id','welou')
    scrutin = mdb.scrutins.find_one({'scrutin_id':id})

    if not scrutin:
        redirect(URL(c='default',f='notfound'))
    
    posorder = [ scrutin['votefi'] ]
    groupes = [(g['libelleAbrev'],g['libelle'],g['nbmembres']) for g in mdb.organes.find({'$and':[{'codeType':'GP'},{'viMoDe_dateFin':None}]})]
    if (scrutin['votefi']!=scrutin['voteem']):
        posorder.append(scrutin['voteem'])
    for p in vpositions:
        if not p in posorder:
            posorder.append(p)
            
    for v in mdb.votes.find({'scrutin_id':id}):
        gp = v['groupeabrev']
        if not 'votes' in scrutin['vote'][gp]:
            scrutin['vote'][gp]['votes'] = []
        if v['position'] in vpositions and v['position']!=scrutin['vote'][gp]['sort']:
            if v['position']==scrutin['votefi']:
                cat = "votefi"
            elif v['position']==scrutin['voteem']:
                cat = "voteem"
            else:
                cat = "autre"
            scrutin['vote'][gp]['votes'].append((v['uid'],v['nom'],cat,v['position']))
            
                
    if scrutin['scrutin_desc'][:12]=="l'amendement":
        scrutin['typedetail'] = 'amendement'
    elif scrutin['scrutin_desc'][:9] =="la motion":
        scrutin['typedetail'] = 'motion'
    elif scrutin['scrutin_desc'][:27] =="l'ensemble du projet de loi":
        scrutin['typedetail'] = 'loi'
    elif scrutin['scrutin_desc'][:9] =="l'article":
        scrutin['typedetail'] = 'article'
    elif scrutin['scrutin_desc'][:14] ==u'la déclaration':
        scrutin['typedetail'] = 'declaration'
    else:
        scrutin['typedetail'] = 'autre'
    scrutin['sort'] = 'adopté' if scrutin['vote']['assemblee']['sort']=='pour' else 'rejeté'
    for g in scrutin['vote'].keys():
        
        scrutin['vote'][g]['stats'] = {
            'exprimepct': (scrutin['vote'][g]['total_votants'],scrutin['vote'][g]['total'],int(100*float(scrutin['vote'][g]['total_votants'])/scrutin['vote'][g]['total'])),
            'votefipct': (scrutin['vote'][g][scrutin['votefi']],scrutin['vote'][g]['total_votants'],int(100*float(scrutin['vote'][g][scrutin['votefi']])/scrutin['vote'][g]['total_votants'])),
            'voteempct': (scrutin['vote'][g][scrutin['voteem']],scrutin['vote'][g]['total_votants'],int(100*float(scrutin['vote'][g][scrutin['voteem']])/scrutin['vote'][g]['total_votants'])),
            'disspct': (scrutin['vote'][g]['total_votants']-scrutin['vote'][g][scrutin['vote'][g]['sort']],scrutin['vote'][g]['total_votants'],int(100*float(scrutin['vote'][g]['total_votants']-scrutin['vote'][g][scrutin['vote'][g]['sort']])/scrutin['vote'][g]['total_votants']))
        }
    return dict(scrutin=scrutin, groupes=groupes)



def suivifi():
    groupes = [(g['libelleAbrev'],g['libelle'],g['nbmembres']) for g in mdb.organes.find({'$and':[{'codeType':'GP'},{'viMoDe_dateFin':None}]})]
    suivi = {}
    scrutins = sorted(mdb.scrutins.find(),key=lambda x:x['scrutin_num'])
    nuls = [ i for i,s in enumerate(scrutins) if s['votefi']==s['voteem']]
    for g,lib,nbm in groupes:
        suivi[g] = {}
        suivi[g]['votefi'] = []
        suivi[g]['voteem'] = []
        for i,s in enumerate(scrutins):
             suivi[g]['votefi'].append(s['vote'][g][s['votefi']] if s['votefi']!=s['voteem'] else 0)
             
              
    return dict(groupes=groupes,suivi=suivi,scrutins=scrutins,nuls=nuls,legende="Nombre de votants exprimés FI-compatibles - par scrutins")

def suivi():
    groupes = [(g['libelleAbrev'],g['libelle'],g['nbmembres']) for g in mdb.organes.find({'$and':[{'codeType':'GP'},{'viMoDe_dateFin':None}]})] + [('assemblee','Assemblée',577)]
    suivi = {}
    scrutins = sorted(mdb.scrutins.find(),key=lambda x:x['scrutin_num'])
    nuls = [ 1 if s['votefi']==s['voteem'] else 0 for i,s in enumerate(scrutins) ]
    for g,lib,nbm in groupes:
        suivi[g] = {}
        suivi[g]['votefi'] = []
        suivi[g]['voteem'] = []
        for i,s in enumerate(scrutins):
             suivi[g]['votefi'].append(s['vote'][g][s['votefi']])
             
              
    return dict(groupes=groupes,suivi=suivi,scrutins=scrutins,nuls=nuls,legende="Nombre de votants exprimés FI-compatibles - par scrutins")

def suivipct():
    groupes = [(g['libelleAbrev'],g['libelle'],g['nbmembres']) for g in mdb.organes.find({'$and':[{'codeType':'GP'},{'viMoDe_dateFin':None}]})] + [('assemblee','Assemblée',577)]
    suivi = {}
    scrutins = sorted(mdb.scrutins.find(),key=lambda x:x['scrutin_num'])
    nuls = [ 1 if s['votefi']==s['voteem'] else 0 for i,s in enumerate(scrutins) ]
    for g,lib,nbm in groupes:
        suivi[g] = {}
        suivi[g]['votefi'] = []
        suivi[g]['voteem'] = []
        for i,s in enumerate(scrutins):
             suivi[g]['votefi'].append(100*float(s['vote'][g][s['votefi']])/nbm)
             
              
    return dict(groupes=groupes,suivi=suivi,scrutins=scrutins,nuls=nuls,legende="% de votants exprimés FI-compatibles - par scrutins")

        
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
    positions_ori = {}
    dossiers= {'tous':{'n':0,'votefi':0,'voteem':0}}
    stats = {'n':votes.count(),'pour':0,'contre':0,'abstention':0,'nonVotant':0,'absent':0,'votefi':0,'voteem':0,'diss':0,'exprime':0,'voteempct':0,'votefipct':0,'disspct':0}
    for v in votes:
        if v['position'] in ['pour','contre','abstention']:
            #positions[v['scrutin_id']] = v['position']
            stats['exprime'] += 1
        positions[v['scrutin_id']] = v['position']
        positions_ori[v['scrutin_id']] = v['position_ori']
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
        
        mots = mdb.mots.find_one({'acteur_id':a_id})
        if mots: 
            mots = [ [mot,count] for mot,count in sorted(mots['mots'],key=lambda x:x[1],reverse=True) ][:200]
            mx = mots[0][1]
            mots = [ [mot,int(100*float(count)/mx)] for mot,count in mots]
        else:
            mots = []
        
        interventions = list(mdb.interventions.find({'acteur':a_id}))
                          
    return dict(stats=dep['statsvote'],scrutins=scrutins_dossiers,positions=positions,positions_ori=positions_ori,dossiers=dossiers,mots=mots,interventions=interventions, **dep)
