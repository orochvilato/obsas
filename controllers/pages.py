# -*- coding: utf-8 -*-
# essayez quelque chose comme
import re

def index(): return dict(message="hello from pages.py")
mdb = client.obsass

# cache
CACHE_EXPIRE = 3600
cache_groupes = cache.ram('groupes', lambda: [(g['groupe_abrev'],g['groupe_libelle']) for g in mdb.groupes.find()], time_expire=CACHE_EXPIRE)
cache_regions = cache.ram('regions',lambda: sorted(mdb.deputes.distinct('depute_region'),key=lambda x:x), time_expire=CACHE_EXPIRE)
# ---------------------------------
# Page députés
# ---------------------------------

def deputes():
    groupe = request.vars.get('gp','ALL')
    tri = request.vars.get('tr','depute_nom_tri')
    direction = int(request.vars.get('di',1))
    text = request.vars.get('txt',"")
    region = request.vars.get('rg',"")
    top = request.vars.get('top',"")

    groupes = cache_groupes
    regions = cache_regions
    tris = [('depute_nom_tri','Tri par nom'),
            ('stats.positions.exprimes','Tri par participation'),
            ('stats.positions.dissidence','Tri par dissidence'),
            ('stats.compat.FI','Tri par FI-Compatibilité'),
            ('stats.compat.REM','Tri par EM-Compatibilité'),
            ('stats.nbitvs',"Tri par nombre d'interventions"),
            ('stats.nbmots',"Tri par nombre de mots"),
            ('depute_circo_id',"Tri par circonscription")]
    tops = [('top10part','Top 10 Participation'),
            ('top10diss','Top 10 Dissidence'),
            ('top10compFI','Top 10 FI-Compatible'),
            ('top10compREM','Top 10 EM-Compatible'),
            ('top10itvs','Top 10 Interventions'),
            ('top10mots','Top 10 Mots'),
            ('flop10part','Flop 10 Participation'),
            ('flop10diss','Flop 10 Dissidence'),
            ('flop10compFI','Flop 10 FI-Compatible'),
            ('flop10compREM','Flop 10 EM-Compatible'),
            ('flop10itvs','Flop 10 Interventions'),
            ('flop10mots','Flop 10 Mots'),
            ]
    return locals()

def deputes_ajax():
    # ajouter des index (aux differentes collections)
    nb = 25
    minpart_top = 30
    page = int(request.args(0) or 2)-2
    groupe = request.vars.get('gp','ALL')
    tri = request.vars.get('tr','depute_nom_tri')
    direction = int(request.vars.get('di',1))
    text = request.vars.get('txt',None)
    region = request.vars.get('rg',None)
    top = request.vars.get('top',None)

    tops_sorts = {'part':'stats.positions.exprimes',
                  'diss':'stats.positions.dissidence',
                  'itvs':'stats.nbitvs',
                  'mots':'stats.nbmots',
                  'compFI':'stats.compat.FI',
                  'compREM':'stats.compat.REM'}

    filter = {'depute_actif':True}


    if text:
        regx = re.compile(text, re.IGNORECASE)
        filter['depute_nom'] = regx
    if groupe and groupe!='ALL':
        filter['groupe_abrev'] = groupe
    if region and region!='ALL':
        filter['depute_region'] = region

    if top:
        rtop = re.match(r'(top|flop)(\d+)([a-z]{4})([A-Z]*)',top)
        if rtop:
            tf,n,typ,gp = rtop.groups()
            nb = int(n)
            page = 0
            direction = -1 if tf=='top' else 1
            tri = tops_sorts[typ+gp]
            filter = {'$and':[ {'stats.positions':{'$ne':None}},filter ]}
            if gp:
                filter['$and'].append({'groupe_abrev':{'$ne':gp}})
    skip = nb*page
    deputes = list(mdb.deputes.find(filter).sort([(tri,direction)]).skip(skip).limit(nb))

    return dict(deputes=deputes, tri = tri, skip = skip, next=((nb == len(deputes)) and not top ))
