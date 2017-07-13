#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import *

def getScrutins():
    import os
    import json
    fp = os.path.join(current.request.folder, 'private/scripts', 'scrutins.py')
    
    did_scrape = True if os.system(fp) else False

    scrutins = json.loads(open('/tmp/scrutins.json','r').read())

    return scrutins


scrutins = current.cache.disk('scrutins', getScrutins, time_expire=24-3600)
