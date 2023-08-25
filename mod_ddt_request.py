import operator
import mod_globals
import xml.etree.ElementTree as et
from mod_utils import *
class DataItem:
    Name = ''
    Endian = ''
    FirstByte = 1
    BitOffset = 0
    Ref = False
    def __str__(self):
        out = 'Endian = %-5s FirstByte = %2d BitOffset = %2d    Ref = %1d Name = %s' % (self.Endian, self.FirstByte, self.BitOffset, self.Ref, self.Name)
        return pyren_encode(out)    

    def __init__(self, di, defaultEndian ):
        self.Name = di.attrib["Name"]
        if "Endian" in di.attrib.keys():
            self.Endian = di.attrib["Endian"]
        else:
            self.Endian=defaultEndian
        if "FirstByte" in di.attrib.keys ():
            self.FirstByte = int(di.attrib["FirstByte"])
        if "BitOffset" in di.attrib.keys ():
            self.BitOffset = int(di.attrib["BitOffset"])
        if "Ref" in di.attrib.keys ():
            Ref = di.attrib["Ref"]
            if Ref=='1': self.Ref=True
            else:                self.Ref=False
        else:
            self.Ref = False

class decu_request:
    Name = ''
    DossierMaintenabilite = None
    ManuelSend = None
    DenyAccess = []
    SentBytes = ''
    SentDI = {}
    VariableLength = False
    ReceivedDI = {}
    MinBytes = 1
    ShiftBytesCount = 0
    ReplyBytes = ''
    Endian = ''
    
    def __str__(self):
        sd = ''
        for s in sorted(self.SentDI.values(), key=operator.attrgetter("FirstByte","BitOffset")):
            sd = sd + '\n'+str(s)
        sd = pyren_decode(sd)
        rd = ''
        for r in sorted(self.ReceivedDI.values(), key=operator.attrgetter("FirstByte","BitOffset")):
            rd = rd + '\n'+str(r)
        rd = pyren_decode(rd)
        out = '''
            Name = %s
            DossierMaintenabilite = %d
            ManuelSend = %d
            DenyAccess = %s
            SentBytes = %s
            SentDI = %s
            VariableLength = %d
            ReceivedDI = %s
            MinBytes = %d
            ShiftBytesCount = %d
            ReplyBytes = %s
            ''' % (self.Name, self.DossierMaintenabilite, self.ManuelSend, self.DenyAccess, self.SentBytes, sd, self.VariableLength, rd, self.MinBytes, self.ShiftBytesCount, self.ReplyBytes)
        return pyren_encode(out)    
    
    def __init__(self, rq, defaultEndian, data_dtc):
        ns = {'ns0': 'http://www-diag.renault.com/2002/ECU',
                    'ns1': 'http://www-diag.renault.com/2002/screens'}
        self.Name = rq.attrib["Name"]
        self.DossierMaintenabilite = False
        DossierMaintenabilite = rq.findall("ns0:DossierMaintenabilite",ns)
        if DossierMaintenabilite: self.DossierMaintenabilite=True
        self.ManuelSend = False
        ManuelSend = rq.findall("ns0:ManuelSend",ns)
        if ManuelSend: self.ManuelSend=True
        self.DenyAccess = []
        DenyAccess = rq.findall("ns0:DenyAccess",ns)
        if DenyAccess:
            NoSDS = DenyAccess[0].findall("ns0:NoSDS",ns)
            if NoSDS: self.DenyAccess.append('NoSDS')
            Supplier = DenyAccess[0].findall("ns0:Supplier",ns)
            if Supplier: self.DenyAccess.append('Supplier')
            Engineering = DenyAccess[0].findall("ns0:Engineering",ns)
            if Engineering: self.DenyAccess.append('Engineering')
            Plant = DenyAccess[0].findall("ns0:Plant",ns)
            if Plant: self.DenyAccess.append('Plant')
            AfterSales = DenyAccess[0].findall("ns0:AfterSales",ns)
            if AfterSales: self.DenyAccess.append('AfterSales')
        Sent = rq.findall("ns0:Sent",ns)
        if len(Sent):
            self.SentBytes = ''
            SentBytes = Sent[0].findall("ns0:SentBytes",ns)
            if len(SentBytes): self.SentBytes = SentBytes[0].text
            if self.SentBytes == '1200040000':
                if self.Name in data_dtc:
                    self.SentBytes = '120004' + data_dtc[self.Name]
                elif '0' in data_dtc:
                    self.SentBytes = '120004' + data_dtc['0']
                
            self.VariableLength = False
            VariableLength = Sent[0].findall("ns0:VariableLength",ns)
            if len(VariableLength): self.VariableLength=True
            self.SentDI = {}
            DataItems = Sent[0].findall("ns0:DataItem",ns)
            if DataItems:
                for di in DataItems:
                    dataitem = DataItem( di, defaultEndian )
                    self.SentDI[dataitem.Name]=dataitem
        Received = rq.findall("ns0:Received",ns)
        if len(Received):
            self.MinBytes = 0
            MinBytes = Received[0].attrib["MinBytes"]
            if MinBytes: self.MinBytes = int(MinBytes)
            self.ShiftBytesCount = 0
            ShiftBytesCount = Received[0].findall("ns0:ShiftBytesCount",ns)
            if len(ShiftBytesCount): self.ShiftBytesCount = int(ShiftBytesCount[0].text)
            self.ReplyBytes = ''
            ReplyBytes = Received[0].findall("ns0:ReplyBytes",ns)
            if len(ReplyBytes): self.ReplyBytes = ReplyBytes[0].text
            self.ReceivedDI = {}
            DataItems = Received[0].findall("ns0:DataItem",ns)
            if len(DataItems):
                for di in DataItems:
                    dataitem = DataItem(di, defaultEndian)
                    self.ReceivedDI[dataitem.Name]=dataitem

    def send_request(self, inputvalues={}, ecu=None, test_data=None):
        request_stream = self.build_data_stream(inputvalues, ecu.datas)
        request_stream = " ".join(request_stream)
        if mod_globals.opt_demo:
            if test_data is not None:
                elmstream = test_data
            else:
                elmstream = self.ReplyBytes
        else:
            elmstream = ecu.elm.request(request_stream)
        if elmstream.startswith('WRONG RESPONSE'):
            return None
        if elmstream.startswith('7F'):
            nrsp = ecu.elm.errorval(elmstream[6:8])
            return None
        values = self.get_values_from_stream(elmstream)
        return values
        

    def build_data_stream(self, data, datas):
        data_stream = self.get_formatted_sentbytes()
        self.datas = datas
        for k, v in data.items():
            if k in self.SentDI:
                datatitem = self.SentDI[k]
            else:
                raise KeyError('Ecurequest::build_data_stream : Data item %s does not exist' % k)
            if k in data:
                data = datas[k]
            else:
                raise KeyError('Ecurequest::build_data_stream : Data %s does not exist' % k)
            if v in datas:
                v = hex(datas.items[v])[2:].upper()
            data.setValue(v, data_stream, datatitem)
        return data_stream

    def get_values_from_stream(self, stream):
        values = {}
        for k, v in self.ReceivedDI.items():
            self.Endian = v.Endian
            if k in self.datas:
                data = self.datas[k]
                values[k] = data.getDisplayValue(stream, v, self.Endian)
            else:
                raise KeyError('Ecurequest::get_values_from_stream : Data %s does not exist' % k)
        return values

    def get_formatted_sentbytes(self):
        bytes_to_send_ascii = self.SentBytes
        return [str(bytes_to_send_ascii[i:i + 2]) for i in range(0, len(bytes_to_send_ascii), 2)]

