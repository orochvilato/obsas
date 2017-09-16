# -*- coding: utf-8 -*-
# essayez quelque chose comme
def index(): return dict(message="hello from pages.py")
mdb = client.obsass

# ---------------------------------
# Page députés
# ---------------------------------

def deputes():
    groupes = [(g['groupe_abrev'],g['groupe_libelle']) for g in mdb.groupes.find()]
    regions = mdb.deputes.distinct('depute_region')
    tris = [('depute_nom_tri','Tri par nom'),
            ('stats.positions.exprimes','Tri par participation'),
            ('stats.positions.dissidence','Tri par dissidence'),
            ('stats.compat.FI','Tri par FI-Compatibilité'),
            ('stats.compat.REM','Tri par EM-Compatibilité'),
            ('stats.nbitvs',"Tri par nombre d'interventions"),
            ('stats.nbmots',"Tri par nombre de mots"),
            ('depute_circo',"Tri par circonscription")]
    return dict(groupes=groupes,tris=tris,regions=regions)

def deputes_ajax():
    # ajouter des index (aux differentes collections)
    nb = 25
    page = int(request.args(0) or 2)-2
    groupe = request.args(1) or 'ALL'
    tri = request.args(2) or 'depute_nom_tri'
    direction = int(request.args(3) or 1)
    text = request.vars.get('search',None)
    region = request.vars.get('region',None)
    filter = {'depute_actif':True}
    
    groupe = request.args(1)
    if text:
        import re
        print text
        regx = re.compile(text, re.IGNORECASE)
        filter['depute_nom'] = regx
    if groupe and groupe!='ALL':
        filter['groupe_abrev'] = groupe
    if region and region!='ALL':
        filter['depute_region'] = region
    #d_sort = 'stats.compat.FI'
    #d_dir = -1
    deputes = list(mdb.deputes.find(filter).sort([(tri,direction)]).skip(nb*page).limit(nb))
    
    return dict(deputes=deputes, next=(nb == len(deputes)))
