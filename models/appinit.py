# -*- coding: utf-8 -*-

import locale
locale.setlocale(locale.LC_ALL, 'fr_FR.utf8')
import pymongo

client = pymongo.MongoClient('mongodb://localhost:27017/')
mdb = client.obsas



def getVoteData_fct(idaxe,filtres):
    pos_icons = { 'pour':'thumbs-up', 'contre':'thumbs-down', 'abstention':'meh-o', 'nonVotant':'ban', 'absent':'plane','voteem':'','votefi':'','autres':''}
    pos_libelles = { 'pour':'votes pour', 'contre':'votes contre', 'abstention':'abstention', 'nonVotant':'non votants (justifiés)', 'absent':'absents',
                     'voteem':'EM-Compatibilité','votefi':'FI-Compatibilité','autres':'Autre'}


    filters = {}
    for a in axes:
        axedef = axes[a]['source']
        filters[a] = {'$or':[ { axes[a]['votes']['field']:f} for f in filtres[a] ]} if (a in filtres.keys() and filtres[a]!=[]) else {}

    axefilter = {'$or':[ { 'key':f} for f in filtres[idaxe] ]} if (idaxe in filtres.keys() and filtres[idaxe]!=[]) else {}
    
    axe = axes[idaxe]
    source = axe['source']

    def getVoteData():

        

        if idaxe == 'depute':
            #groupes = cache.disk('groupes',lambda:dict((g['uid'],g) for g in mdb.organes.find({'codeType':'GP','actif':True})),time_expire=24*3600)
            #acteurs = cache.disk('acteurs',lambda:dict((a['uid'],a) for a in mdb.acteurs.find()),time_expire=24*3600)
            groupes = appcache.getcached('groupes')
            acteurs = appcache.getcached('acteurs')

            
        scrutins = appcache.getcached('scrutins')
        if any(filters.values()):
            req = {'$and': [ f for f in filters.values() if f!={}]}
        else:
            req = {}
        nbscrutins = len(mdb.votes.distinct('scrutin_id', req))
        nbdeputes = len(mdb.votes.distinct('uid',req))

        axefiltered = mdb.votes.distinct(axe['votes']['field'],req)
        
        _items = [ it for it in mdb['axe_'+idaxe].find(axefilter) if it['key'] in axefiltered ]
       
        items = []
    
        for item in _items:
            if idaxe == 'depute':
                item['groupe_libelle'] = groupes[acteurs[item['key']]['groupe']]['libelle']
                item['groupe_abrev'] = groupes[acteurs[item['key']]['groupe']]['libelleAbrev']

            #itemreq = {axe['votes']['field']:item['key']}
            itemreq = {axe['votes']['field']:item['key']}		
            req = {'$and': [ itemreq ] + [ f for f in filters.values() if f!={}]}		
            votes = {}
            nb = {'absent':0,'nonVotant':0,'pour':0,'contre':0,'abstention':0}
            sim = {'voteem':0,'votefi':0}
            result = mdb.votes.find(req)
            if result.count() == 0:
                continue
            
            for vote in result:
                votes[vote['position']] = votes.get(vote['position'],[]) + [ vote['uid'] ]
                nb[vote['position']] +=  1
                for _sim in sim.keys():
                    if (vote['position'] == scrutins[vote['scrutin_id']][_sim]):
                        sim[_sim] += 1

            if nbscrutins==1:
                item['votes'] = votes
            item['nb'] = nb
            item['deputes'] = sum(nb.values())/nbscrutins
            total_exprime = nb['pour'] + nb['contre'] + nb['abstention']
            total = total_exprime + nb['absent'] + nb['nonVotant']
            item['votants'] = round(float(total_exprime)/nbscrutins,1)
            item['participation'] = round(100*float(total_exprime) / (total_exprime + nb['absent']),1) if total_exprime+nb['absent']>0 else '-'
            item['stats'] = {'exprime':{},'tous': {},'fiemcpt':{}}
            sim['autres'] = total_exprime-sum(sim.values())
            for pos in ['voteem','votefi','autres']:
                item['stats']['fiemcpt'][pos]={'n':round(float(sim[pos])/nbscrutins,1),'ntot':sim[pos],
                                               'position':pos,
                                               'libelle':pos_libelles[pos],
                                               'pct':round(100*float(sim[pos])/total_exprime,1) if total_exprime>0 else '-',
                                               'class':'pct','icon':pos_icons[pos]}

            for pos in ['pour','contre','abstention']:
                item['stats']['exprime'][pos]={'n':round(float(nb[pos])/nbscrutins,1),'ntot':nb[pos],
                                               'position':pos,
                                               'libelle':pos_libelles[pos],
                                               'pct':round(100*float(nb[pos])/total_exprime,1) if total_exprime>0 else '-',
                                               'class':'pct','icon':pos_icons[pos]}
            for pos in ['pour','contre','abstention','absent','nonVotant']:
                item['stats']['tous'][pos]= {'position':pos,'n':round(float(nb[pos])/nbscrutins,1),'ntot':nb[pos], 'libelle':pos_libelles[pos],'pct':round(100*float(nb[pos])/total,1),'class':'pct','icon':pos_icons[pos]}

            # chercher le max
            result = max(item['stats']['exprime'].values(),key=lambda x:x['ntot'])

            item['resultpos'] = result['position']
            for k in item['stats'].keys():
                max(item['stats'][k].values(),key=lambda x:x['ntot'])['class'] += 'Big'
            #item['stats


            # cercles
            item['cercles'] = []
            #<a class="vcircle {{position}}" title="{{nom}}" href="acteurs/{{uid}}.html" ></a>
            items.append(item)

        return dict(items=items,nbscrutins=nbscrutins,nbdeputes=nbdeputes)
    return getVoteData