class decu_requests:
    def __init__(self, requiest_list, xdoc):
        ns = {'ns0': 'http://www-diag.renault.com/2002/ECU', 'ns1': 'http://www-diag.renault.com/2002/screens'}
        data_dtc = {}
        devices = xdoc.findall('ns0:Target/ns0:Devices', ns)
        if devices:
            for device in devices[0]:
                if 'DTC' in device.attrib:
                    if 'FreezeFrame' in device.attrib:
                        FreezeFrame = device.attrib['FreezeFrame']
                        if FreezeFrame == 'Read Freeze Frame':
                            data_dtc[device.attrib['Name']] = hex(int(device.attrib['DTC'])).replace("0x", "").upper()
                        else:
                            data_dtc[FreezeFrame] = hex(int(device.attrib['DTC'])).replace("0x", "").upper()
                    elif '0' not in data_dtc.keys():
                        data_dtc['0'] = hex(int(device.attrib['DTC'])).replace("0x", "").upper()
        tmpdoc = xdoc.findall('ns0:Target/ns0:Requests', ns)
        defaultEndian = ''
        if tmpdoc and ('Endian' in tmpdoc[0].attrib.keys()):
            defaultEndian = tmpdoc[0].attrib["Endian"]
        else:
            defaultEndian = "Big"
        requests = tmpdoc[0].findall("ns0:Request", ns)
        if requests:
            for rq in requests:
                request = decu_request(rq, defaultEndian, data_dtc)
                requiest_list[request.Name] = request