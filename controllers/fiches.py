# -*- coding: utf-8 -*-
# essayez quelque chose comme
# TODO : page député les scrutins avec votes identiques FI/EM doivent apparaitre de la couleur du groupe du député si EM/FI

def gauges():
    return dict()
def dashlet_template_mouvements(**kwargs):
    return XML(response.render('dashlets/mouvements.html',kwargs))

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
            
                
    if 'amendement' in scrutin['scrutin_desc'][:13]:
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
        if scrutin['vote'][g]['total_votants']==0:
            scrutin['vote'][g]['stats'] = {'exprimepct':(0,0,0),'votefipct':(0,0,0),'voteempct':(0,0,0),'disspct':(0,0,0)}
        else:
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
    import datetime
    scrutins_dossiers = OrderedDict()
    calendrier = {}
    for s in scrutins:
        # calendrier
        poss = positions[s['scrutin_id']]
        cdat = datetime.datetime.strptime(s['scrutin_date'],'%d/%m/%Y').strftime('%Y-%m-%d')
        if not cdat in calendrier.keys():
            calendrier[cdat] = {'n':0,'v':0}
        calendrier[cdat]['n'] += 1 if poss!='nonVotant' else 0
        calendrier[cdat]['v'] += 1 if not poss in ['absent','nonVotant'] else 0
        
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

        itvs = sorted(list(mdb.interventions.find({'acteur':a_id})),key=lambda x:(x['date'],-x['n']),reverse=True)

    calendrier = sorted([ dict(date=k,pct=float(v['v'])/v['n']) for k,v in calendrier.iteritems() if v['n']>0],key=lambda x:x['date']) 
    
    return dict(calendrier=calendrier,stats=dep['statsvote'],scrutins=scrutins_dossiers,positions=positions,positions_ori=positions_ori,dossiers=dossiers, itvs=itvs, **dep)


def nuages():
    lex = 'verbs' if request.args(0) == 'verbes' else 'noms'
    groupes = []
    for abrev,lib,nbm in [(g['libelleAbrev'],g['libelle'],g['nbmembres']) for g in mdb.organes.find({'$and':[{'codeType':'GP'},{'viMoDe_dateFin':None}]})] + [('assemblee','Assemblée',577)]:
        mots = mdb.mots.find_one({'acteur_id':abrev})
        groupes.append({'code':abrev,'libelle':lib,'nbmembres':nbm,'mots':mots['mots'][lex]}) 
    return dict(groupes=groupes)

def interventions():
    groupes = list(mdb.organes.find({'$and':[{'codeType':'GP'},{'viMoDe_dateFin':None}]}))
    itvs = 0
    mots = 0
    for g in groupes:
        itvs += g['nbitv']
        mots += g['nbmots']
    for g in groupes:
        g['ratio_itv'] = round((float(g['nbmots'])/mots)/(float(g['nbmembres'])/577),1)
        g['ratio_mots'] = round((float(g['nbitv'])/itvs)/(float(g['nbmembres'])/577),1)

    return dict(test=[(g['libelle'],g['ratio_itv'],g['ratio_mots']) for g in groupes],groupes=groupes,colors=[ colors[g['libelleAbrev']] for g in groupes])

def groupes():
    
    groupes = list(mdb.organes.find({'$and':[{'codeType':'GP'},{'viMoDe_dateFin':None}]}))
    tops = {'participation':[],'dissidence':[],'votefi':[],'voteem':[],'mots':[],'interventions':[]}
    for g in groupes:
            tops['participation'].append((g['libelle'],g['libelleAbrev'],round(100*float(g['statsvote']['exprime'])/g['statsvote']['n'],1)))
            tops['dissidence'].append((g['libelle'],g['libelleAbrev'],round(100*float(g['statsvote']['diss'])/g['statsvote']['exprime'],1)))
            tops['voteem'].append((g['libelle'],g['libelleAbrev'],round(100*float(g['statsvote']['voteem'])/g['statsvote']['exprime'],1)))
            tops['votefi'].append((g['libelle'],g['libelleAbrev'],round(100*float(g['statsvote']['votefi'])/g['statsvote']['exprime'],1)))
            tops['mots'].append((g['libelle'],g['libelleAbrev'],g['nbmots']/g['nbmembres']))
            tops['interventions'].append((g['libelle'],g['libelleAbrev'],g['nbitv']/g['nbmembres']))

    _tops = [{'titre':'Participation','icon':'vote','key':'participation','reverse':True,'unit':'%'},
            {'titre':'Dissidence','icon':'diss','key':'dissidence','reverse':True,'unit':'%'},
            {'titre':'FI-compatibilité','icon':'compfi','key':'votefi','reverse':True,'unit':'%'},
            {'titre':'EM-compatibilité','icon':'compem','key':'voteem','reverse':True,'unit':'%'},
            {'titre':'Mots par député','icon':'microphone','key':'mots','reverse':True,'unit':''},
            {'titre':'Interventions par député','icon':'microphone','key':'interventions','reverse':True,'unit':''},
           ]
    return dict(tops=tops,groupes=groupes,_tops=_tops)

def groupe():
    id = request.vars.get('id','welou')
    groupe = mdb.organes.find_one({'libelleAbrev':id})
    if not groupe:
        redirect(URL(c='default',f='notfound'))
    acteurs = list(mdb.acteurs.find({'uid':{'$in':groupe['membres'].keys()}}))
    tops = {}
    tops['participation'] = sorted([ (a,a['statsvote']['exprimepct']) for a in acteurs if a['statsvote']['exprime']>0],key=lambda x:x[1],reverse=True)
    tops['dissidence'] = sorted([ (a,a['statsvote']['disspct']) for a in acteurs if a['statsvote']['exprime']>15],key=lambda x:x[1],reverse=True)
    tops['voteem'] = sorted([ (a,a['statsvote']['voteempct']) for a in acteurs if a['statsvote']['exprime']>15],key=lambda x:x[1],reverse=True)
    tops['votefi'] = sorted([ (a,a['statsvote']['votefipct']) for a in acteurs if a['statsvote']['exprime']>15],key=lambda x:x[1],reverse=True)
    tops['mots'] = sorted([ (a,a['nbmots']) for a in acteurs ],key=lambda x:x[1],reverse=True)
    tops['interventions'] = sorted([ (a,a['nbitv']) for a in acteurs ],key=lambda x:x[1],reverse=True)
    
    _tops = [{'titre':'Participation','icon':'vote','key':'participation','unit':'%'},
            {'titre':'Dissidence','icon':'diss','key':'dissidence','unit':'%'},
            {'titre':'FI-compatibilité','icon':'compfi','key':'votefi','unit':'%'},
            {'titre':'EM-compatibilité','icon':'compem','key':'voteem','unit':'%'},
            {'titre':'Mots par député','icon':'microphone','key':'mots','unit':''},
            {'titre':'Interventions par député','icon':'microphone','key':'interventions','unit':''},
           ]
    return dict(acteurs=acteurs,tops=tops,_tops=_tops,**groupe)