import datetime
import hashlib
import pickle
import short_url

class TinyURL:
    def __init__(self,db):
        self.db = db
        self.tiny = db.tinyurl
        self.tiny.profiles.create_index([('hash',pymongo.ASCENDING)],unique=True)
        self.tiny.profiles.create_index([('_uid',pymongo.ASCENDING)],unique=True)
        if self.db.tiny_counter.count()==0:
            db.tiny_counter.insert({'_id': "tinyid", 'seq': 0})
    def getNextSequence(self,collection,name):
        return collection.find_and_modify(query= { '_id': name },update= { '$inc': {'seq': 1}}, new=True ).get('seq');
    def get(self,sid):
        _uid = short_url.decode_url(sid)
        r = self.tiny.find_one({'_uid':_uid})
        return r['params'] if r else None
        
    def set(self,params):
        hash = hashlib.md5(pickle.dumps(params)).hexdigest()
        r = self.tiny.find_one({'hash':hash})
        if r:
            _uid = r['_uid']
        else:
            _uid = self.getNextSequence(self.db.tiny_counter,"tinyid")
            self.tiny.insert({'_uid': _uid, 'params': params,'hash':hash})
        sid = short_url.encode_url(_uid)
        return sid

class AppCache:
    def __init__(self,db,name):
        self.db = db
        self.cachedb = db[name]
        self.cachedb.profiles.create_index([('hash', pymongo.ASCENDING)], unique=True)
        self.fct_cache = {}
    def getcached(self,id):
        return self.cachedb.find_one({'id':id})['data']
    def get(self,id,fct,params={}):
        self.fct_cache[id] = fct
        value = self.cachedb.find_one({'id':id})
        if value:
            return value['data']
        return self.set(id,fct,params)
    def set(self,id,fct,params={}):
        record = {'id':id,'timestamp':datetime.datetime.now(),'data':fct(**params)(),'params':params}
        self.cachedb.update({'id':id},{'$set': record },upsert=True)
        return record['data']
    def clear(self):
        self.cachedb.remove()
    
appcache = AppCache(mdb,'cache_obsas')#+request.application)
tinyurl = TinyURL(mdb)
