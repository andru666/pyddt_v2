import math
import mod_globals
from mod_utils import *
# Returns signed value from 16 bits (2 bytes)
def hex16_tosigned(value):
    return -(value & 0x8000) | (value & 0x7fff)


# Returns signed value from 8 bits (1 byte)
def hex8_tosigned(value):
    return -(value & 0x80) | (value & 0x7f)


class decu_data:
    Name = ""
    Comment = ""
    Mnemonic = ""
    Description = ""
    Bytes = False
    BytesCount = 1
    BytesASCII = False
    Bits = False
    BitsCount = 8
    signed = False
    Binary = False
    List = {}
    Scaled = False
    Step = 1.0
    Offset = 0.0
    DivideBy = 1.0
    Format = ''
    Unit = ''
    
    def __str__(self):
        li = ''
        for k in self.List.keys():
            li = li + '\n'+'%4s:%s'%(k,self.List[k])

        out = '''
            Name = %s
            Comment = %s
            Mnemonic = %s
            Description = %s
            Bytes = %d
            BytesCount = %d
            BytesASCII = %d
            Bits = %d
            BitsCount = %d
            signed = %d
            Binary = %d
            List = %s
            Scaled = %d
            Step = %f
            Offset = %f
            DivideBy = %f
            Format = %s
            Unit = %s 
            ''' % (self.Name, self.Comment, self.Mnemonic, self.Description, self.Bytes, self.BytesCount, self.BytesASCII, self.Bits, self.BitsCount, self.signed, self.Binary, li, self.Scaled, self.Step, self.Offset, self.DivideBy, self.Format, self.Unit)
        return pyren_encode(out)    

    def __init__(self, dt):
    
        ns = {'ns0': 'http://www-diag.renault.com/2002/ECU', 'ns1': 'http://www-diag.renault.com/2002/screens'}
        self.Name = dt.attrib["Name"]
        self.Comment = ""
        Comment = dt.findall("ns0:Comment",ns)
        if Comment: self.Comment=Comment[0].text
        self.Mnemonic = ""
        Mnemonic = dt.findall("ns0:Mnemonic",ns)
        if Mnemonic: self.Mnemonic=Mnemonic[0].text
        self.Description = ""
        Description = dt.findall("ns0:Description",ns)
        if Description: self.Description=Description[0].text.replace('<![CDATA[','').replace(']]>','')
        Bytes = dt.findall("ns0:Bytes", ns)
        if len(Bytes):
            by = Bytes[0]
            self.Bytes = True
            self.BytesCount = 1
            if "count" in by.attrib.keys():
                self.BytesCount = int(math.ceil(float(by.attrib["count"])))
            self.BitsCount = self.BytesCount * 8
            self.BytesASCII = False
            if "ascii" in by.attrib.keys():
                self.BytesASCII = True
        Bits = dt.findall("ns0:Bits", ns)
        if Bits:
            bi = Bits[0]
            self.Bits = True
            self.BitsCount = 8
            self.BytesASCII = False
            if "ascii" in bi.attrib.keys():
                self.BytesASCII = True
            if "count" in bi.attrib.keys():
                self.BitsCount = int(bi.attrib["count"])
            self.BytesCount = int(math.ceil(self.BitsCount / 8.0))
            self.signed = False
            if "signed" in bi.attrib.keys():
                self.signed = True
            self.Binary = False
            Binary = bi.findall("ns0:Binary", ns)
            if len(Binary): self.Binary = True
            self.List = {}
            Items = bi.findall("ns0:List/ns0:Item", ns)
            if len(Items):
                for i in Items:
                    Value = 0
                    if "Value" in i.attrib.keys():
                        Value = int(i.attrib["Value"])
                    Text = ""
                    if "Text" in i.attrib.keys():
                        Text = i.attrib["Text"]
                    if ';' in Text: Text = Text.split(';')[0].strip()
                    self.List[Value] = Text
            self.Scaled = False
            Scaled = bi.findall("ns0:Scaled", ns)
            if len(Scaled):
                sc = Scaled[0]
                self.Scaled = True
                self.Step = 1.0
                if "Step" in sc.attrib.keys():
                    self.Step = float(sc.attrib["Step"])
                self.Offset = 0.0
                if "Offset" in sc.attrib.keys() and sc.attrib["Offset"]!='':
                    self.Offset = float (sc.attrib["Offset"])
                self.DivideBy = 1.0
                if "DivideBy" in sc.attrib.keys():
                    self.DivideBy = float (sc.attrib["DivideBy"])
                self.Format = ""
                if "Format" in sc.attrib.keys():
                    self.Format = sc.attrib["Format"]
                self.Unit = ""
                if "Unit" in sc.attrib.keys():
                    self.Unit = sc.attrib["Unit"]

    def setValue(self, value, bytes_list, dataitem, test_mode=False):
        start_byte = dataitem.FirstByte - 1
        start_bit = dataitem.BitOffset
        little_endian = False
        
        if dataitem.Endian == "Little":
            little_endian = True
        if dataitem.Endian == "Big":
            little_endian = False
        if self.BytesASCII:
            value = str(value)
            if self.BytesCount > len(value):
                value = value.ljust(self.BytesCount)
            if self.BytesCount < len(value):
                value = value[0:self.BytesCount]

            asciival = ""
            for i in range(self.BytesCount):
                if not test_mode:
                    asciival += hex(ord(value[i]))[2:].upper()
                else:
                    asciival += "FF"

            value = asciival
        if self.Scaled:
            if not test_mode:
                try:
                    value = float(value)
                except:
                    return None

                # Input value must be base 10
                value = int((value * float(self.DivideBy) - float(self.Offset)) / float(self.Step))
            else:
                value = int("0x" + value, 16)
        else:
            if not test_mode:
                # Check input length and validity
                if not all(c in string.hexdigits for c in value):
                    return None
                # Value is base 16
                value = int('0x' + str(value), 16)
            else:
                value = int("0x" + value, 16)
        valueasbin = bin(value)[2:].zfill(self.BitsCount)

        numreqbytes = int(math.ceil(float(self.BitsCount + start_bit) / 8.))
        request_bytes = bytes_list[start_byte:start_byte + numreqbytes]
        requestasbin = ""

        for r in request_bytes:
            requestasbin += bin(int(r, 16))[2:].zfill(8)
        requestasbin = list(requestasbin)

        if little_endian:
            remainingbits = self.BitsCount

            lastbit = 7 - start_bit + 1
            firstbit = lastbit - self.BitsCount
            if firstbit < 0:
                firstbit = 0

            count = 0
            for i in range(firstbit, lastbit):
                requestasbin[i] = valueasbin[count]
                count += 1

            remainingbits -= count
            currentbyte = 1
            while remainingbits >= 8:
                for i in range(0, 8):
                    requestasbin[currentbyte * 8 + i] = valueasbin[count]
                    count += 1
                remainingbits -= 8
                currentbyte += 1
            if remainingbits > 0:
                lastbit = 8
                firstbit = lastbit - remainingbits

                for i in range(firstbit, lastbit):
                    requestasbin[currentbyte * 8 + i] = valueasbin[count]
                    count += 1

        else:
            for i in range(self.BitsCount):
                requestasbin[i + start_bit] = valueasbin[i]

        requestasbin = "".join(requestasbin)
        valueasint = int("0b" + requestasbin, 2)
        valueashex = hex(valueasint)[2:].replace("L", "").zfill(numreqbytes * 2).upper()

        for i in range(numreqbytes):
            bytes_list[i + start_byte] = valueashex[i * 2:i * 2 + 2].zfill(2)

        return bytes_list

    def getDisplayValue(self, elm_data, dataitem, ecu_endian):
        value = self.getHexValue(elm_data, dataitem, ecu_endian)
        if value is None:
            return None

        if self.BytesASCII:
            return bytes.fromhex(value).decode('utf-8')

        if not self.Scaled:
            val = int('0x' + value, 16)

            if self.signed:
                if self.BytesCount == 1:
                    val = hex8_tosigned(val)
                elif self.BytesCount == 2:
                    val = hex16_tosigned(val)
                else:
                    print("Warning, cannot get signed value for %s" % dataitem.Name)

            if val in self.List:
                return self.List[val]

            return value

        value = int('0x' + value, 16)

        if self.signed:
            if self.BytesCount == 1:
                value = hex8_tosigned(value)
            elif self.BytesCount == 2:
                value = hex16_tosigned(value)

        if self.DivideBy == 0:
            print("Division by zero, please check data item : ", dataitem.Name)
            return None

        res = (float(value) * float(self.Step) + float(self.Offset)) / float(self.DivideBy)

        if len(self.Format) and '.' in self.Format:
            acc = len(self.Format.split('.')[1])
            fmt = '%.' + str(acc) + 'f'
            res = fmt % res
        else:
            if int(res) == res:
                return str(int(res))

        return str(res)

    def getHexValue(self, resp, dataitem, ecu_endian):
        little_endian = False

        if ecu_endian == "Little":
            little_endian = True

        # Data cleaning
        resp = resp.strip().replace(' ', '')
        if not all(c in string.hexdigits for c in resp): resp = ''
        resp.replace(' ', '')

        res_bytes = [resp[i:i + 2] for i in range(0, len(resp), 2)]

        # Data count
        startByte = dataitem.FirstByte
        startBit = dataitem.BitOffset
        bits = self.BitsCount

        databytelen = int(math.ceil(float(self.BitsCount) / 8.0))
        reqdatabytelen = int(math.ceil(float(self.BitsCount + startBit) / 8.0))

        sb = startByte - 1
        if (sb * 2 + databytelen * 2) > (len(resp)):
            return None

        hexval = resp[sb * 2:(sb + reqdatabytelen) * 2]

        hextobin = ""
        for b in res_bytes[sb:sb + reqdatabytelen]:
            hextobin += bin(int(b, 16))[2:].zfill(8)

        if len(hexval) == 0:
            return None

        if little_endian:
            # Don't like this method

            totalremainingbits = bits
            lastbit = 7 - startBit + 1
            firstbit = lastbit - bits
            if firstbit < 0:
                firstbit = 0

            tmp_bin = hextobin[firstbit:lastbit]
            totalremainingbits -= lastbit - firstbit

            if totalremainingbits > 8:
                offset1 = 8
                offset2 = offset1 + ((reqdatabytelen - 2) * 8)
                tmp_bin += hextobin[offset1:offset2]
                totalremainingbits -= offset2 - offset1

            if totalremainingbits > 0:
                offset1 = (reqdatabytelen - 1) * 8
                offset2 = offset1 - totalremainingbits
                tmp_bin += hextobin[offset2:offset1]
                totalremainingbits -= offset1 - offset2

            if totalremainingbits != 0:
                print("getHexValue >> abnormal remaining bytes ", bits, totalremainingbits)
            hexval = hex(int("0b" + tmp_bin, 2))[2:].replace("L", "")
        else:
            valtmp = "0b" + hextobin[startBit:startBit + bits]
            hexval = hex(int(valtmp, 2))[2:].replace("L", "")

        # Resize to original length
        hexval = hexval.zfill(databytelen * 2)
        return hexval


class decu_datas:
    def __init__(self, data_list, xdoc):
        ns = {'ns0': 'http://www-diag.renault.com/2002/ECU', 'ns1': 'http://www-diag.renault.com/2002/screens'}
        data = xdoc.findall('ns0:Target/ns0:Datas', ns)
        datas = data[0].findall('ns0:Data', ns)
        if datas:
            for dt in datas:
                data = decu_data( dt )
                data_list[data.Name] = data