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
    if len(IdRsp) > 59 and not IdRsp.startswith('7F'):
        DiagVersion = str(int(IdRsp[21:23], 16))
        Supplier = IdRsp[24:32].replace(' ', '').strip()
        Supplier = trim(bytes.fromhex(Supplier).decode('utf-8', 'ignore').strip())
        Soft = IdRsp[48:53].replace(' ', '').strip()
        Version = IdRsp[54:59].replace(' ', '').strip()
        Std = 'STD_A'
        vinRsp = elm.request(req='2181', positive='61', cache=False)
        if len(vinRsp)>55 and 'NR' not in vinRsp and not vinRsp.startswith('7F'):
            VIN = vinRsp[6:56].replace(' ', '').strip()
            VIN = trim(bytes.fromhex(VIN).decode('utf-8', 'ignore').strip())
    else:
        IdRsp_F1A0 = elm.request(req='22F1A0', positive='62', cache=False)
        if len(IdRsp_F1A0) > 9 and 'NR' not in IdRsp_F1A0 and 'BUS' not in IdRsp_F1A0 and not IdRsp_F1A0.startswith('7F'):
            if True:
                DiagVersion = str(int(IdRsp_F1A0[9:11], 16))
                IdRsp_F18A = elm.request(req='22F18A', positive='62', cache=False)
                if len(IdRsp_F18A) > 8 and 'NR' not in IdRsp_F18A and 'BUS' not in IdRsp_F18A and not IdRsp_F18A.startswith('7F'):
                    Supplier = IdRsp_F18A[9:].replace(' ', '').strip()
                    Supplier = trim(bytes.fromhex(Supplier).decode('utf-8', 'ignore').strip())
                IdRsp_F194 = elm.request(req='22F194', positive='62', cache=False)
                if len(IdRsp_F194) > 8 and 'NR' not in IdRsp_F194 and 'BUS' not in IdRsp_F194 and not IdRsp_F194.startswith('7F'):
                    Soft = IdRsp_F194[9:].replace(' ', '').strip()
                    Soft = trim(bytes.fromhex(Soft).decode('utf-8', 'ignore').strip())
                IdRsp_F195 = elm.request(req='22F195', positive='62', cache=False)
                if len(IdRsp_F195) > 8 and 'NR' not in IdRsp_F195 and 'BUS' not in IdRsp_F195 and not IdRsp_F195.startswith('7F'):
                    Version = IdRsp_F195[9:].replace(' ', '').strip()
                    Version = trim(bytes.fromhex(Version).decode('utf-8', 'ignore').strip())
                elif Soft:
                    Version = Soft
                Std = 'STD_B'
                vinRsp = elm.request(req='22F190', positive='62', cache=False)
                if len(vinRsp) > 58:
                    VIN = vinRsp[9:59].replace(' ', '').strip()
                    VIN = trim(bytes.fromhex(VIN).decode('utf-8', 'ignore').strip())
            else:
                pass
        else:
            IdRsp_0122 = elm.request(req='220122', positive='62', cache=False)
            if len(IdRsp_0122) > 8 and 'NR' not in IdRsp_0122 and 'BUS' not in IdRsp_0122 and not IdRsp_0122.startswith('7F'):
                if True:
                    DiagVersion = '04'
                    Supplier = IdRsp_0122[9:].replace(' ', '').strip()
                    Supplier = trim(bytes.fromhex(Supplier).decode('utf-8', 'ignore').strip())
                    Version = Supplier
                    IdRsp_0125 = elm.request(req='220125', positive='62', cache=False)
                    if len(IdRsp_0125) > 8 and 'NR' not in IdRsp_0125 and 'BUS' not in IdRsp_0125 and not IdRsp_0125.startswith('7F'):
                        Soft = (IdRsp_0125[9:].replace(' ', '')).strip()
                    Std = 'STD_B'
                    vinRsp = elm.request(req='220120', positive='62', cache=False)
                    if len(vinRsp) > 58:
                        VIN = vinRsp[9:59].replace(' ', '').strip()
                        VIN = trim(bytes.fromhex(VIN).decode('utf-8', 'ignore').strip())
                else:
                    pass
            else:
                IdRsp_6183 = elm.request(req='6183', positive='61', cache=False)
                if len(IdRsp) > 59 and not IdRsp.startswith('7F'):
                    DiagVersion = str(int(IdRsp[21:23], 16))
                    Supplier = IdRsp[24:32].replace(' ', '').strip()
                    Supplier = trim(bytes.fromhex(Supplier).decode('utf-8', 'ignore').strip())
                    Soft = IdRsp[48:53].replace(' ', '').strip()
                    Version = IdRsp[54:59].replace(' ', '').strip()
                    Std = 'STD_A'
                    vinRsp = elm.request(req='2181', positive='61', cache=False)
                    if len(vinRsp)>55 and 'NR' not in vinRsp and not vinRsp.startswith('7F'):
                        VIN = vinRsp[6:56].replace(' ', '').strip()
                        VIN = trim(bytes.fromhex(VIN).decode('utf-8', 'ignore').strip())
    return StartSession, DiagVersion, Supplier, Soft, Version, Std, VIN