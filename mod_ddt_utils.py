import os, re
import xml.etree.ElementTree as et
import mod_globals, mod_db_manager

from operator import itemgetter
from copy import deepcopy
from kivy.utils import platform
if platform != 'android':
    import serial
    from serial.tools import list_ports
else:
    from jnius import autoclass
    mod_globals.os = 'android'
    BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
    BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
    BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
    UUID = autoclass('java.util.UUID')
try:
    import cPickle as pickle
except:
    import pickle

class settings():
    path = ''
    port = ''
    lang = 'RU'
    speed = '38400'
    logName = 'log.txt'
    log = False
    cfc = False
    n1c = False
    si = False
    dump = False
    can2 = False
    options = ''

    def __init__(self):
        self.load()

    def __del__(self):
        pass

    def load(self):
        if not os.path.isfile("../settings.p"):
            self.save()

        f = open('../settings.p', 'rb')
        tmp_dict = pickle.load(f)
        f.close()
        self.__dict__.update(tmp_dict)

    def save(self):
        f = open('../settings.p', 'wb')
        pickle.dump(self.__dict__, f)
        f.close()

def multikeysort(items, columns):
    comparers = [ ((itemgetter(col[1:].strip()), -1) if col.startswith('-') else (itemgetter(col.strip()), 1)) for col in columns]
    def comparer(left, right):
        for fn, mult in comparers:
            result = cmp(fn(left), fn(right))
            if result:
                return mult * result
        else:
            return 0
    return sorted(items, cmp=comparer)

def getPortList():
    devs = {}
    if mod_globals.os != 'android':
        iterator = sorted(list(serial.tools.list_ports.comports()))
        for port, desc, hwid in iterator:
            devs[desc] = port
        return devs
    paired_devices = BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()
    for device in paired_devices:
        deviceName = device.getName()
        if deviceName:
            deviceAddress = device.getAddress()
            devs[deviceName] = deviceAddress
    return devs

def loadECUlist():
    eculistcache = os.path.join(mod_globals.cache_dir, "ddt_eculist.p")

    if os.path.isfile(eculistcache):
        eculist = pickle.load(open(eculistcache, "rb"))
    else:
        eculistfilename = 'ecus/eculist.xml'
        if not mod_db_manager.file_in_ddt(eculistfilename):
            return None

        ns = {'ns0': 'http://www-diag.renault.com/2002/ECU',
              'ns1': 'http://www-diag.renault.com/2002/screens'}

        tree = et.parse(mod_db_manager.get_file_from_ddt(eculistfilename))
        root = tree.getroot()

        eculist = {}
        functions = root.findall("Function")
        if len(functions):
            for function in functions:
                Address = hex(int(function.attrib["Address"])).replace("0x", "").zfill(2).upper()
                eculist[Address] = {}
                FuncName = function.attrib["Name"]
                targets = function.findall("Target")
                eculist[Address]["FuncName"] = FuncName
                eculist[Address]["targets"] = {}
                if len(targets):
                    for target in targets:
                        href = target.attrib["href"]
                        eculist[Address]["targets"][href] = {}
                        pjc = target.findall("Projects")
                        if len(pjc) > 0:
                            pjcl = [elem.tag.upper() for elem in pjc[0].iter()][1:]
                        else:
                            pjcl = []
                        eculist[Address]["targets"][href]['Projects'] = pjcl
                        Prot = target.findall("Protocol")
                        eculist[Address]["targets"][href]['Protocol'] = Prot[0].text
                        ail = []
                        ais = target.findall("ns0:AutoIdents", ns)
                        if len(ais)==0:
                            ais = target.findall("AutoIdents")
                        if len(ais):
                            for ai in ais:
                                AutoIdents = ai.findall("ns0:AutoIdent", ns)
                                if len(AutoIdents)==0:
                                    AutoIdents = ai.findall("AutoIdent")
                                if len(AutoIdents):
                                    for AutoIdent in AutoIdents:
                                        air = {}
                                        air['DiagVersion'] = AutoIdent.attrib["DiagVersion"].strip()
                                        air['Supplier'] = AutoIdent.attrib["Supplier"].strip()
                                        air['Soft'] = AutoIdent.attrib["Soft"].strip()
                                        air['Version'] = AutoIdent.attrib["Version"].strip()
                                        ail.append(air)
                        eculist[Address]["targets"][href]['AutoIdents'] = ail
        pickle.dump(eculist, open(eculistcache, "wb"))

    return eculist


