# -*- coding: utf-8 -*-
# essayez quelque chose comme

import os
import json
import datetime
import csv
import requests
from tools import normalize
from pymongo import UpdateOne
from bson.son import SON
import xmltodict
mdb = client.obsass
output_path = os.path.join(request.folder, 'private', 'scrapy')

# ---------------------
# Helpers
# ---------------------
def updatePhotos():
    for d in mdb.deputes.find():
        r =requests.get('http://www2.assemblee-nationale.fr/static/tribun/15/photos/'+d['depute_uid'][2:]+'.jpg')
        with open(os.path.join(request.folder, 'static', 'images','deputes',d['depute_id']+'.jpg'),'w') as f:
            f.write(r.content)
    return 'ok'

def formatpct(n,d,prec=1):
    return round(float(n)/d,prec)
def updateCircos():
    paris = ['077-01','077-02','077-03','077-04','077-05','077-06','077-07','077-08','077-09','077-10','077-11','078-01','078-02','078-03','078-04','078-05','078-06','078-07','078-08','078-09','078-10','078-11','078-12','091-01','091-02','091-03','091-04','091-05','091-06','091-07','091-08','091-09','091-10','095-01','095-02','095-03','095-04','095-05','095-06','095-07','095-08','095-09','095-10','092-01','092-02','092-03','092-04','092-05','092-06','092-07','092-08','092-09','092-10','092-11','092-12','092-13','093-01','093-02','093-03','093-04','093-05','093-06','093-07','093-08','093-09','093-10','093-11','093-12','094-01','094-02','094-03','094-04','094-05','094-06','094-07','094-08','094-09','094-10','094-11','075-01','075-02','075-03','075-04','075-05','075-06','075-07','075-08','075-09','075-10','075-11','075-12','075-13','075-14','075-15','075-16','075-17','075-18']
    villes = ['075-01','075-02','075-03','075-04','075-05','075-06','075-07','075-08','075-09','075-10','075-11','075-12','075-13','075-14','075-15','075-16','075-17','075-18','069-01','069-02','069-03','069-04','069-06','069-07','069-12','069-14','013-01','013-02','013-03','013-04','013-05','013-06','013-07','044-01','044-02','033-01','033-02','033-03','031-01','031-04','006-01','006-03','067-01','067-02','067-03','059-01','059-02','059-04','059-07','059-08','059-09','059-10']
    circopath = os.path.join(request.folder, 'private','circonscriptions_france2.svg')
    svg = xmltodict.parse(open(circopath,'r'))
    for c in svg['svg']['path']:
        circo = dict(ville=(c['@id'] in villes),paris=(c['@id'] in paris),carte='france',d=c['@d'],id=c['@id'],dep=c['@id'].split('-')[0],title=c['title']['#text'],desc=c['desc']['#text'])
        mdb.circonscriptions.update({'id':c['@id']},{'$set':circo},upsert=True)
    return "ok"
def test():

    circos = list(mdb.circonscriptions.find())


    return dict(circos=circos)

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

