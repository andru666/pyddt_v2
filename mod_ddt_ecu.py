# -*- coding: utf-8 -*-

import sys, os
import pickle
import string
import time
import Queue
import threading
from datetime import datetime
from string import printable
from mod_ddt_request import *
from mod_ddt_data import *
from mod_elm import AllowedList
import itertools

import xml.etree.ElementTree as et
def trim(st):
    res = ''.join(char for char in st if char in printable)
    return res.strip()

import mod_globals
import mod_ddt_utils
import mod_db_manager
    
eculist = None 
ecudump = {}

class CommandQueue(Queue.Queue):
    def _init(self, maxsize):
        self.queue = set()
    def _put(self, item):
        self.queue.add(item)
    def _get(self):
        return self.queue.pop()
    def __contains__(self, item):
        with self.mutex:
            return item in self.queue
    def clear(self):
        self.queue.clear()

def ecuSearch(vehTypeCode, Address, DiagVersion, Supplier, Soft, Version, el, xml_f = False):
    if Address not in el.keys():
        return []
    t = el[Address]['targets']
    while len(DiagVersion) < 3:
        DiagVersion = '0' + DiagVersion
    xml = {0:[], 1:[], 2:[], 3:[], 4:[], 5:[]}
    for k, v in t.iteritems():
        if xml_f:
            if k not in xml_f: continue
        for ai in v['AutoIdents']:
            while len(ai['DiagVersion']) < 3:
                ai['DiagVersion'] = '0' + ai['DiagVersion']
            if '?' in ai['Supplier'] and len(ai['Supplier']) == len(Supplier):
                sup = ''
                for a in range(len(ai['Supplier'])):
                    if ai['Supplier'][a] == '?':
                        sup += Supplier[a]
                    else:
                        sup += ai['Supplier'][a]
                ai['Supplier'] = sup
            h = ai['DiagVersion']+ai['Supplier']+ai['Soft']+ai['Version']
            if xml_f:
                if DiagVersion == ai['DiagVersion'] and Supplier == ai['Supplier'] and Soft.startswith(ai['Soft']) and Version.startswith(ai['Version']):
                    xml[0].append([h, k])
            else:
                if DiagVersion == ai['DiagVersion'] and Supplier == ai['Supplier'] and Soft.startswith(ai['Soft']) and Version.startswith(ai['Version']):
                    xml[0].append([h, k])
                elif len(xml[0]) > 0:
                    if Supplier == ai['Supplier'] and Soft == ai['Soft'] and Version == ai['Version']:
                        xml[1].append([h, k])
                    elif len(xml[1]) > 0:
                        if DiagVersion == ai['DiagVersion'] and Supplier == ai['Supplier'] and Soft == ai['Soft']:
                            xml[2].append([h, k])
                        elif len(xml[2]) > 0:
                            if DiagVersion == ai['DiagVersion'] and Supplier == ai['Supplier'] and len(Soft) == len(ai['Soft']):
                                xml[3].append([h, k])
                            elif len(xml[3]) > 0:
                                if Supplier == ai['Supplier'] and Soft == ai['Soft'] and len(Version) == len(ai['Version']):
                                    xml[4].append([h, k])
                                elif len(xml[4]) > 0:
                                    if Supplier == ai['Supplier'] and len(Soft) == len(ai['Soft']) and len(Version) == len(ai['Version']):
                                        xml[5].append([h, k])

    if len(xml[0]) > 0:
        xmls = {}
        for v in xml[0]:
            xmls[v[1].rsplit('_', 1)[1]] = v[1]
        return xmls[sorted(xmls, reverse=True)[0]]
    else:
        for n in xml:
            if n == 0: continue
            if len(xml[n]) > 0:
                if len(xml[n]) == 1:
                    return xml[n][0][1]
                else:
                    xmls = {}
                    for v in xml[n]:
                        if n == 1:
                            if v[0][:len(DiagVersion)] == D:
                                xmls[v[1].rsplit('_', 1)[1]] = v[1]
                        elif n == 2:
                            V = minD(Version, [x[0][len(DiagVersion)+len(Supplier)+len(Soft):] for x in xml[n]])
                            if v[0][len(DiagVersion)+len(Supplier)+len(Soft):] == V:
                                xmls[v[1].rsplit('_', 1)[1]] = v[1]
                        elif n == 3:
                            So = minD(Soft, [x[0][len(DiagVersion)+len(Supplier):-len(Version)] for x in xml[n]])
                            xmls = {}
                            if v[0][len(DiagVersion)+len(Supplier):-len(Version)] == So:
                                xmls[v[1].rsplit('_', 1)[1]] = v[1]
                        elif n == 4:
                            D = minD(DiagVersion, [x[0][:len(DiagVersion)] for x in xml[n]])
                            V = minD(Version, [x[0][len(DiagVersion)+len(Supplier)+len(Soft):] for x in xml[n]])
                            if v[0][-len(Version):] == V and v[0][:len(DiagVersion)] == D:
                                xmls[v[1].rsplit('_', 1)[1]] = v[1]
                            elif v[0][len(DiagVersion)+len(Supplier)+len(Soft):] == V:
                                xmls[v[1].rsplit('_', 1)[1]] = v[1]
                        elif n == 5:
                            So = minD(Soft, [x[0][len(DiagVersion)+len(Supplier):-len(Version)] for x in xml[n]])
                            if v[0][len(DiagVersion)+len(Supplier):-len(Version)] == So:
                                xmls[v[1].rsplit('_', 1)[1]] = v[1]
                    if len(xmls): 
                        return xmls[sorted(xmls, reverse=True)[0]]
    return 'not_ident#%s#%s#%s#%s'%(DiagVersion, Supplier, Soft, Version)
    
def minD(value, iterable):
    try:
        return min(iterable, key=lambda x: abs(int(value, 16) - int(x, 16)))
    except:
        if len(value) > 1:
            val = ''
            for v in value:
                val = val + str(ord(v))
            it = []
            lvl = {}
            for vl in iterable:
                va = ''
                vll = vl
                while len(vl)<len(value) and '.' in vl:
                    vl = vl.replace('.', '.0')
                for v in vl:
                    va = va + str(ord(v))
                lvl[va] = vll
                it.append(va)
            m = lvl[min(it, key=lambda x:abs(int(x) - int(val)))]
            return m
        else:
            return min(iterable, key=lambda x: abs(ord(value) - ord(x)))