# -*- coding: utf-8 -*-
# essayez quelque chose comme

import os
import json
import datetime
import csv
from tools import normalize
from pymongo import UpdateOne
from bson.son import SON

mdb = client.obsass
output_path = os.path.join(request.folder, 'private', 'scrapy')


# ---------------------
# Helpers
# ---------------------
def formatpct(n,d,prec=1):
    return round(float(n)/d,prec)
def test():
    d = mdb.deputes.find_one({'depute_uid':'PA610667'})
    del d['_id']
    
    return json.dumps(d)

def launchScript(name,params=""):
    fp = os.path.join(request.folder, 'private/scripts', name +'.py '+output_path+' '+params)
    
    did_scrape = True
    if not 'debug' in request.args:
        did_scrape = True if os.system(fp) else False

    return did_scrape

def getData(name,id):
    fp = os.path.join(request.folder, 'private/data/', name +'.csv')
    with open(fp) as csvfile:
        reader = csv.DictReader(csvfile,delimiter='|')
        result = dict((row[id].decode('utf8'),dict((k,v.decode('utf8')) for k,v in row.iteritems())) for row in reader)
    return result
def addData(name,elts):
    fp = os.path.join(request.folder, 'private/data/', name +'.csv')
    with open(fp,'a') as f:
        f.write('|'.join([e.encode('utf8') for e in elts])+'\n')
    
def getJson(name):
    return json.loads(open(output_path+'/'+name+'.json','r').read())



def genNuages(_mots):
    mts = {}
    for lex in _mots.keys():
        if _mots[lex]:
            mots = [ [mot,count] for mot,count in sorted(_mots[lex].items(),key=lambda x:x[1],reverse=True) if not mot in nuages_excl][:200]
            if mots:
                mx = mots[0][1]
                mn = mots[-1][1]-1
                coef = 12000/sum([len(mot)*(float(count-mn)/(mx-mn))**2 for mot,count in mots])
                mts[lex] = [ [mot,int(coef*float(count-mn)/(mx-mn))] for mot,count in mots]
        
    return mts

# ---------------------
# Imports de données
# ---------------------

def updateAssemblee():
    updateHATVP()
    updateDeputyWatch()
    launchScript('assemblee')
    deputes = getJson('deputes')
    deputywatch = getJson('deputywatch')
    departements = getData('departements','departement')
    professions = getData('deputes_professions','id')
    professions2 = getData('deputes_professions','profession')
    hatvp = getJson('hatvp')
    csp_incomplet = []
    for d in deputes:
        d['depute_sexe'] = 'Homme' if d['depute_nom']=='M.' else 'Femme'
        d['depute_id'] = normalize(d['depute_nom'])
        d['depute_age'] = int((datetime.datetime.now() - datetime.datetime.strptime(d['depute_ddn'],'%d/%m/%Y')).days / 365.25)
        d['depute_classeage'] = '%d-%d ans' % ((d['depute_age']/10)*10,(1+(d['depute_age']/10))*10)
        d['depute_deputywatch'] = deputywatch.get(d['depute_id'],None)
        d['depute_hatvp'] = hatvp.get(d['depute_id'],[])
        d['depute_region'] = departements[d['depute_departement']]['region']
        d['depute_typeregion'] = departements[d['depute_departement']]['typeregion']
        d['depute_departement_id'] = departements_ids[d['depute_departement']]
        d['depute_circo_id'] = d['depute_departement_id']+'-'+('00'+d['depute_circo'])[-2:]
        m = professions.get(d['depute_uid'],None)
        if not m:
            m = professions2.get(d['depute_profession'],None)
        csp = ""
        if m:
            csp = m['csp']
       
        if not csp and not d['depute_uid'] in professions.keys():
            addData('deputes_professions',(d['depute_uid'],d['depute_nom'],d['depute_profession'],''))
            
        d['depute_csp'] = csp
        mdb.deputes.update_one({'depute_uid': d['depute_uid']}, {'$set': d}, upsert = True)
    
    groupes = getJson('groupes')
    for g in groupes:
        membres = mdb.deputes.find({'groupe_uid':g['groupe_uid']})
        g['groupe_membres'] = [ dict(qualite=m['groupe_qualite'],uid=m['depute_uid'],actif = m['depute_actif']) for m in membres]
        g['groupe_nbmembres'] = len([ m for m in g['groupe_membres'] if m['actif']])
        mdb.groupes.update_one({'groupe_uid':g['groupe_uid']},{'$set':g}, upsert= True)
    
    # initialise les champs stats
    mdb.deputes.update_many({'stats':None},{'$set':{'stats':{'nbmots':0,'nbitvs':0}}})
    mdb.groupes.update_many({'stats':None},{'$set':{'stats':{'nbmots':0,'nbitvs':0}}})
    
    return mdb.deputes.find().count()

