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

class DDTECU():

    elm = None
    screen = None
    cecu = None
    ecufname = '' 
    requests = {}
    datas = {}
    req4data = {}
    cmd4data = {}
    req4sent = {}
    langmap = {}
    defaultEndian = 'Big'
    sentRequests = []
    BaudRate = '500000'
    Multipoint = '1'
    
    rotaryCommandsQueue = None
    rotaryResultsQueue = None
    rotaryThread = None
    rotaryRunAlloved = None
    rotaryTerminate = None
    elmAccess = None

    def __init__(self, cecu):
    
        global eculist
    
        self.elm = 0
        self.cecu = cecu
        self.ecufname = '' 
        self.requests = {}
        self.datas = {}
        self.req4data = {}
        self.cmd4data = {}
        self.req4sent = {}
        self.langmap = {}
        self.BaudRate = '500000'
        self.Multipoint = '1'

    def __del__(self):
        try:
            del(self.elm)
            del(self.cecu)
            del(self.ecufname)
            del(self.requests)
            del(self.datas)
            del(self.req4data)
            del(self.cmd4data)
            del(self.req4sent)
            del(self.langmap)
            del(self.BaudRate)
            del(self.Multipoint)
            del(self.rotaryRunAlloved)
            del(self.rotaryTerminate)
            del(self.rotaryCommandsQueue)
            del(self.rotaryResultsQueue)
            del(self.elmAccess)
        except:
            pass

    def initRotary(self):

        self.rotaryCommandsQueue = CommandQueue()
        self.rotaryResultsQueue = CommandQueue()

        self.rotaryRunAlloved = threading.Event()
        self.rotaryRunAlloved.set()

        self.rotaryTerminate = threading.Event()
        self.rotaryTerminate.clear()

        self.elmAccess = threading.Lock()

        self.rotaryThread = threading.Thread(target=self.rotary)
        self.rotaryThread.setDaemon(True)
        self.rotaryThread.start()

    def rotary(self):
        while not self.rotaryTerminate.isSet():
            while self.rotaryRunAlloved.isSet():
                if not self.rotaryCommandsQueue.empty():
                    req = self.rotaryCommandsQueue.get_nowait()
    
                    prev_rsp = self.elm.getFromCache(req)
                    self.elm.delFromCache(req)
    
                    self.elmAccess.acquire()
   
                    rsp = self.elm.request(req, positive='', cache=True)
    
                    self.elmAccess.release()
    
                    if self.rotaryResultsQueue.qsize()<64:
                        if prev_rsp != rsp or req not in self.sentRequests:
                            self.rotaryResultsQueue.put((req, rsp))
    
                    if req not in self.sentRequests:
                        self.sentRequests.append(req)
    
                else:
                    if mod_globals.opt_demo:
                        time.sleep(0.1)

    def putToRotary(self, req):
            self.rotaryCommandsQueue.put(req)
            return ''

    def setELM(self, elm):
        if self.elm!=None:
            del(self.elm)
        if elm!=None:
            self.elm = elm
        
    def setLangMap(self,langmap):
        self.langmap = langmap
        
    def translate(self, data):
        
        if data in self.datas.keys():
            d = self.datas[data]
        else:
            return data        

        if data in self.req4data.keys() and self.req4data[data] in self.requests.keys():
            r = self.requests[self.req4data[data]]
        else: return data
        
        sentBytes = r.SentBytes
        startByte = r.ReceivedDI[data].FirstByte
        startBit = r.ReceivedDI[data].BitOffset
        bitLength = d.BitsCount
        
        if bitLength%8:
            startBit = 7-startBit
            if r.ReceivedDI[data].Endian=="Big":
                startBit = 7 - startBit
        else:
            startBit = 0
        
        key = "%s:%s:%s:%s"%(sentBytes,str(startByte), str(startBit), str(bitLength))
        
        if key in self.langmap.keys():
            return self.langmap[key]
        else:
            return data

    def scanECU(self):
        
        global eculist
        
        vehTypeCode = ''
        Address = ''
        DiagVersion = ''
        Supplier = ''
        Soft = ''
        Version = ''
        hash = ''

        self.clearELMcache()
        IdRsp = self.elm.request(req = '2180', positive = '61', cache = False)

        Address = self.cecu['dst']

        if "vehTypeCode" in self.cecu.keys():
            vehTypeCode = self.cecu['vehTypeCode']

        if len(IdRsp)>59:
            DiagVersion = str(int(IdRsp[21:23],16))
            Supplier = trim(IdRsp[24:32].replace(' ','').decode('hex'))
            Soft = trim(IdRsp[48:53].replace(' ',''))
            Version = trim(IdRsp[54:59].replace(' ',''))
        else:
            self.clearELMcache()

            IdRsp_F1A0 = self.elm.request(req = '22F1A0', positive = '62', cache = False)
            if len(IdRsp_F1A0)>8 and 'NR' not in IdRsp_F1A0:
                DiagVersion = str(int(IdRsp_F1A0[9:11],16))

            IdRsp_F18A = self.elm.request(req = '22F18A', positive = '62', cache = False)
            if len(IdRsp_F18A)>8 and 'NR' not in IdRsp_F18A:
                Supplier = trim(IdRsp_F18A[9:].replace(' ','').decode('hex').decode('ASCII', errors='ignore'))

            IdRsp_F194 = self.elm.request(req = '22F194', positive = '62', cache = False)
            if len(IdRsp_F194)>8 and 'NR' not in IdRsp_F194:
                Soft = trim(IdRsp_F194[9:].replace(' ','').decode('hex').decode('ASCII', errors='ignore'))
            
            IdRsp_F195 = self.elm.request(req = '22F195', positive = '62', cache = False)
            if len(IdRsp_F195)>8 and 'NR' not in IdRsp_F195:
                Version = trim(IdRsp_F195[9:].replace(' ','').decode('hex').decode('ASCII', errors='ignore'))
                
        hash = Address+DiagVersion+Supplier+Soft+Version

        eculist = mod_ddt_utils.loadECUlist()

        if len(mod_globals.opt_ddtxml)>0:
            fname = mod_globals.opt_ddtxml
            self.ecufname = mod_globals.ddtroot+'/ecus/'+fname
        else:
            problist = ecuSearch(vehTypeCode, Address, DiagVersion, Supplier, Soft, Version, eculist)

            while 1:
                if len(problist)!=1:
                    fname = raw_input("File name:")
                else:
                    fname = raw_input("File name ["+problist[0]+"]:")
                    if len(fname)==0:
                            fname = problist[0]
                
                fname = fname.strip()
                if len(fname):
                    self.ecufname = 'ecus/'+fname
                    if mod_db_manager.file_in_ddt(self.ecufname):
                        break
                    else:
                        print "No such file :",self.ecufname
                else:
                    return
                
        self.loadXml()    
                
    def loadXml(self, xmlfile = ''):
    
        if len(xmlfile):
            self.ecufname = xmlfile
        
        if not mod_db_manager.file_in_ddt(self.ecufname):
            return

        tree = et.parse(mod_db_manager.get_file_from_ddt(self.ecufname))
        root = tree.getroot()
        
        ns = {'ns0':'http://www-diag.renault.com/2002/ECU',
                    'ns1':'http://www-diag.renault.com/2002/screens'}
        
        cans = root.findall('ns0:Target/ns0:CAN', ns)
        if cans:
            for can in cans:
                self.BaudRate = can.attrib["BaudRate"]
                self.Multipoint = can.attrib["Multipoint"]
        
        rq_class = decu_requests(self.requests, root)
        dt_class = decu_datas(self.datas, root)
        
        for r in self.requests.values():
            self.req4sent[r.SentBytes] = r.Name
            for di in r.ReceivedDI.values():
                if di.Ref or di.Name not in self.req4data.keys():
                    self.req4data[di.Name] = r.Name
            for di in r.SentDI.values():
                if di.Name not in self.cmd4data.keys():
                    self.cmd4data[di.Name] = r.Name

    def saveDump(self):
        xmlname = self.ecufname.split('/')[-1]
        if xmlname.upper().endswith('.XML'):
            xmlname = xmlname[:-4]

        dumpname = os.path.join(mod_globals.dumps_dir, str(int(time.time()))+'_'+xmlname+'.txt')
        df = open(dumpname,'wt')

        self.elm.clear_cache()

        im = ' from ' + str(len(self.requests.keys()))
        i = 0
        for request in self.requests.values():
            i = i + 1
            sys.stdout.flush()
            if request.SentBytes[:2] in AllowedList + ['17','19']:
                if request.SentBytes[:2] == '19' and request.SentBytes[:2] != '1902':
                    continue
                pos = chr(ord(request.SentBytes[0])+4)+request.SentBytes[1]
                rsp = self.elm.request(request.SentBytes, pos, False)
                if ':' in rsp: continue
                df.write('%s:%s\n'%(request.SentBytes,rsp))
        df.close()

    def loadDump(self, dumpname=''):
        global ecudump
        
        ecudump = {}
        
        xmlname = self.ecufname.split('/')[-1]
        if xmlname.upper().endswith('.XML'):
            xmlname = xmlname[:-4]

        if len(dumpname)==0 or not os.path.exists(dumpname):
            flist = []
         
            for root, dirs, files in os.walk(mod_globals.dumps_dir):
                for f in files:
                    if(xmlname+'.') in f:
                        flist.append(f)
                        
            if len(flist)==0: return
            flist.sort()
            dumpname = os.path.join(mod_globals.dumps_dir, flist[-1])

        mod_globals.dumpName = dumpname
        df = open(dumpname,'rt')
        lines = df.readlines()
        df.close()
        
        for l in lines:
            l = l.strip().replace('\n','')
            if l.count(':')==1:
                req,rsp = l.split(':')
                ecudump[req] = rsp
        
        self.elm.setDump(ecudump)
        
    def clearELMcache(self):
        self.elm.clear_cache()
        self.sentRequests = []

    def elmRequest(self, req, delay='0', positive='', cache=True):
        if req.startswith('10'):
            self.elm.startSession = req
            
        if type(delay) is str:
            delay = int(delay)
            
        if delay>0 and delay<1000: delay = 1000

        self.elmAccess.acquire()
        rsp = self.elm.request(req, positive, cache , serviceDelay=delay)
        self.elmAccess.release()

        if self.screen != None and(not cache or req not in self.sentRequests):
            tmstr = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        if cache and req not in self.sentRequests:
            self.sentRequests.append(req)

        return rsp

    def getValue(self, data, auto=True, request=None, responce=None):
        hv = self.getHex(data, auto, request, responce)

        if hv == mod_globals.none_val:
            return mod_globals.none_val
        
        if data in self.datas.keys():
            d = self.datas[data]
        else:
            return hv
        
        if len(d.List.keys()):
            listIndex = int(hv,16)
            if listIndex in d.List.keys():
                hv = hex(listIndex)[2:]
                return hv+':'+d.List[listIndex]
            else:
                return hv

        if d.Scaled:
            p = int(hv,16)
            if d.signed and p>(2**(d.BitsCount-1)-1):
                p = p-2**d.BitsCount
            res =(p*float(d.Step)+float(d.Offset))/float(d.DivideBy)
            if len(d.Format) and '.' in d.Format:
                acc = len(d.Format.split('.')[1])
                fmt = '%.'+str(acc)+'f'
                res = fmt%(res)
            res = str(res)
            if res.endswith('.0'): res = res[:-2]
            return res+' '+d.Unit
        
        if d.BytesASCII:
            res = hv.decode('hex')
            
            if not all(c in string.printable for c in res): 
                res = hv
            return res 

        return hv

    def getHex(self, data, auto=True, request=None, responce=None):
        if data in self.datas.keys():
            d = self.datas[data]
        else:
            if data not in self.requests.keys():
                return mod_globals.none_val
        print request
        if request==None:
            if data in self.req4data.keys() and self.req4data[data] in self.requests.keys():
                r = self.requests[self.req4data[data]]
            else:
                if data in self.requests.keys():
                    r = self.requests[data]
                else: 
                    return mod_globals.none_val
        else:
            r = request
        
        if auto and(r.ManuelSend or len(r.SentDI.keys())>0) and data not in r.SentDI.keys():
            return mod_globals.none_val
            
        if(r.SentBytes[:2] not in AllowedList) and not mod_globals.opt_exp and data not in r.SentDI.keys(): 
            return mod_globals.none_val

        if responce==None:
            resp = self.elmRequest(r.SentBytes)
        else:
            resp = responce

        if data not in self.datas.keys():
            return resp
        
        resp = resp.strip().replace(' ','')
        if not all(c in string.hexdigits for c in resp): resp = ''
        resp = ' '.join(a+b for a,b in zip(resp[::2], resp[1::2]))
            
        if data in r.ReceivedDI.keys():
            littleEndian = True if r.ReceivedDI[data].Endian=="Little" else False
            sb = r.ReceivedDI[data].FirstByte - 1 
            sbit = r.ReceivedDI[data].BitOffset
        else:
            littleEndian = True if r.SentDI[data].Endian=="Little" else False
            sb = r.SentDI[data].FirstByte - 1 
            sbit = r.SentDI[data].BitOffset
                    
        bits = d.BitsCount
        bytes =(bits+sbit-1)/8 + 1
        if littleEndian:
            rshift = sbit
        else:
            rshift =((bytes+1)*8 -(bits+sbit))%8
        
        if(sb*3+bytes*3-1)>(len(resp)):
            return mod_globals.none_val
        
        hexval = resp[sb*3:(sb+bytes)*3-1]
        hexval = hexval.replace(" ","")

        val =(int(hexval,16)>>int(rshift))&(2**bits-1)

            
        hexval = hex(val)[2:]
        if hexval[-1:].upper()=='L':
            hexval = hexval[:-1]
        if len(hexval)%2:
            hexval = '0'+hexval

        if len(hexval)/2 < d.BytesCount:
            hexval = '00'*(d.BytesCount-len(hexval)/2) + hexval

        if littleEndian:
            a = hexval
            b = ''
            if not len(a) % 2:
                for i in range(0,len(a),2):
                    b = a[i:i+2]+b
                hexval = b
        
        return hexval

    def getParamExtr(self, parName, iValues, dValues):
        result = '\nTerminal command hint\n\n'
        if parName not in self.datas.keys():
            return 'Error finding datas'
        d = self.datas[parName]
        rr = None
        for r in self.requests.values():
            if parName in r.ReceivedDI.keys() and r.SentBytes[:2] in ['21','22']:
                rr = r
                break

        rcm = rr.SentBytes[:2]
        lid = r.SentBytes[2:].upper()

        if rcm == '21':
            wcm = '3B' + lid
        else:
            wcm = '2E' + lid

        wr = None
        for r in self.requests.values():
            if parName in r.SentDI.keys() and r.SentBytes.upper().startswith(wcm):
                wr = r
                break

        if    rr==None:
            return "Didn't find command for DataRead"

        if    wr==None:
            result += "Didn't find command for DataWrite\n\n"

        rdi = rr.ReceivedDI[parName]
        if wr!=None:
            sdi = wr.SentDI[parName]

            if rr.MinBytes != len(wr.SentBytes) / 2:
                result += "Commands for DataRead and DataWrite have different length"

            if rdi.FirstByte!=sdi.FirstByte or rdi.BitOffset!=sdi.BitOffset or rdi.Endian!=sdi.Endian:
                result += "Data not in the same place in DataRead and DataWrite"

        if d.Name in iValues.keys():
            value = iValues[d.Name].strip()
        elif d.Name in dValues.keys():
            value = dValues[d.Name].strip()
        else:
            value = 0
        value = self.getValueFromInput(d, value)

        littleEndian = True if rdi.Endian == "Little" else False
        sb = rdi.FirstByte - 1
        bits = d.BitsCount
        sbit = rdi.BitOffset
        bytes =(bits + sbit - 1) / 8 + 1
        if littleEndian:
            lshift = sbit
        else:
            lshift =((bytes + 1) * 8 -(bits + sbit)) % 8
        try:
            val = int(value, 16)
        except:
            return 'ERROR: Wrong HEX value in parametr(%s) : "%s"' %(d.Name, value)
        val =(val &(2 ** bits - 1)) << lshift
        value = hex(val)[2:]
        if value[-1:].upper() == 'L':
            value = value[:-1]
        if len(value) % 2:
            value = '0' + value

        if value.upper().startswith('0X'): value = value[2:]
        value = value.zfill(bytes * 2).upper()
        if not all(c in string.hexdigits for c in value) and len(value) == bytes * 2:
            return 'ERROR: Wrong value in parametr:%s(it should have %d bytes)' %(d.Name, d.BytesCount)

        mask =(2 ** bits - 1) << lshift
        hmask = hex(mask)[2:].upper()
        if hmask[-1:].upper() == 'L':
            hmask = hmask[:-1]
        hmask = hmask[-bytes * 2:].zfill(bytes * 2)

        func_params = ' ' + lid + ' ' + str(rr.MinBytes) + ' ' + str(rdi.FirstByte) + ' ' + hmask + ' ' + value + '\n'

        for f in ['exit_if','exit_if_not']:
            result +=(f + func_params)
        if wr!=None:
            for f in ['set_bits', 'xor_bits']:
                result +=(f + func_params)

        return result

    def getValueFromInput(self, d, value):

        if len(d.List.keys()) and ':' in value:
            value = value.split(':')[0]

        if d.Scaled:
            if ' ' in value:
                value = value.split(' ')[0]
            if value.upper().startswith('0X'):
                value = value[2:]
            else:
                if not all((c in string.digits or c == '.' or c == ',' or c == '-' or c == 'e' or c == 'E') for c in value):
                    return 'ERROR: Wrong value in parametr:%s(it should have %d bytes), be decimal or starts with 0x for hex' %(
                    d.Name, d.BytesCount)
                flv =(float(value) * float(d.DivideBy) - float(d.Offset)) / float(d.Step)
                value = hex(int(flv))
        if d.BytesASCII:
            hst = ''
            if len(value)<(d.BitsCount/8):
                value += ' '*(d.BitsCount/8 - len(value))
            for c in value:
                hst = hst + hex(ord(c))[2:].zfill(2)
            value = hst

        return value

    def packValues(self, requestName, iValues):
        r = self.requests[requestName]
        
        cmdPatt = r.SentBytes
        
        for sdi in r.SentDI.values():
        
            d = self.datas[sdi.Name]
            if d.Name not in iValues.keys():
                continue
            value = iValues[d.Name].strip()
            value = self.getValueFromInput(d, value)
            
            littleEndian = True if sdi.Endian=="Little" else False
            sb = sdi.FirstByte - 1 
            bits = d.BitsCount
            sbit = sdi.BitOffset
            bytes =(bits+sbit-1)/8 + 1
            if littleEndian:
                lshift = sbit
            else:
                lshift =((bytes+1)*8 -(bits+sbit))%8
                
            try:
                val = int(value,16)
            except:
                return 'ERROR: Wrong HEX value in parametr(%s) : "%s"' %(d.Name, value)
            val =(val&(2**bits-1))<<lshift
            value = hex(val)[2:]
            if value[-1:].upper()=='L':
                value = value[:-1]
            if len(value)%2:
                value = '0'+value

            if value.upper().startswith('0X'): value = value[2:]
            value = value.zfill(bytes*2).upper()
            if not all(c in string.hexdigits for c in value) and len(value)==bytes*2:
                return 'ERROR: Wrong value in parametr:%s(it should have %d bytes)' %(d.Name, d.BytesCount)

            base = cmdPatt[sb*2:(sb+bytes)*2]
            binbase = int(base,16)
            binvalue = int(value,16)
            mask =(2**bits-1)<<lshift
            
            binvalue = binbase ^(mask & binbase) | binvalue

            value = hex(binvalue)[2:].upper()
            if value[-1:].upper()=='L':
                value = value[:-1]
            value = value[-bytes*2:].zfill(bytes*2)

            cmdPatt = cmdPatt[0:sb*2] + value + cmdPatt[(sb+bytes)*2:]

        return cmdPatt

    def getValueForConfig_second_cmd(self, d, first_cmd):

        res = 'ERROR'
        rcmd = ''
        for c in self.requests.keys():
            if c == first_cmd: continue
            if d in self.requests[c].ReceivedDI.keys():
                rcmd = c
                break

        if rcmd == '':
            return 'ERROR'

        if self.datas[d].BytesASCII:
            res = self.getValue(d, request=self.requests[rcmd])
        else:
            gh = self.getHex(d, request=self.requests[rcmd])
            if gh != mod_globals.none_val:
                res = '0x' + gh
            else:
                res = gh
        return res

    def getValueForConfig(self, d):

        res = 'ERROR'

        if d in self.req4data.keys():
            rcmd = self.req4data[d]
        else:
            return res
        
        if self.datas[d].BytesASCII:
            res = self.getValue(d, request=self.requests[rcmd])
        else:
            gh = self.getHex(d, request=self.requests[rcmd])
            if gh != mod_globals.none_val:
                res = '0x' + gh
            else:
                res = gh

        if(res==mod_globals.none_val):
            res = self.getValueForConfig_second_cmd(d,rcmd)

        return res

    def makeConf(self, indump = False, annotate = False):
        config = []
        conf_v = {}
        config_ann = []
        
        sentValues = {}
        for r in sorted(self.requests.values(), key = lambda x: x.SentBytes):
            if not(r.SentBytes[0:2].upper() == '3B' or r.SentBytes[0:2].upper() == '2E') or len(r.SentDI) == 0:
                continue

            if annotate:
                    config_ann.append('#'*60)
                    config_ann.append('# '+r.Name)

            sentValues.clear()
            for di in sorted(r.SentDI.values(), key = lambda x: x.FirstByte*8+x.BitOffset):
                d = di.Name
                
                if indump:
                        if d in self.req4data.keys():
                                first_cmd = self.req4data[d]
                                i_r_cmd = self.requests[self.req4data[d]].SentBytes
                                if i_r_cmd not in self.elm.ecudump.keys() or (i_r_cmd in self.elm.ecudump.keys() and self.elm.ecudump[i_r_cmd]==''):
                                    second_is = False
                                    for c in self.requests.keys():
                                        if c == first_cmd: continue
                                        if d in self.requests[c].ReceivedDI.keys():
                                            second_is = True
                                            break
                                    if not second_is:
                                        continue
                                    
                val = self.getValueForConfig(d)

                if 'ERROR' in val:
                    continue
                    
                sentValues[d] = val
                conf_v[d] = val
                
                if annotate:
                        val_ann = self.getValue(d)
                        config_ann.append('##         '+d + ' = ' + val_ann)

            if len(sentValues) != len(r.SentDI):
                if len(r.SentDI) == 2 and r.SentBytes[0:2].upper() == '3B':
                    SDIs = sorted(r.SentDI.values(), key=operator.attrgetter("FirstByte","BitOffset"))
                    if len(self.datas[SDIs[0].Name].List)>0:
                        for list_el_key in self.datas[SDIs[0].Name].List.keys():
                            list_el_val = self.datas[SDIs[0].Name].List[list_el_key]
                            found = False
                            fdk = ""
                            for datas_keys in self.datas.keys():
                                if datas_keys in list_el_val:
                                    if len(datas_keys)>len(fdk):
                                        fdk = datas_keys
                                    found = True
                            if found:
                                if SDIs[0].Name not in sentValues.keys():
                                    sentValues[SDIs[0].Name] = ''
                                sentValues[SDIs[0].Name] = hex(list_el_key)
                                if SDIs[1].Name not in sentValues.keys():
                                    sentValues[SDIs[1].Name] = ''
                                sentValues[SDIs[1].Name] = self.getValueForConfig(fdk)
                                conf_v[SDIs[1].Name] = self.getValueForConfig(fdk)
                                sendCmd = self.packValues(r.Name, sentValues)
                                config.append(sendCmd)
                                if annotate:
                                    config_ann.append(sendCmd)
                                    config_ann.append('')
                continue
            else:
                sendCmd = self.packValues(r.Name, sentValues)
                if 'ERROR' in sendCmd:
                    continue
                config.append(sendCmd)
                if annotate:
                    config_ann.append(sendCmd)
                    config_ann.append('')

        sentValues.clear()
        if annotate:
            return config_ann, conf_v
        else:
            return config, conf_v

    def bukva(self, bt, l, sign=False):
        S1 = chr((bt - l) % 26 + ord('A'))
        ex = int(bt - l) / 26
        if ex:
            S2 = chr((ex - 1) % 26 + ord('A'))
            S1 = S2 + S1
        if sign:
            S1 = 'signed(' + S1 + ')'
        return S1

    def get_ddt_pid(self, l_Scaled, l_BitsCount, l_Endian, l_FirstByte, l_BitOffset, l_signed, l_Step, l_Offset, l_DivideBy, l_SentBytes):
    
        l = len(l_SentBytes) / 2 + 1
        sb = int(l_FirstByte)
        bits = int(l_BitsCount)
        sbit = int(l_BitOffset)
        bytes =(bits + sbit - 1) / 8 + 1
        rshift =((bytes + 1) * 8 -(bits + sbit)) % 8
        mask = str(2 ** bits - 1)
        sign = l_signed
    
        equ = self.bukva(sb, l, sign)
    
        if l_Endian.upper() == 'BIG':
            if bytes == 2:
                equ = self.bukva(sb, l, sign) + '*256+' + self.bukva(sb + 1, l)
            if bytes == 3:
                equ = self.bukva(sb, l, sign) + '*65536+' + self.bukva(sb + 1, l) + '*256+' + self.bukva(sb + 2, l)
            if bytes == 4:
                equ = self.bukva(sb, l, sign) + '*16777216+' + self.bukva(sb + 1, l) + '*65536+' + self.bukva(sb + 2, l) + '*256+' + self.bukva(sb + 3, l)
        else:
            if bytes == 2:
                equ = self.bukva(sb + 1, l, sign) + '*256+' + self.bukva(sb, l)
            if bytes == 3:
                equ = self.bukva(sb + 2, l, sign) + '*65536+' + self.bukva(sb + 1, l) + '*256+' + self.bukva(sb, l)
            if bytes == 4:
                equ = self.bukva(sb + 3, l, sign) + '*16777216+' + self.bukva(sb + 2, l) + '*65536+' + self.bukva(sb + 1, l) + '*256+' + self.bukva(sb, l)
                
    
        if len(equ) > 2:
            if equ[0] == '(' and equ[-1] == ')':
                pass
            else:
                equ = '(' + equ + ')'
    
        if bits % 8:
            smask = '&' + mask
        else:
            smask = ''
    
        if bits == 1:
            equ = "{" + equ + ":" + str(rshift) + "}"
        elif rshift == 0:
            equ = equ + smask
        else:
            equ = "(" + equ + ">" + str(rshift) + ")" + smask
    
        if len(equ) > 2:
            if(equ[0] == '(' and equ[-1] == ')') or(equ[0] == '{' and equ[-1] == '}'):
                pass
            else:
                equ = '(' + equ + ')'

        if l_Scaled:
            if l_Step!=1:
                equ = equ+'*'+str(l_Step)
            if l_Offset != 0:
                if l_Offset>0:
                    equ = equ+'+'+str(l_Offset)
                else:
                    equ = equ+str(l_Offset)
                if l_DivideBy!=1:
                    equ = '('+equ+')'
            if l_DivideBy!=1:
                equ = equ+'/'+str(l_DivideBy)

        return equ

