# -*- coding: utf-8 -*-
# essayez quelque chose comme
def index():
    axe = request.vars.get('axe','groupes')
    suffrages = request.vars.get('suffrages','tous')
    scrutin = request.vars.get('scrutin','tous')
    tri = request.vars.get('tri','participation')
    desc = request.vars.get('desc','1')
    return locals()

def vueaxe():
    pos_icons = { 'pour':'thumbs-up', 'contre':'thumbs-down', 'abstention':'meh-o', 'nonVotant':'ban', 'absent':'plane'}
    pos_libelles = { 'pour':'votes pour', 'contre':'votes contre', 'abstention':'abstention', 'nonVotant':'non votants (justifiés)', 'absent':'absents'}
    
    idaxe = request.vars.get('axe','groupes')
    suffrages = request.vars.get('suffrages','tous')
    scrutin = request.vars.get('scrutin','tous')
    tri = request.vars.get('tri','participation')
    desc = request.vars.get('desc','1')

    filters = {}
    if scrutin != 'tous':
        filters = {'scrutin_id':'15_'+scrutin}
    
    # Gestion du cache
    import hashlib
    import pickle
    hash = hashlib.md5(pickle.dumps([idaxe,filters])).hexdigest()
    
    axe = axes[idaxe]
    source = axe['source']
    def getVoteData():
       
        items = [ {'key':item[0],'label':item[1]} for item in list(set([(item[source['key']],item[source['label']]) for item in mdb[source['nom']].find(source['filtre'])]))]
        
        nbscrutins= len(mdb.votes.distinct('scrutin_id',filters))
        
        for item in items:
            itemreq = {axe['votes']['field']:item['key']}
            req = {'$and': [ itemreq, filters ]}
            votes = {}
            nb = {'absent':0,'nonVotant':0,'pour':0,'contre':0,'abstention':0}
            for vote in mdb.votes.find(req):
                votes[vote['position']] = votes.get(vote['position'],[]) + [ vote['uid'] ]
                nb[vote['position']] +=  1
            if nbscrutins==1:
                item['votes'] = votes
            item['nb'] = nb
            item['deputes'] = sum(nb.values())/nbscrutins
            total_exprime = nb['pour'] + nb['contre'] + nb['abstention']
            total = total_exprime + nb['absent'] + nb['nonVotant']
            item['votants'] = round(float(total_exprime)/nbscrutins,1)
            item['participation'] = round(100*float(total_exprime) / (total_exprime + nb['absent']),1) if total_exprime+nb['absent']>0 else '-'
            item['stats'] = {'exprime':{},'tous': {}}
            for pos in ['pour','contre','abstention']:
                item['stats']['exprime'][pos]={'n':round(float(nb[pos])/nbscrutins,1),
                                               'libelle':pos_libelles[pos],
                                               'pct':round(100*float(nb[pos])/total_exprime,1) if total_exprime>0 else '-',
                                               'class':'pct','icon':pos_icons[pos]}
            for pos in ['pour','contre','abstention','absent','nonVotant']:
                item['stats']['tous'][pos]= {'n':round(float(nb[pos])/nbscrutins,1), 'libelle':pos_libelles[pos],'pct':round(100*float(nb[pos])/total,1),'class':'pct','icon':pos_icons[pos]}
            
            # chercher le max
            #item['stats

           
            # cercles
            item['cercles'] = []

        return dict(items=items,nbscrutins=nbscrutins)
    
    votedata = cache.ram(hash,getVoteData,time_expire=1800)
    
    contexte = dict(tri=tri,axe=idaxe,suffrages=suffrages,desc=desc)    
    
    votedata['items'].sort(key=lambda x:sortfcts[tri]['fct'](contexte,x),reverse=(desc=='1'))
    
    return dict(axes_choix=[ (a,axes[a]['libelle']) for a in axes_order],
                axe=idaxe,
                suffrages_choix=[('exprime','Exprimés'),('tous','Tous')],
                tris_choix=[ (s,sortfcts[s]['libelle']) for s in sortfcts_order],
                tri=tri,
                scrutin=scrutin,
                desc=desc,
                suffrages=suffrages,
                elements = axe['elements'],
                titre = axe['titre'],
                **votedata
                )
