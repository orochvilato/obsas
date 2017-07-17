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
    
    #votedata = cache.ram(hash,getVoteData_fct(idaxe,filtres),time_expire=3600)
    
    votedata = appcache.get(hash,getVoteData_fct,params={'idaxe':idaxe,'filtres':filtres})

    # Tris
    if not tri in sortfcts_order+axes[idaxe].get('tris',[]):
        tri = axes[idaxe].get('tri_defaut',['participation'])[0]

    contexte = dict(tri=tri,axe=idaxe,suffrages=suffrages,desc=desc)

    votedata['items'].sort(key=lambda x:sortfcts[tri]['fct'](contexte,x),reverse=(desc=='1'))
    
    # A corriger
    from bson import ObjectId

    axes_values = mdb.axes.find_one()
    
    return dict(axes_choix=[ (a,axes[a]['libelle']) for a in axes_order],
                axes_values = axes_values,#json.dumps(axes_values,default=lambda o:'' if isinstance(o,ObjectId) else o),
                axe=idaxe,
                suffrages_choix=[('exprime','Exprimés'),('tous','Tous'),('fiemcpt','FI/EM comptabilité')],
                tris_choix=[ (s,sortfcts[s]['libelle']) for s in sortfcts_order+axes[idaxe].get('tris',[])],
                tri=tri,
                filtres = filtres,
                desc=desc,
                suffrages=suffrages,
                elements = axes[idaxe]['elements'],
                titre = axes[idaxe]['titre'],
                **votedata
                )