def updateDeputyWatch():
    launchScript('deputywatch')

def updateHATVP():
    types_doc = {
     'dia': u'Déclaration d’intérêts et d’activités',
     'diam': u'Déclaration de modification substantielle des intérêts et des activités',
     'di': u'Déclaration d’intérêts',
     'dim': u'Déclaration de modification substantielle des intérêts',
     'dsp': u'Déclaration de situation patrimoniale',
     'dspm': u'Déclaration de modification substantielle de situation patrimoniale',
     'dspfm': u'Déclaration de modification substantielle de situation patrimoniale',
     'appreciation': u'Appréciation de la HATVP'
    }

    import requests
    import csv
    import json
    from cStringIO import StringIO
    from tools import normalize
    r = requests.get('http://www.hatvp.fr/files/open-data/liste.csv')
    f = StringIO(r.content)
    csv = csv.DictReader(f, delimiter=';', quotechar='"')
    declarations = {}
    for row in csv:
        drow = dict((k,v.decode('utf8') if isinstance(v,basestring) else v) for k,v in row.iteritems())
        id = normalize(drow['civilite']+' '+drow['prenom']+' '+drow['nom'])
        drow['docurl'] = 'http://www.hatvp.fr/livraison/dossiers/'+drow['nom_fichier']
        drow['typedoc'] = types_doc[drow['type_document']]
        declarations[id] = declarations.get(id,[])+ [drow]

    with open(output_path+'/hatvp.json','w') as f:
        f.write(json.dumps(declarations))

