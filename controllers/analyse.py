# -*- coding: utf-8 -*-
# essayez quelque chose comme
import json
def index():
    axe = request.vars.get('axe','groupes')
    filtresaxes =json.loads(request.vars.get('filtresaxes','{}'))
    filtresitems =json.loads(request.vars.get('filtresitems','{}'))
    suffrages = request.vars.get('suffrages','tous')
    tri = request.vars.get('tri','participation')
    desc = request.vars.get('desc','1')
    filterson =request.vars.get('filterson',0)
    tiny = request.vars.get('t',None)
    
    if tiny:
        params = tinyurl.get(tiny)
        params.update({'filterson':filterson})
        return params
    else:
        t = tinyurl.set(locals())
    return locals()

def vueaxe():
    pos_icons = { 'pour':'thumbs-up', 'contre':'thumbs-down', 'abstention':'meh-o', 'nonVotant':'ban', 'absent':'plane','voteem':'','votefi':''}
    pos_libelles = { 'pour':'votes pour', 'contre':'votes contre', 'abstention':'abstention', 'nonVotant':'non votants (justifiés)', 'absent':'absents',
                     'voteem':'EM-Compatibilité','votefi':'FI-Compatibilité'}

    idaxe = request.vars.get('axe','groupes')
    filtresaxes = json.loads(request.vars.get('filtresaxes','{}'))
    filtresitems = json.loads(request.vars.get('filtresitems','{}'))
    suffrages = request.vars.get('suffrages','tous')
    tri = request.vars.get('tri','participation')
    desc = request.vars.get('desc','1')
    filterson = request.vars.get('filterson','0')
    
    
  
    tinyid = tinyurl.set({'axe':idaxe,'filtresaxes':filtresaxes,'filtresitems':filtresitems,'suffrages':suffrages,'tri':tri,'desc':desc})



    #filtres = {}
    #if scrutin != 'tous':
    #    filtres = {'scrutin_id':'15_'+scrutin}

    # Gestion du cache
    import hashlib
    import pickle


    hash = hashlib.md5(pickle.dumps([idaxe,filtresaxes])).hexdigest()
    
    #votedata = cache.ram(hash,getVoteData_fct(idaxe,filtres),time_expire=3600)
    
    votedata = appcache.get(hash,getVoteData_fct,params={'idaxe':idaxe,'filtres':filtresaxes})

    # Tris
    if not tri in sortfcts_order+axes[idaxe].get('tris',[]):
        tri = axes[idaxe].get('tri_defaut',['participation'])[0]

    contexte = dict(tri=tri,axe=idaxe,suffrages=suffrages,desc=desc)

    votedata['items'].sort(key=lambda x:sortfcts[tri]['fct'](contexte,x),reverse=(desc=='1'))
    for f,v in filtresitems.iteritems():
        fct = filtresitm[f]['fct']
        votedata['items'] = filter(lambda it:( fct(it)>=v[0] and fct(it)<=v[1]),votedata['items'])
        
    # A corriger
    from bson import ObjectId
    if idaxe == 'depute':
        votedata['nbdeputes'] = len(votedata['items'])
    axes_values = mdb.axes.find_one()
    axes_dicts = dict((a,dict((it['key'],it['label']) for it in axes_values[a])) for a in axes_order)
    return dict(axes_choix=[ (a,axes[a]['libelle']) for a in axes_order],
                axes_dicts = axes_dicts,
                filtresitems_choix=[ (f,filtresitm[f]['libelle']) for f in filtresitm_order],
                axes_values = axes_values,#json.dumps(axes_values,default=lambda o:'' if isinstance(o,ObjectId) else o),
                axe=idaxe,
                suffrages_choix=[('exprime','Exprimés'),('tous','Tous'),('fiemcpt','FI/EM comptabilité')],
                tris_choix=[ (s,sortfcts[s]['libelle']) for s in sortfcts_order+axes[idaxe].get('tris',[])],
                tri=tri,
                tinyid=tinyid,
                filtresaxes = filtresaxes,
                filtresitems = filtresitems,
                desc=desc,
                filterson=filterson,
                suffrages=suffrages,
                elements = axes[idaxe]['elements'],
                titre = axes[idaxe]['titre'],
                **votedata
                )
