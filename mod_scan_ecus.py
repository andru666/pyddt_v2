from string import printable

def trim( st ):
    res = ''.join(char for char in st if char in printable)
    return res.strip()

opt_demo = False

def readECUIds( elm ):
    elm.clear_cache()

    StartSession = ''
    DiagVersion = ''
    Supplier = ''
    Version = ''
    Soft = ''
    Std = ''
    VIN = ''
    rsp = ''
    if elm.startSession == '':
        res = elm.request(req='10C0', positive='50', cache=False)
        if res=='' or 'ERROR' in res:
            return StartSession, DiagVersion, Supplier, Version, Soft, Std, VIN
        if res.startswith('50'):
            StartSession = '10C0'
        else:
            res = elm.request(req='1003', positive='50', cache=False)
            if res.startswith('50'):
                StartSession = '1003'
            else:
                res = elm.request(req='10A0', positive='50', cache=False)
                if res.startswith('50'):
                    StartSession = '10A0'
                else:
                    res = elm.request(req='10B0', positive='50', cache=False)
                    if res.startswith('50'):
                        StartSession = '10B0'
    else:
        StartSession = elm.startSession
        res = elm.request(req=elm.startSession, positive='50', cache=False)
    if not res.startswith('50'):
        pass
    IdRsp = elm.request(req='2180', positive='61', cache=False)
    if len(IdRsp) > 59 and '7F' not in IdRsp:
        DiagVersion = str(int(IdRsp[21:23], 16))
        Supplier = trim(IdRsp[24:32].replace('00', '20').replace(' ', '')).strip()
        Supplier = bytes.fromhex(Supplier).strip().decode('utf-8')
        Soft = trim(IdRsp[48:53].replace('00', '20').replace(' ', '')).strip()
        Version = trim(IdRsp[54:59].replace('00', '20').replace(' ', '')).strip()
        Std = 'STD_A'
        vinRsp = elm.request(req='2181', positive='61', cache=False)
        if len(vinRsp)>55 and 'NR' not in vinRsp and '7F' not in vinRsp:
            VIN = trim(vinRsp[6:56].replace('00', '20').replace(' ', '')).strip()
            VIN = bytes.fromhex(VIN).strip().decode('utf-8')
    else:
        IdRsp_F1A0 = elm.request(req='22F1A0', positive='62', cache=False)
        if len(IdRsp_F1A0) > 9 and 'NR' not in IdRsp_F1A0 and 'BUS' not in IdRsp_F1A0 and '7F' not in IdRsp_F1A0:
            if True:
                DiagVersion = str(int(IdRsp_F1A0[9:11], 16))
                IdRsp_F18A = elm.request(req='22F18A', positive='62', cache=False)
                if len(IdRsp_F18A) > 8 and 'NR' not in IdRsp_F18A and 'BUS' not in IdRsp_F18A and '7F' not in IdRsp_F18A:
                    Supplier = trim(IdRsp_F18A[9:].replace('00', '20').replace(' ', '')).strip()
                    Supplier = bytes.fromhex(Supplier).strip().decode('utf-8')
                IdRsp_F194 = elm.request(req='22F194', positive='62', cache=False)
                if len(IdRsp_F194) > 8 and 'NR' not in IdRsp_F194 and 'BUS' not in IdRsp_F194 and '7F' not in IdRsp_F194:
                    Soft = trim(IdRsp_F194[9:].replace('00', '20').replace(' ', '')).strip()
                    Soft = bytes.fromhex(Soft).strip().decode('utf-8')
                IdRsp_F195 = elm.request(req='22F195', positive='62', cache=False)
                if len(IdRsp_F195) > 8 and 'NR' not in IdRsp_F195 and 'BUS' not in IdRsp_F195 and '7F' not in IdRsp_F195:
                    Version = trim(IdRsp_F195[9:].replace('00', '20').replace(' ', '')).strip()
                    Version = bytes.fromhex(Version).strip().decode('utf-8')
                elif Soft:
                    Version = Soft
                Std = 'STD_B'
                vinRsp = elm.request(req='22F190', positive='62', cache=False)
                if len(vinRsp) > 58:
                    VIN = trim(vinRsp[9:59].replace('00', '20').replace(' ', '')).strip()
                    VIN = bytes.fromhex(VIN).strip().decode('utf-8')
            else:
                pass
        else:
            IdRsp_0122 = elm.request(req='220122', positive='62', cache=False)
            if len(IdRsp_0122) > 8 and 'NR' not in IdRsp_0122 and 'BUS' not in IdRsp_0122 and '7F' not in IdRsp_0122:
                if True:
                    DiagVersion = '04'
                    Supplier = trim(IdRsp_0122[9:].replace('00', '20').replace(' ', '')).strip()
                    Supplier = bytes.fromhex(Supplier).strip().decode('utf-8')
                    Version = Supplier
                    IdRsp_0125 = elm.request(req='220125', positive='62', cache=False)
                    if len(IdRsp_0125) > 8 and 'NR' not in IdRsp_0125 and 'BUS' not in IdRsp_0125 and '7F' not in IdRsp_0125:
                        Soft = trim(IdRsp_0125[9:].replace('00', '20').replace(' ', '')).strip()
                    Std = 'STD_B'
                    vinRsp = elm.request(req='220120', positive='62', cache=False)
                    if len(vinRsp) > 58:
                        VIN = trim(vinRsp[9:59].replace('00', '20').replace(' ', '')).strip()
                        VIN = bytes.fromhex(VIN).strip().decode('utf-8')
                else:
                    pass
    return StartSession, DiagVersion, Supplier, Soft, Version, Std, VIN