def updateSessions():
    if 'rebuild' in request.args:
        mdb.interventions.remove()
        mdb.deputes.update_many({},{'$set':{'depute_mots':{},'depute_nuages':{},'stats.nbmots':0,'stats.nbitvs':0}})
        
    lexiques_path = os.path.join(request.folder, 'private','lexiques.json')

    with open(lexiques_path,'r') as f:
        lexiques = json.loads(f.read())

    lexiquenoms = lexiques['NOM']
    #lexiquenoms.update(lexiques['ADV'])
    lexiquenoms.update(lexiques['ADJ'])
    lexiqueverbes = lexiques['VER']
    _lexiques = {'noms':lexiquenoms,'verbes':lexiqueverbes}
    _lex = {'noms':set(_lexiques['noms'].keys()),
            'verbes':set(_lexiques['verbes'].keys()) }

    def countWords(txt):
        words = {'noms':{},'verbes':{}}
        txt = txt.replace('\n',' ').replace('.',' ').replace(':',' ').replace(',',' ').replace(';',' ').replace('-',' ').replace('  ',' ').replace(u'\xa0','').replace(u'\u2019',' ').lower().split(' ')
        for lex in _lexiques.keys():
            _words = [ _lexiques[lex][x] for x in txt if x in _lex[lex] ]
            for w in _words:
                if not w.strip():
                    continue
                if not w in words[lex].keys():
                    words[lex][w] = 1
                else:
                    words[lex][w] += 1

        return words
    
    def addWords(w1,w2):
        for k in w2.keys():
            if not k in w1.keys():
                w1[k] = w2[k]
            else:
                for mot,n in w2[k].iteritems():
                    w1[k][mot] = w1[k].get(mot,0) + n
        
    exclude = mdb.interventions.distinct('session_id')
    launchScript('sessions',"'%s'" % (json.dumps(exclude)))
    sessions = getJson('sessions')
    scrutins = list(mdb.scrutins.find())
    for s in scrutins:
        if s['scrutin_typedetail']=='amendement' and 'scrutin_ref' in s.keys():
            cptrd = s['scrutin_ref']['urlCompteRenduRef'].split('#')[0]
            if cptrd in sessions.keys():
                balises = sessions[cptrd]
                bal = balises.get(s['scrutin_ref']['numAmend'],'')
                s['scrutin_ref']['urlCompteRenduRef'] = cptrd + '#' + bal
                mdb.scrutins.update_one({'scrutin_id': s['scrutin_id']}, {'$set': {'scrutin_ref': s['scrutin_ref']}})


    deputes = dict((a['depute_id'],{'uid':a['depute_uid'],'mots':a['depute_mots'],'stats':a['stats']}) for a in mdb.deputes.find())
    interventions = getJson('interventions')
    for itv in interventions:
        for n,depid in enumerate(itv['depute_id'].split(u'|')):
            new_itv=dict(itv)
            new_itv['depute_id'] = depid
            nid = deputes.get(depid,None)
            if nid and nid['uid'] != new_itv['depute_uid']:
                new_itv['depute_uid'] = nid['uid']
            new_itv['mots'] = countWords(new_itv['itv_contenu_texte'])
            new_itv['itv_id'] = "%s%d" % (new_itv['itv_id'],n)
            mdb.interventions.update_one({'itv_id':new_itv['itv_id']},{'$set':new_itv}, upsert=True)
            if new_itv['depute_id'] in deputes.keys():
                deputes[new_itv['depute_id']]['stats']['nbmots'] += new_itv['itv_nbmots']
                deputes[new_itv['depute_id']]['stats']['nbitvs'] += 1
                addWords(deputes[new_itv['depute_id']]['mots'],new_itv['mots'])



    for d in mdb.deputes.find():
        if d['depute_id'] in deputes.keys():
            mdb.deputes.update_one({'depute_id':d['depute_id']},
                                   {'$set':{'depute_mots':deputes[d['depute_id']]['mots'],
                                            'depute_nuages':genNuages(deputes[d['depute_id']]['mots']),
                                            'stats':deputes[d['depute_id']]['stats']}})

