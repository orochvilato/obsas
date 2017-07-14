# -*- coding: utf-8 -*-
# essayez quelque chose comme
import tools
import pymongo


def fetch_acteurs_organes():
    from sources.hatvp import declarations
    from sources.deputywatch import deputywatch
    from sources.acteurs_organes import getActeursOrganes

    
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
   
    
def index():
    from sources.scrutins import getScrutins    
    #fetch_acteurs_organes()
    # Scrutins et votes
    s_ids = [ s['scrutin_id'] for s in mdb.scrutins.find()]
    acteurs = dict((a['id'],a) for a in mdb.acteurs.find())
    scr = getScrutins(acteurs,s_ids)
    # stockage des votes et des scrutins dans la base
    if scr['votes']:
        
        mdb.votes.create_index([('vote_id', pymongo.ASCENDING)], unique = True)
        #mdb.votes.insert_many(scr['votes'])
        for s in scr['votes']:
            mdb.votes.insert(s)

    if scr['scrutins']:
        mdb.scrutins.create_index([('scrutin_id', pymongo.ASCENDING)], unique = True)
        mdb.scrutins.insert_many(scr['scrutins'])

    

    return dict(s_ids=s_ids)
