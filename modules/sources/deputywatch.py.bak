#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import *

def getDeputyWatch():
    import os
    import json
    fp = os.path.join(current.request.folder, 'private/scripts', 'deputywatch.py')
    
    did_scrape = True if os.system(fp) else False

    deputywatch = json.loads(open('/tmp/deputywatch.json','r').read())

    return dict((k,v) for k,v in deputywatch.iteritems() if v.get('flag',False) == True)

deputywatch = current.cache.disk('deputywatch', getDeputyWatch, time_expire=3*24*3600)