def updateScrutins():
    _scrutins = {}
    if 'rebuild' in request.args:
        mdb.votes.remove()
        mdb.scrutins.remove()
    
    # TODO : fonctionnalité import PDF à conserver ?
    #_scrutins = get_scrutinsPDFs()
    #fp = os.path.join(current.request.folder, 'private/scripts', 'scrutins.py')
    #did_scrape = True if os.system(fp) else False

    scrutins_complets = [ s['scrutin_id'] for s in list(mdb.scrutins.find({'$and':[{'scrutin_dossier':{'$ne':'N/A'}},{'scrutin_type':{'$ne':'N/A'}}]}))]
    launchScript('scrutins',"'"+json.dumps(scrutins_complets)+"'")
    _scrutins.update(getJson('scrutins'))

    votes = []
    scrutins = []
    
    deputes = dict((d['depute_id'],d) for d in mdb.deputes.find())
    
    def act_votedata(id,position,posori=None):
        d = deputes[id]
        return {'depute_uid':d['depute_uid'],
                'depute_nom':d['depute_nom'],
                'groupe_uid': d['groupe_uid'],
                'groupe_abrev': d['groupe_abrev'],
                'depute_age':d['depute_age'],
                'depute_classeage':d['depute_classeage'],
                'depute_region':d['depute_region'],
                'depute_typeregion':d['depute_typeregion'],
                'depute_departement':d['depute_departement'],
                'depute_csp':d['depute_csp'],
                'depute_sexe':d['depute_sexe'],
                'vote_position':position,
                'vote_position_ori':posori }

    for s in _scrutins.values():
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
        for p in s['votes'].keys():
            for v in s['votes'][p]:
                vote = dict(scrutin)
                depute = deputes.get('m.'+v,deputes.get('mme'+v,deputes.get(v,'PB')))
                if depute == 'PB':
                    print v.encode('utf8')
                else:
                    exprimes.append(depute['depute_id'])
                    if p=='nonVotant':
                        continue
                    corr = s['corrections'].get('m.'+v,s['corrections'].get('mme'+v,False))
                    if corr:
                        position = corr
                        posori = p
                    else:
                        position = p
                        posori = p
                    vote.update(act_votedata(depute['depute_id'],position,posori))
                    vote['vote_id'] = "%d_%s" % (s['num'],depute['depute_id'])
                    votes.append(vote)
        for depcorr,pos in s['corrections'].iteritems():
            if not depcorr in exprimes:
                vote = dict(scrutin)
                vote.update(act_votedata(depcorr,pos,'absent'))
                vote['vote_id'] = "%d_%s" % (s['num'],depcorr)
                votes.append(vote)
                exprimes.append(depcorr)
                    
        for id in list(set(deputes.keys())-set(exprimes)):
            datescrutin = datetime.datetime.strptime(s['date'],'%d/%m/%Y')
            depute = deputes[id]
            
            if (depute['depute_mandat_debut'] and datetime.datetime.strptime(depute['depute_mandat_debut'],'%d/%m/%Y')>datescrutin) or (depute['depute_mandat_fin'] and datetime.datetime.strptime(depute['depute_mandat_fin'],'%d/%m/%Y')<datescrutin):
                
                continue

            vote = dict(scrutin)
            vote.update(act_votedata(id,'absent'))
            vote['vote_id'] = "%d_%s" % (s['num'],id)
            votes.append(vote)
        if 'reference' in s.keys():
            scrutin.update({'scrutin_ref':s['reference']})
        scrutin.update({  'scrutin_lienscrutin':s['scrutinlien'],
                            'scrutin_liendossier':s['dossierlien'] })
        scrutins.append(scrutin)

    

    scrutins_incomplets = [ s['scrutin_id'] for s in list(mdb.scrutins.find({'$or':[{'scrutin_dossier':'N/A'},{'scrutin_type':'N/A'}]}))]

    mdb.votes.remove({'scrutin_id':{'$in':scrutins_incomplets}})
    mdb.scrutins.remove({'scrutin_id':{'$in':scrutins_incomplets}})

    # stockage des votes et des scrutins dans la base
    if votes:
        mdb.votes.create_index([('vote_id', pymongo.ASCENDING)], unique = True)
        #mdb.votes.insert_many(votes)
        for v in votes:
            mdb.votes.insert(v)

    if scrutins:
        mdb.scrutins.create_index([('scrutin_id', pymongo.ASCENDING)], unique = True)
        mdb.scrutins.insert_many(scrutins)
    
    updateScrutinsStats()
    updateDeputesStats()
        
def updateDeputesStats():
    pgroup = dict((g,{'$sum':'$vote_compat.'+g}) for g in mdb.groupes.distinct('groupe_abrev'))
    pgroup['_id'] = {'depute':'$depute_uid'}
    pipeline = [
        {"$group": pgroup },
    ]
    deputes = {}
    for compat in list(mdb.votes.aggregate(pipeline)):
        depuid = compat['_id']['depute']
        del compat['_id']
        deputes[depuid] = {'depute_compat':compat, 'depute_positions':{} }
    
    pipeline = [
        {"$group":{'_id': {'depute':'$depute_uid','position':'$vote_position'}, 'n':{'$sum':1}}},
        {"$sort": SON([("_id.depute",1)])}
    ]
    
    for p in list(mdb.votes.aggregate(pipeline)):
        uid = p['_id']['depute']
        deputes[uid]['depute_positions'][p['_id']['position']] = p['n']
    ops = []
    for uid,dep in deputes.iteritems():
        dep['depute_positions']['total'] = sum(dep['depute_positions'].values())
        dep['depute_positions']['exprimes'] = dep['depute_positions']['total'] - dep['depute_positions'].get('absent',0)
        ops.append(UpdateOne({'depute_uid':uid},{'$set':dep}))

    if ops:
        mdb.deputes.bulk_write(ops)

    return json.dumps(deputes)


