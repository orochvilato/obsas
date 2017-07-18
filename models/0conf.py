# -*- coding: utf-8 -*-


axes = {'groupes':{'libelle':'Groupes',
                   'elements':'G',
                   'tri_defaut':('alpha',False),
                   'hidechart':False,
                   'titre':'Votes par Groupe parlementaire',
                   'source':{'nom':'organes','filtre':{'codeType':'GP','actif':True},'key':'uid','label':'libelle'},
                   'votes':{'field':'groupe'}},
        'assemblee':{'libelle':'Assemblée',
                   'elements':'G',
                   'tri_defaut':('alpha',False),
                   'hidechart':False,
                   'titre':"Votes de l'Assemblée",
                   'source':{'nom':'organes','filtre':{'codeType':'ASSEMBLEE','actif':True},'key':'libelleAbrev','label':'libelle'},
                   'votes':{'field':'organes'}},
        'commissions':{'libelle':'Commissions',
                   'elements':'G',
                   'tri_defaut':('alpha',False),
                   'titre':'Votes par Commissions',
                   'source':{'nom':'organes','filtre':{'$and':[{'$or':[{'codeType':'COMPER'},{'codeType':'CONFPT'}]},{'actif':True}]},'key':'uid','label':'libelle'},
                   'votes':{'field':'commissions'}},
        'regions':{'libelle':'Régions',
                   'elements':'G',
                   'titre':'Votes par Régions',
                   'tri_defaut':('alpha',False),
                   'source':{'nom':'acteurs','filtre':{},'key':'region','label':'region'},
                   'votes':{'field':'region'}},
        'typeregion':{'libelle':'Type Régions',
                   'elements':'G',
                   'titre':'Votes par Type de régions',
                   'tri_defaut':('alpha',False),
                   'source':{'nom':'acteurs','filtre':{},'key':'typeregion','label':'typeregion'},
                   'votes':{'field':'typeregion'}},
        'departements':{'libelle':'Départements',
                   'elements':'G',
                   'tri_defaut':('alpha',False),
                   'titre':'Votes par Départements',
                   'source':{'nom':'acteurs','filtre':{},'key':'departement','label':'departement'},
                   'votes':{'field':'departement'}},
        'ages':{'libelle':"Classes d'age",
                   'elements':'G',
                   'titre':"Votes par classe d'age",
                   'tri_defaut':('alpha',False),
                   'source':{'nom':'acteurs','filtre':{},'key':'classeage','label':'classeage'},
                   'votes':{'field':'classeage'}},
        'csp':{'libelle':"Catégorie Socio-professionnelle",
                   'elements':'G',
                   'tri_defaut':('alpha',False),
                   'titre':'Votes par Catégorie Socio-professionnelle',
                   'source':{'nom':'acteurs','filtre':{},'key':'csp','label':'csp'},
                   'votes':{'field':'csp'}},
        'sexe':{'libelle':"Sexe",
                   'elements':'G',
                   'tri_defaut':('alpha',False),
                   'titre':'Votes par sexe',
                   'source':{'nom':'acteurs','filtre':{},'key':'sexe','label':'sexe'},
                   'votes':{'field':'sexe'}},
        'depute':{'libelle':"Députés",
                   'elements':'P',
                   'tri_defaut':('alphanom',False),
                   'titre':'Votes par député',
                   'source':{'nom':'acteurs','filtre':{},'key':'uid','label':'prenomnom'},
                   'votes':{'field':'uid'}},

        'scrutin':{'libelle':"Scrutins",
                   'elements':'G',
                   'tris':['datescrutin'],
                   'tri_defaut':('datescrutin',True),
                   'titre':'Votes par scrutin',
                   'source':{'nom':'scrutins','filtre':{},'key':'scrutin_id','label':'scrutin_fulldesc'},
                   'votes':{'field':'scrutin_id'}},
        'typescrutin':{'libelle':"Type scrutins",
                   'elements':'G',
                   'tri_defaut':('alpha',False),
                   'titre':'Votes par type de scrutin',
                   'source':{'nom':'scrutins','filtre':{},'key':'scrutin_type','label':'scrutin_typeLibelle'},
                   'votes':{'field':'scrutin_type'}},

        'dossierleg':{'libelle':"Dossier législatif",
                   'elements':'G',
                   'tri_defaut':('alpha',False),
                   'titre':'Votes par dossier législatif',
                   'source':{'nom':'scrutins','filtre':{},'key':'scrutin_dossier','label':'scrutin_dossierLibelle'},
                   'votes':{'field':'scrutin_dossier'}},

       }

axes_order = ['assemblee','groupes','commissions','typeregion','regions','departements','ages','csp','sexe','depute','scrutin','typescrutin','dossierleg']
def vide(ctx,v):
    if (v=='-'):
        return float(-1) if ctx['desc']=='1' else float(10000000)
    else:
        return v

import datetime
sortfcts = {
        'participation': {'libelle':'Participation','fct':lambda ctx,x:vide(ctx,x['participation'])},
        'pctpour': {'libelle':'% Votes pour', 'fct': lambda ctx,x:vide(ctx,x['stats'][ctx['suffrages']]['pour']['pct'])},
        'pctcontre': {'libelle':'% Votes contre', 'fct': lambda ctx,x:vide(ctx,x['stats'][ctx['suffrages']]['contre']['pct'])},
        'pctabs': {'libelle':'% Votes abstention', 'fct': lambda ctx,x:vide(ctx,x['stats'][ctx['suffrages']]['abstention']['pct'])},
        'alpha': {'libelle':'Ordre Alphabétique', 'fct': lambda ctx,x:x['label']},
        'alphanom': {'libelle':'Ordre Alphabétique (nom prenom)', 'fct': lambda ctx,x:x['nomprenom']},
        'ficompat': {'libelle':'FI-Compatibilité', 'fct': lambda ctx,x:vide(ctx,x['stats']['fiemcpt']['votefi']['pct'])},
        'emcompat': {'libelle':'EM-Compatibilité', 'fct': lambda ctx,x:vide(ctx,x['stats']['fiemcpt']['voteem']['pct'])},
        'datescrutin': {'libelle':'par N° de scrutin', 'fct': lambda ctx,x:x['scrutin_num']}
        }
sortfcts_order = ['participation','pctpour','pctcontre','pctabs','alpha','ficompat','emcompat']

filtresitm = {
        'participation': { 'libelle':'Taux de participation','max':100,'min':0,'fct':lambda x:x['participation']},
        'ficompat': { 'libelle':'Taux de FI-compatibilité','max':100,'min':0,'fct':lambda x:x['stats']['fiemcpt']['votefi']['pct']},
        'emcompat': { 'libelle':'Taux de EM-compatibilité','max':100,'min':0,'fct':lambda x:x['stats']['fiemcpt']['voteem']['pct']},
    
    }
filtresitm_order = ['participation','ficompat','emcompat']
