# -*- coding: utf-8 -*-
lexiques = { 'NOM':{},'ADJ':{},'VER':{},'ADV':{} }
i = 0
with open('lexique.txt','r') as f:
    while 1:
        lig = f.readline()

        if not lig:
            break
        if lig[0] == '1':
            continue
        mot,lemme,mtype,mtypes = lig.split(';')
    
        if 'NOM' in mtypes:
            if mtype!='NOM':
                continue
        elif 'ADJ' in mtypes:
            if mtype!='ADJ':
                continue
        elif 'VER' in mtypes:
            if mtype!='VER':
                continue
        if mtype not in ['NOM','ADJ','VER','ADV']:
            continue
        excl = False
        for exc in ['CON', 'PRO','ART','PRE','AUX','ind','dem','pos']:
            if exc in mtypes:
                excl = True
                break
        if excl:
            continue
      

        if not mot in lexiques[mtype].keys():
            lexiques[mtype][mot] = lemme
            i += 1

        if i % 1000 == 0:
            print i

    import json

    with open('lexiques.json','w') as f:
        f.write(json.dumps(lexiques))