def buildIndexes():
    mdb.deputes.ensure_index([("depute_nom", pymongo.TEXT)],default_language='french')
    mdb.deputes.ensure_index([("depute_nom_sort", pymongo.ASCENDING)])
    mdb.deputes.ensure_index([("depute_nom_sort", pymongo.DESCENDING)])
    mdb.deputes.reindex()


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
    mdb.groupes.update_many({'groupe_mots':None},{'$set':{'groupe_mots':{}}})
    mdb.deputes.update_many({'depute_mots':None},{'$set':{'depute_mots':{}}})

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
        mdb.groupes.update_many({},{'$set':{'groupe_mots':{},'groupe_nuages':{},'stats.nbmots':0,'stats.nbitvs':0}})
    
    
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
    #launchScript('sessions',"'%s'" % (json.dumps(exclude)))
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


    deputes = dict((a['depute_id'],{'gp':a['groupe_abrev'],'uid':a['depute_uid'],'mots':a['depute_mots'],'stats':a['stats']}) for a in mdb.deputes.find())
    groupes = dict((g['groupe_abrev'], {'mots':g['groupe_mots'], 'stats':g['stats']}) for g in mdb.groupes.find())
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
                _dep = deputes[new_itv['depute_id']]
                _dep['stats']['nbmots'] += new_itv['itv_nbmots']
                _dep['stats']['nbitvs'] += 1
                addWords(_dep['mots'],new_itv['mots'])
                _grp = groupes[_dep['gp']]
                _grp['stats']['nbmots'] += new_itv['itv_nbmots']
                _grp['stats']['nbitvs'] += 1
                addWords(_grp['mots'],new_itv['mots'])

    for gid,g in groupes.iteritems():
        mdb.groupes.update_one({'groupe_abrev':gid},
                               {'$set':{'groupe_mots':groupes[gid]['mots'],
                                         'groupe_nuages':genNuages(groupes[gid]['mots']),
                                         'stats':groupes[gid]['stats']}})

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
    groupe_depute = dict((d['depute_uid'],d['groupe_abrev']) for d in mdb.deputes.find())
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
        dep['depute_positions']['dissidence'] = dep['depute_positions']['exprimes'] - dep['depute_compat'][groupe_depute[uid]]

        # stats positions
        dep['stats.positions'] = dict((p,0) for p in ('pour','contre','exprimes','absent','abstention','dissidence'))
        for pos in dep['stats.positions'].keys():
            if dep['depute_positions']['exprimes']>0:
                dep['stats.positions'][pos] = round(100*float(dep['depute_positions'].get(pos,0)) / dep['depute_positions']['total'],1)
        # stats compat
        dep['stats.compat'] = dict((g,0) for g in dep['depute_compat'].keys())
        for g,v in dep['depute_compat'].iteritems():
            if dep['depute_positions']['exprimes']>0:
                dep['stats.compat'][g] = round(100*float(v) / dep['depute_positions']['exprimes'],1)
        dep['stats.compat_sort'] = [ dict(g=g,p=p) for g,p in sorted(dep['stats.compat'].items(), key=lambda x:x[1], reverse=True) ]
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

def updateGroupesStats():
    #pipeline = [
    #    {"$group":{'_id': {'groupe':'$groupe_abrev','csp':'$depute_csp'}, 'n':{'$sum':1}}},
    #    {"$sort": SON([("n",-1)])}
    #]
    #return json.dumps(list(mdb.deputes.aggregate(pipeline)))
    pgroup = dict((g,{'$sum':'$vote_compat.'+g}) for g in mdb.groupes.distinct('groupe_abrev'))
    pgroup['_id'] = {'groupe':'$groupe_abrev'}
    pipeline = [
        {"$group": pgroup },
    ]
    groupes = {}
    for compat in list(mdb.votes.aggregate(pipeline)):
        groupe = compat['_id']['groupe']
        del compat['_id']
        groupes[groupe] = {'groupe_compat':compat, 'groupe_positions':{} }
    
    pipeline = [
        {"$group":{'_id': {'groupe':'$groupe_abrev','position':'$vote_position'}, 'n':{'$sum':1}}},
        {"$sort": SON([("_id.groupe",1)])}
    ]

    for p in list(mdb.votes.aggregate(pipeline)):
        gid = p['_id']['groupe']
        groupes[gid]['groupe_positions'][p['_id']['position']] = p['n']
    ops = []
    for gid,g in groupes.iteritems():
        g['groupe_positions']['total'] = sum(g['groupe_positions'].values())
        g['groupe_positions']['exprimes'] = g['groupe_positions']['total'] - g['groupe_positions'].get('absent',0)
        g['groupe_positions']['dissidence'] = g['groupe_positions']['exprimes'] - g['groupe_compat'][gid]

        # stats positions
        g['stats.positions'] = dict((p,0) for p in ('pour','contre','exprimes','absent','abstention','dissidence'))
        for pos in g['stats.positions'].keys():
            if g['groupe_positions']['exprimes']>0:
                g['stats.positions'][pos] = round(100*float(g['groupe_positions'].get(pos,0)) / g['groupe_positions']['total'],1)
        # stats compat
        g['stats.compat'] = dict((_g,0) for _g in g['groupe_compat'].keys())
        for _g,_v in g['groupe_compat'].iteritems():
            if g['groupe_positions']['exprimes']>0:
                g['stats.compat'][_g] = round(100*float(_v) / g['groupe_positions']['exprimes'],1)
        g['stats.compat_sort'] = [ dict(g=_g,p=_p) for _g,_p in sorted(g['stats.compat'].items(), key=lambda x:x[1], reverse=True) ]
        ops.append(UpdateOne({'groupe_abrev':gid},{'$set':g}))

    if ops:
        mdb.groupes.bulk_write(ops)

    return json.dumps(groupes)
