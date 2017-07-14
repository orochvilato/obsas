# -*- coding: utf-8 -*-
# essayez quelque chose comme
def index():
    import tools
    import pymongo
    from sources.hatvp import declarations
    from sources.deputywatch import deputywatch
    from sources.acteurs_organes import getActeursOrganes
    from sources.scrutins import getScrutins

    # Acteurs et organes
    actorg = getActeursOrganes()

    mdb.acteurs.create_index([('uid', pymongo.ASCENDING)], unique = True)
    bulk = mdb.acteurs.initialize_unordered_bulk_op()
    for act in actorg['acteurs'].values():
        bulk.find({'uid':act['uid']}).upsert().replace_one(act)
    result = bulk.execute()
   
    
    mdb.organes.create_index([('uid', pymongo.ASCENDING)], unique = True)
    bulk = mdb.organes.initialize_unordered_bulk_op()
    for org in actorg['organes'].values():
        bulk.find({'uid':org['uid']}).upsert().replace_one(org)
    result = bulk.execute()
   
    
    # Scrutins et votes
    s_ids = [ s['scrutin_id'] for s in mdb.scrutins.find()]
    acteurs = dict((a['id'],a) for a in mdb.acteurs.find())
    scr = getScrutins(acteurs,s_ids)
    # stockage des votes et des scrutins dans la base
    if scr['votes']:
        mdb.votes.create_index([('vote_id', pymongo.ASCENDING)], unique = True)
        mdb.votes.insert_many(scr['votes'])

    if scr['scrutins']:
        mdb.scrutins.create_index([('scrutin_id', pymongo.ASCENDING)], unique = True)
        mdb.scrutins.insert_many(scr['scrutins'])

    
    #for axe,defs in axes:
    #    axe_items = [ (s[defs['key']],s[defs['label']]) for s in andata[defs['source']] ]
    #    axesdefs['noms'].append(axe)
    #    axesdefs['defs'][axe] = {'titre':defs['titre'],'hidechart':defs.get('hidechart',False),'field':defs['item_field'], 'compare':defs['item_compare'], 'items':sorted(list(set(axe_items)),key=lambda item:item[1])}

    return dict(d=len(declarations),e=len(deputywatch),s=scr['scrutins'],s_ids=s_ids)
