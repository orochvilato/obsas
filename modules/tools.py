#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import *

import requests
from zipfile import ZipFile
from cStringIO import StringIO
import xmltodict
from datetime import datetime
import re


import unicodedata
def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')
def normalize(s):
    return strip_accents(s).replace(' ','').replace('-','').lower() if s else s

from datetime import datetime
def format_date(date):
    d = datetime.strptime(date,'%Y-%m-%d')
    return d.strftime('%-d %B %Y').decode('utf8')



# Traitement XML data.assemblee.gouv

def loadXMLZip(url):

    zip = StringIO(requests.get(url).content)

    with ZipFile(zip,'r') as z:
        name = z.namelist()[0]
        with z.open(name,'r') as f:
            xml = f.read()

    return xmltodict.parse(xml)
def getVal(v):
    return None if isinstance(v,dict) else v

import collections
def flatten(elt):
    if isinstance(elt,dict):
        update = []
        for k,v in elt.iteritems():
            if isinstance(v, collections.MutableMapping):
                update.append((k,v))
            elif isinstance(v,list):
                flatten(v)
        for (k,v) in update:
            flatten(v)
            if '@xsi:nil' in v.keys():
                elt[k] = None
                continue
            if len(v.keys()) == 1 and k == v.keys()[0]+'s':
                elt[k] = v.values()[0]
                continue
            for _k,_v in v.iteritems():
                elt[ k + '_' + _k ] = _v
            del elt[k]
        if '@xsi:type' in elt.keys():
            elt['type'] = elt['@xsi:type']
            del elt['@xsi:type']
        if 'uid_#text' in elt.keys():
            elt['uid'] = elt['uid_#text']
            del elt['uid_#text']
    elif isinstance(elt,list):
        for e in elt:
            flatten(e)
