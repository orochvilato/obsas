# -*- coding: utf-8 -*-
# essayez quelque chose comme
import tools
import pymongo

def test():
    savecache=[dict(id=c['id'],params=c['params']) for c in appcache.cachedb.find()]
    appcache.clear()
    for r in savecache:
        print r
        appcache.get(r['id'],getVoteData_fct,params=r['params'])
    return dict(t=t)

def clear_cache():
    appcache.clear()
    rebuild_cache()
    
def rebuild_cache():
    savecache=[dict(id=c['id'],params=c['params']) for c in appcache.cachedb.find()]
    appcache.clear()
    
    def getGroupesDict():
        return dict((g['uid'],g) for g in mdb.organes.find({'codeType':'GP','actif':True}))
    def getActeursDict():
        return dict((a['uid'],a) for a in mdb.acteurs.find())
    def getScrutinsDict():
        return dict((s['scrutin_id'],s) for s in mdb.scrutins.find())


    appcache.set('groupes',lambda:getGroupesDict,params={})
    appcache.set('acteurs',lambda:getActeursDict,params={})
    appcache.set('scrutins',lambda:getScrutinsDict,params={})
    for r in savecache:
        print r
        appcache.get(r['id'],getVoteData_fct,params=r['params'])
    
def update_emfi_compat():
    scrutins = mdb.scrutins.find({'vote':None})
    groupes = [g['libelleAbrev'] for g in mdb.organes.find({'$and':[{'codeType':'GP'},{'viMoDe_dateFin':None}]})]
    
    for s in scrutins:
        votes = mdb.votes.find({'scrutin_id':s['scrutin_id']})
        
        exprime=dict((g,{'pour':0,'contre':0,'abstention':0}) for g in groupes+['assemblee'])
        nonexprime=dict((g,{'nonVotant':0,'absent':0}) for g in groupes+['assemblee'])
        for v in votes:
            if v['position'] in ['pour','contre','abstention']:
                exprime[v['groupeabrev']][v['position']] += 1
                exprime['assemblee'][v['position']] += 1
            else:
                nonexprime[v['groupeabrev']][v['position']] += 1
                nonexprime['assemblee'][v['position']] += 1
                
        s['scrutin_desc'] = s['scrutin_desc'].replace('. [','.')
        s['scrutin_fulldesc'] = s['scrutin_fulldesc'].replace('. [','.')
        for g in groupes+['assemblee']:
            exprime[g]['sort'] = max(exprime[g].items(),key=lambda x:x[1])[0]
            exprime[g]['participation'] = round(100*float(exprime[g]['pour']+exprime[g]['contre']+exprime[g]['abstention'])/(exprime[g]['pour']+exprime[g]['contre']+exprime[g]['abstention']+nonexprime[g]['nonVotant']+nonexprime[g]['absent']))
            exprime[g].update(nonexprime[g])
        
         
        
        s['votefi'] = exprime['FI']['sort']
        s['voteem'] = exprime['REM']['sort']
        s['vote'] = exprime
        mdb.scrutins.update({'scrutin_id':s['scrutin_id']},{'$set':s})
        
def update_axes():
    axe_all = {}
    for axe in axes:
        source = axes[axe]['source']
        items = [ {'key':item[0],'label':item[1]} for item in list(set([(item[source['key']],item[source['label']]) for item in mdb[source['nom']].find(source['filtre'])]))]
        items = list(mdb[source['nom']].find(source['filtre']))
        uniqueitems = list(set([(item[source['key']],item[source['label']]) for item in items]))
        if len(uniqueitems) == len(items):
            axe_all[axe] = []
            for item in items:
                it = {'key':item[source['key']],'label':item[source['label']]}
                item.update(it)
           
        else:
            items =  [{'key':item[0],'label':item[1]} for item in uniqueitems]
           
        items.sort(key=lambda x:sortfcts[axes[axe]['tri_defaut'][0]]['fct']({},x),reverse=axes[axe]['tri_defaut'][1])
        axe_all[axe] = [{'key':it['key'],'label':it['label']} for it in items]
        mdb['axe_'+axe].remove()
        mdb['axe_'+axe].insert_many(items)
        
    
    mdb['axes'].remove()
    mdb['axes'].insert(axe_all)