def updateScrutinsStats():
    if 'rebuild' in request.args:
        mdb.votes.update_many({},{'$set':{'vote_compat':None}})

    # decomptes positions par scrutin, par groupe, par position
    pipeline = [
        {"$match":{'vote_compat':None}},
        {"$group":{'_id': {'position':'$vote_position','scrutin':'$scrutin_id','groupe':'$groupe_abrev'},'total':{'$sum':1}}}, 
        {"$sort": SON([("_id.scrutin",1),("_id.groupe",1),("total",-1),("_id.position",1)])},
        
    ]

    # Stats scrutins
    scrutins = {}

    scrutin_id = None
    for r in list(mdb.votes.aggregate(pipeline)):
        if r['_id']['scrutin'] != scrutin_id:
            scrutin_id = r['_id']['scrutin']
            scrutins[scrutin_id] = {}
            scrutins[scrutin_id]['positions'] = {'assemblee':{'pour':0,'contre':0,'abstention':0,'absent':0}}
            scrutins[scrutin_id]['compats'] = {}
            groupe = None
        position = r['_id']['position']
        if r['_id']['groupe'] != groupe:
            groupe = r['_id']['groupe']
            scrutins[scrutin_id]['positions'][groupe] = {'position':''}
            scrutins[scrutin_id]['compats'][groupe] = ''
        if position != 'absent' and scrutins[scrutin_id]['positions'][groupe]['position']=='':
            scrutins[scrutin_id]['positions'][groupe]['position'] = position
            scrutins[scrutin_id]['compats'][groupe] = position
        scrutins[scrutin_id]['positions'][groupe][position] = r['total']
        scrutins[scrutin_id]['positions']['assemblee'][position] += r['total']
    # Complements stats
    groupes = mdb.groupes.distinct('groupe_abrev')
    groupe_init = dict((abr,0) for abr in groupes+['assemblee'])
    ops = []
    for sid,scrutin in scrutins.iteritems():
        tri = sorted([(k,v) for k,v in scrutin['positions']['assemblee'].iteritems() if k!='absent'], key=lambda x:x[1], reverse=True)
        asspos = tri[0][0] if len(tri)>0 else ''
        scrutin['positions']['assemblee']['position'] = asspos
        scrutin['compats']['assemblee'] = asspos
        
        compatpos = { 'absent':groupe_init }
        for pos in ('pour','contre','abstention'):
            compatpos[pos] = dict((g,1 if scrutin['compats'][g]==pos else 0) for g in groupes+['assemblee'])
        scrutin['compatpos'] = compatpos
        for g in groupes+['assemblee']:
            scrutin['positions'][g]['exprimes'] = scrutin['positions'][g].get('pour',0) + scrutin['positions'][g].get('contre',0) + scrutin['positions'][g].get('abstention',0)
            scrutin['positions'][g]['total'] = scrutin['positions'][g]['exprimes'] + scrutin['positions'][g].get('absent',0) 
        scrutin['sort'] = u'adopté' if scrutin['positions']['assemblee']['position']=='pour' else u'rejeté'
        ops.append(UpdateOne({'scrutin_id':sid},{'$set':{'scrutin_positions':scrutin['positions'], 'scrutin_compats':scrutin['compats'], 'scrutin_sort':scrutin['sort']}}))
    
    if ops:
        mdb.scrutins.bulk_write(ops)
    ops = []
    for v in mdb.votes.find({'scrutin_id':{'$in':scrutins.keys()}}):
        ops.append(UpdateOne({'vote_id':v['vote_id']},{'$set':{'vote_compat':scrutins[v['scrutin_id']]['compatpos'][v['vote_position']]}}))
    if ops:
        mdb.votes.bulk_write(ops)        
        

    return "OK"