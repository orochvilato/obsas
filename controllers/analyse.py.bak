# -*- coding: utf-8 -*-
# essayez quelque chose comme
import json
def index():
    axe = request.vars.get('axe','groupes')
    filtres = request.vars.get('filtres',{})
    suffrages = request.vars.get('suffrages','tous')
    scrutin = request.vars.get('scrutin','tous')
    tri = request.vars.get('tri','participation')
    desc = request.vars.get('desc','1')

    return locals()

def vueaxe():
    pos_icons = { 'pour':'thumbs-up', 'contre':'thumbs-down', 'abstention':'meh-o', 'nonVotant':'ban', 'absent':'plane','voteem':'','votefi':''}
    pos_libelles = { 'pour':'votes pour', 'contre':'votes contre', 'abstention':'abstention', 'nonVotant':'non votants (justifiés)', 'absent':'absents',
                     'voteem':'EM-Compatibilité','votefi':'FI-Compatibilité'}

    idaxe = request.vars.get('axe','groupes')
    filtres = json.loads(request.vars.get('filtres','{}'))
    suffrages = request.vars.get('suffrages','tous')
    tri = request.vars.get('tri','participation')
    desc = request.vars.get('desc','1')

    

    #filtres = {}
    #if scrutin != 'tous':
    #    filtres = {'scrutin_id':'15_'+scrutin}

    # Gestion du cache
    import hashlib
    import pickle
    hash = hashlib.md5(pickle.dumps([idaxe,filtres])).hexdigest()

    filters = {}
    for a in axes:
        axedef = axes[a]['source']
        if a==idaxe:
            axefilter = {'$or':[ { 'key':f} for f in filtres[idaxe] if a in filtres.keys() ]} if a in filtres.keys() else {}

        filters[a] = {'$or':[ { axedef['key']:f} for f in filtres[a] ]} if a in filtres.keys() else {}

    axe = axes[idaxe]
    source = axe['source']
    if not tri in sortfcts_order+axe.get('tris',[]):
        tri = axe.get('tri_defaut','participation')
    
    def getVoteData():
        #items = [ {'key':item[0],'label':item[1]} for item in list(set([(item[source['key']],item[source['label']]) for item in mdb[source['nom']].find(source['filtre'])]))]

        items = list(mdb['axe_'+idaxe].find(axefilter))
        print axefilter,len(items)
        if idaxe == 'depute':
            groupes = cache.disk('groupes',lambda:dict((g['uid'],g) for g in mdb.organes.find({'codeType':'GP','actif':True})),time_expire=24*3600)
            acteurs = cache.disk('acteurs',lambda:dict((a['uid'],a) for a in mdb.acteurs.find()),time_expire=24*3600)

        nbscrutins = len(mdb.votes.distinct('scrutin_id', filters['scrutin']))
        
        scrutins = cache.disk('scrutins',lambda:dict((s['scrutin_id'],s) for s in mdb.scrutins.find()), time_expire=24*3600)

        for item in items:
            if idaxe == 'depute':
                item['groupe_libelle'] = groupes[acteurs[item['key']]['groupe']]['libelle']
                item['groupe_abrev'] = groupes[acteurs[item['key']]['groupe']]['libelleAbrev']

            itemreq = {axe['votes']['field']:item['key']}
            req = {'$and': [ itemreq ] + [ f for f in filters.values() if f!={}]}
            votes = {}
            nb = {'absent':0,'nonVotant':0,'pour':0,'contre':0,'abstention':0}
            print req
            sim = {'voteem':0,'votefi':0}
            for vote in mdb.votes.find(req):
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
            for pos in ['voteem','votefi']:
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
            result['class'] += 'Big'
            item['resultpos'] = result['position']
            for k in item['stats'].keys():
                max(item['stats'][k].values(),key=lambda x:x['ntot'])['class'] += 'Big'
            #item['stats
            

            # cercles
            item['cercles'] = []
            #<a class="vcircle {{position}}" title="{{nom}}" href="acteurs/{{uid}}.html" ></a>
            

        return dict(items=items,nbscrutins=nbscrutins)

    votedata = cache.ram(hash,getVoteData,time_expire=0)

    contexte = dict(tri=tri,axe=idaxe,suffrages=suffrages,desc=desc)

    votedata['items'].sort(key=lambda x:sortfcts[tri]['fct'](contexte,x),reverse=(desc=='1'))

    return dict(axes_choix=[ (a,axes[a]['libelle']) for a in axes_order],
                axe=idaxe,
                suffrages_choix=[('exprime','Exprimés'),('tous','Tous'),('fiemcpt','FI/EM comptabilité')],
                tris_choix=[ (s,sortfcts[s]['libelle']) for s in sortfcts_order+axes[a].get('tris',[])],
                tri=tri,
                filtres = json.dumps(filtres),
                desc=desc,
                suffrages=suffrages,
                elements = axe['elements'],
                titre = axe['titre'],
                **votedata
                )