def fetch_acteurs_organes():
    from sources.hatvp import declarations
    from sources.deputywatch import deputywatch
    from sources.acteurs_organes import getActeursOrganes

    
    # Acteurs et organes
    actorg = getActeursOrganes()

    mdb.acteurs.create_index([('uid', pymongo.ASCENDING)], unique = True)
    bulk = mdb.acteurs.initialize_unordered_bulk_op()
    for act in actorg['acteurs'].values():
        bulk.find({'uid':act['uid']}).upsert().replace_one(act)
    result = bulk.execute()
   
    
    mdb.organes.create_index([('uid', pymongo.ASCENDING)], unique = True)
    bulk = mdb.organes.initialize_unordered_bulk_op()
    for org in actorg['organes'].values():
        bulk.find({'uid':org['uid']}).upsert().replace_one(org)
    result = bulk.execute()

def fetch_scrutins():
    # Scrutins et votes
    from sources.scrutins import getScrutins    
    #mdb.votes.remove()
    #mdb.scrutins.remove()
    scrutinscomplets = [ s['scrutin_id'] for s in list(mdb.scrutins.find({'$and':[{'scrutin_dossier':{'$ne':'N/A'}},{'scrutin_type':{'$ne':'N/A'}}]}))]
    acteurs = dict((a['id'],a) for a in mdb.acteurs.find())
    
    scr = getScrutins(acteurs,scrutinscomplets)
    scrutinsincomplets = [ s['scrutin_id'] for s in list(mdb.scrutins.find({'$or':[{'scrutin_dossier':'N/A'},{'scrutin_type':'N/A'}]}))]
    
    print "remove",scrutinsincomplets
    mdb.votes.remove({'scrutin_id':{'$in':scrutinsincomplets}})
    mdb.scrutins.remove({'scrutin_id':{'$in':scrutinsincomplets}})
    
    # stockage des votes et des scrutins dans la base
    if scr['votes']:
        mdb.votes.create_index([('vote_id', pymongo.ASCENDING)], unique = True)
        #mdb.votes.insert_many(scr['votes'])
        for s in scr['votes']:
            mdb.votes.insert(s)

    if scr['scrutins']:
        mdb.scrutins.create_index([('scrutin_id', pymongo.ASCENDING)], unique = True)
        mdb.scrutins.insert_many(scr['scrutins'])

def update_acteurs_stats():
    
    deputes = mdb.acteurs.find()
    for dep in deputes:
        dep['iddepartement'] = departements[dep['departement']]
        dep['idcirco'] = dep['iddepartement']+'-'+('00'+dep['circo'])[-2:]
        votes = mdb.votes.find({'uid':dep['uid']})
        positions = {}
        dossiers= {'tous':{'n':0,'votefi':0,'voteem':0}}
        stats = {'n':votes.count(),'pour':0,'contre':0,'abstention':0,'nonVotant':0,'absent':0,'votefi':0,'voteem':0,'diss':0,'exprime':0,'voteempct':0,'votefipct':0,'disspct':0}
        for v in votes:
            if v['position'] in ['pour','contre','abstention']:
                stats['exprime'] += 1
            positions[v['scrutin_id']] = v['position']
            stats[v['position']] += 1
        stats['exprimepct'] = int(100*float(stats['exprime'])/stats['n']) if stats['nonVotant']!=stats['n'] else '-'
        scrutins = sorted(list(mdb.scrutins.find({'scrutin_id':{'$in':positions.keys()}})),key=lambda x:x['scrutin_num'],reverse=True)
        
        from collections import OrderedDict
        scrutins_dossiers = OrderedDict()
        for s in scrutins:
            diss = ( positions[s['scrutin_id']] != s['vote'][dep['groupe_abrev']]['sort']) and (not positions[s['scrutin_id']] in ['absent','nonVotant'])
            if diss:
                stats['diss'] += 1
    
            for p in ['votefi','voteem']:
                if positions[s['scrutin_id']] == s[p]:
                    stats[p] += 1

            s['flag'] = diss
            stats['disspct'] =  int(100*float(stats['diss'])/stats['exprime']) if stats['exprime']>0 else '-'
            stats['votefipct'] =  int(100*float(stats['votefi'])/stats['exprime']) if stats['exprime']>0 else '-'
            stats['voteempct'] =  int(100*float(stats['voteem'])/stats['exprime']) if stats['exprime']>0 else '-'
        dep['statsvote'] = stats
        mdb.acteurs.update({'uid':dep['uid']},{'$set':dep})
        #print dep['nomcomplet'].encode('utf8')
    
    
def index():
    
    fetch_acteurs_organes()
    fetch_scrutins()
    update_axes()
    update_emfi_compat()
    update_acteurs_stats()
    rebuild_cache()
    return dict()