def ecuSearch(vehTypeCode, Address, DiagVersion, Supplier, Soft, Version, el, interactive = True):
    if Address not in el.keys():
        return []
    
    ela = el[Address]
    if interactive:
        print Address, '#', pyren_encode(ela['FuncName'])
    t = ela['targets']
    cand = {}

    for k in t.keys():
        for ai in t[k]['AutoIdents']:
            ai['DiagVersion'], ai['Supplier'], ai['Soft'], ai['Version']
            h = ai['DiagVersion']+ai['Supplier']+ai['Soft']+ai['Version']
            if DiagVersion == ai['DiagVersion'] and Supplier == ai['Supplier'] and Soft == ai['Soft'] and Version == ai['Version']:
                return k
            elif Supplier == ai['Supplier'] and Soft == ai['Soft'] and Version == ai['Version']:
                cand[h] = k
            elif Supplier == ai['Supplier'] and Soft == ai['Soft']:
                cand[h] = k
    if len(cand) > 0:
        if DiagVersion+Supplier+Soft+Version in cand.keys():
            return cand[DiagVersion+Supplier+Soft+Version]
        xml = {0:{}, 1:{}, 2:{}, 3:{}, 4:{}}
        for key, values in cand.items():
            if key.startswith(DiagVersion+Supplier+Soft):
                xml[1][values] = key
            if key.startswith(DiagVersion+Supplier):
                xml[2][values] = key
            if Supplier+Soft+Version in key:
                xml[3][values] = key
            if Supplier+Soft in key:
                xml[4][values] = key
        for n in range(5):
            if xml[n]:
                if len(xml[n]) == 1:
                    return xml[n].keys()[0]
                else:
                    V = minD(int(Version, 16), [int(x[-4:], 16) for x in xml[n].values()])
                    D = minD(int(DiagVersion, 16), [int(x[:4], 16) for x in xml[n].values()])
                    S = minD(int(Soft, 16), [int(x[-8:-4], 16) for x in xml[n].values()])
                    for k, v in xml[n].items():
                        if n == 2:
                            if int(v[-8:-4], 16) == S:
                                return k
                        if n >= 3:
                            if int(v[:4], 16) == D:
                                return k
                        if int(v[-4:], 16) == V:
                            return k

def minD(value, items):
    found = items[0]
    for item in items:
        if abs(item - value) < abs(found - value):
            found = item
    return found