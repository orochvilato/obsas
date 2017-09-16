# -*- coding: utf-8 -*-

colors = { 'FI':'rgba(12,195,214,1)',
          'NI':'rgba(191,191,191,1)',
          'NG':'rgba(234,52,208,1)',
          'REM':'rgba(255,192,0,1)',
          'MODEM':'rgba(237,125,49,1)',
          'LR':'rgba(47,85,151,1)',
          'LC':'rgba(112,48,160,1)',
          'GDR':'rgba(192,0,0,1)'
        }

departements_ids = {u'Haute-Sa\xf4ne': '070', u'Tarn': '081', u'Paris': '075', u'Fran\xe7ais \xe9tablis hors de France': '999', u'Corse-du-Sud': '02A', u'Ard\xe8che': '007', u'Doubs': '025', u'Calvados': '014', u'Var': '083', u'Haut-Rhin': '068', u'Meurthe-et-Moselle': '054', u'Haute-Marne': '052', u'Moselle': '057', u'Loz\xe8re': '048', u'Gironde': '033', u'Haute-Loire': '043', u"Val-d'Oise": '095', u'Eure': '027', u'Jura': '039', u'Loir-et-Cher': '041', u'Aveyron': '012', u'Ain': '001', u'Seine-et-Marne': '077', u'Yonne': '089', u'Mayenne': '053', u'Val-de-Marne': '094', u'Alpes-Maritimes': '006', u'Corr\xe8ze': '019', u'Gard': '030', u"C\xf4tes-d'Armor": '022', u'Haute-Vienne': '087', 'Saint-Pierre-et-Miquelon': '975', u'Saint-Barth\xe9lemy et Saint-Martin': '977', u'Ari\xe8ge': '009', u'Vend\xe9e': '085', u'Alpes-de-Haute-Provence': '004', u'Sarthe': '072', u'Loire-Atlantique': '044', u"C\xf4te-d'Or": '021', u'Creuse': '023', u'Oise': '060', u'Finist\xe8re': '029', u'Lot-et-Garonne': '047', u'Cantal': '015', u'Vienne': '086', u'Yvelines': '078', u'Bouches-du-Rh\xf4ne': '013', u'Meuse': '055', u'Orne': '061', u'Indre-et-Loire': '037', u'Maine-et-Loire': '049', u'Vaucluse': '084', u'Hauts-de-Seine': '092', u'Deux-S\xe8vres': '079', u'Loire': '042', u'Tarn-et-Garonne': '082', u'Essonne': '091', u'Indre': '036', u'Pas-de-Calais': '062', u'Aude': '011', u'Hautes-Alpes': '005', u'Eure-et-Loir': '028', u'Morbihan': '056', u'Nouvelle-Cal\xe9donie': '988', u'Lot': '046', u'Haute-Corse': '02B', u'Charente': '016', u'Savoie': '073', u'Loiret': '045', u'Manche': '050', u'Pyr\xe9n\xe9es-Atlantiques': '064', u'Puy-de-D\xf4me': '063', u'Ille-et-Vilaine': '035', u'Allier': '003', u'Vosges': '088', u'Marne': '051', u'Rh\xf4ne': '069', u'Sa\xf4ne-et-Loire': '071', u'Pyr\xe9n\xe9es-Orientales': '066', u'Aube': '010', u'Is\xe8re': '038', u'Aisne': '002', u'Haute-Savoie': '074', u'Haute-Garonne': '031', u'Gers': '032', u'Nord': '059', u'Charente-Maritime': '017', u'R\xe9union': '974', u'Landes': '040', u'Hautes-Pyr\xe9n\xe9es': '065', u'H\xe9rault': '034', u'Dr\xf4me': '026', u'Martinique': '972', u'Wallis-et-Futuna': '986', u'Somme': '080', u'Ni\xe8vre': '058', u'Seine-Saint-Denis': '093', u'Mayotte': '976', u'Seine-Maritime': '076', u'Dordogne': '024', u'Guyane': '973', u'Guadeloupe': '971', u'Ardennes': '008', u'Cher': '018', u'Polyn\xe9sie Fran\xe7aise': '987', u'Bas-Rhin': '067', u'Territoire de Belfort': '090'}


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

nuages_excl =('ministre','monsieur',u'collègue','madame','premier','cher','effet','commission','parlementaire',u'député','deux','amendement','sujet','texte','an','fois','lieu','trois','mois','rapporteur','cinq','quant','quel','dix','nom','quelle',u'deuxième','hui','vingt','point','question','y','ne','pas','dire','plus','fait','bien','dit',u'président')