class ddtProjects():
    def __init__(self):
        self.proj_path = 'vehicles/projects.xml'

        self.plist = []

        if not mod_db_manager.file_in_ddt(self.proj_path):
            return

        tree = et.parse(mod_db_manager.get_file_from_ddt(self.proj_path))
        root = tree.getroot()

        DefaultAddressing = root.findall('DefaultAddressing')
        if DefaultAddressing:
            defaddrsheme = DefaultAddressing[0].text

        Manufacturer = root.findall('Manufacturer')
        if Manufacturer:
            for ma in Manufacturer:
                name = ma.findall('name')
                if name:
                    ma_name = ma[0].text
                else:
                    ma_name = 'Unknown'

                pl_ma = {}
                pl_ma['name'] = ma_name
                pl_ma['list'] = []

                project = ma.findall('project')
                if project:
                    for pr in project:
                        cartype = {}
                        addressing = pr.findall('addressing')
                        if addressing:
                            cartype['addr'] = addressing[0].text
                        else:
                            cartype['addr'] = defaddrsheme

                        if 'code' in pr.attrib:
                            cartype['code'] = pr.attrib['code']
                        else:
                            cartype['code'] = ''

                        if 'name' in pr.attrib:
                            cartype['name'] = pr.attrib['name']
                        else:
                            cartype['name'] = ''

                        if 'segment' in pr.attrib:
                            cartype['segment'] = pr.attrib['segment']
                        else:
                            cartype['segment'] = ''

                        pl_ma['list'].append(cartype)

                self.plist.append(pl_ma)

class ddtAddressing():
    def __init__(self, filename, data):
        self.alist = {}
        fun = self.iso_can_select(filename)
        try:
            v_pcan =  int(fun['00']['baudRate'])
        except:
            v_pcan = 0
        for f in data:
            if filename.lower() in str(data[f]).lower():
                self.alist[f] = {}
                self.alist[f]['xml'] = {}
                try:
                    self.alist[f]['XId'] = hex(int(fun[f]['XId']))[2:].upper()
                except:
                    self.alist[f]['XId'] = ''
                for t in data[f]['targets']:
                    if "'"+filename.lower()+"'" in str(data[f]['targets'][t]['Projects']).lower():
                        self.alist[f]['FuncName'] = data[f]['FuncName']
                        try:
                            self.alist[f]['iso8'] = fun[f]['iso8']
                        except:
                            self.alist[f]['iso8'] = ''
                        if data[f]['targets'][t]['Protocol'].startswith('KWP2000 FastInit'):
                            self.alist[f]['xml'][t] = 'KWP-FAST'
                        elif data[f]['targets'][t]['Protocol'].startswith('KWP2000 Init'):
                            self.alist[f]['xml'][t] = 'KWP-SLOW'
                        elif data[f]['targets'][t]['Protocol'].startswith('ISO8'):
                            self.alist[f]['xml'][t] = 'ISO8'
                        elif data[f]['targets'][t]['Protocol'].startswith('DiagOnCAN'):
                            if v_pcan>250000 :
                                self.alist[f]['xml'][t] = 'CAN-500'
                            else:
                                self.alist[f]['xml'][t] = 'CAN-250'
                        else:
                            self.alist[f]['xml'][t] = data[f]['targets'][t]['Protocol']
                if len(self.alist[f]['xml']) == 0:
                    del self.alist[f]
    def iso_can_select(self, filename):
        addr_path = 'vehicles/' + filename.upper() + '/addressing.xml'
        if not mod_db_manager.file_in_ddt(addr_path) :
            addr_path = 'vehicles/' + filename.upper() + '/Addressing.xml'
            if not mod_db_manager.file_in_ddt(addr_path) :
                addr_path = 'vehicles/' + filename + '/addressing.xml'
                if not mod_db_manager.file_in_ddt(addr_path) :
                    addr_path = 'vehicles/' + filename + '/Addressing.xml'
                    if not mod_db_manager.file_in_ddt(addr_path) :
                        return False
        tree = et.parse(mod_db_manager.get_file_from_ddt(addr_path))
        root = tree.getroot()
        ns = {'ns0': 'DiagnosticAddressingSchema.xml',
              'ns1': 'http://www.w3.org/XML/1998/namespace'}
        fun = {}
        Function = root.findall('ns0:Function', ns)
        if Function:
            for fu in Function:
                addr = hex(int(fu.attrib['Address'])).replace("0x", "").zfill(2).upper()
                
                fun[addr] = {}
                baudRate = fu.findall('ns0:baudRate',ns)
                if baudRate:
                    fun[addr]['baudRate'] = baudRate[0].text
                else:
                    fun[addr]['baudRate'] = '0'
                XId = fu.findall('ns0:XId',ns)
                fun[addr]['XId'] = ''
                if XId:
                    fun[addr]['XId'] = XId[0].text
                ISO8 = fu.findall('ns0:ISO8',ns)
                fun[addr]['ISO8'] = ''
                if ISO8:
                    fun[addr]['ISO8'] = ISO8[0].text
        return fun