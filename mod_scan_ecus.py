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
    if len(IdRsp) > 59:
        DiagVersion = str(int(IdRsp[21:23], 16))
        Supplier = IdRsp[24:32].replace(' ', '').strip().decode('hex').decode('ASCII', errors='ignore')
        Soft = IdRsp[48:53].strip().replace(' ', '')
        Version = IdRsp[54:59].strip().replace(' ', '')

        Std = 'STD_A'

        vinRsp = elm.request(req='2181', positive='61', cache=False)
        if len(vinRsp)>55 and 'NR' not in vinRsp:
            VIN = vinRsp[6:56].strip().replace(' ', '').decode('hex').decode('ASCII', errors='ignore')
    else:
        try:
            IdRsp_F1A0 = elm.request(req='22F1A0', positive='62', cache=False)
            if len(IdRsp_F1A0) > 8 and 'NR' not in IdRsp_F1A0 and 'BUS' not in IdRsp_F1A0:
                DiagVersion = str(int(IdRsp_F1A0[9:11], 16))
            IdRsp_F18A = elm.request(req='22F18A', positive='62', cache=False)
            if len(IdRsp_F18A) > 8 and 'NR' not in IdRsp_F18A and 'BUS' not in IdRsp_F18A:
                Supplier = IdRsp_F18A[9:].strip().replace(' ', '').decode('hex').decode('ASCII', errors='ignore')

            IdRsp_F194 = elm.request(req='22F194', positive='62', cache=False)
            if len(IdRsp_F194) > 8 and 'NR' not in IdRsp_F194 and 'BUS' not in IdRsp_F194:
                Soft = IdRsp_F194[9:].strip().replace(' ', '').decode('hex').decode('ASCII', errors='ignore')
            IdRsp_F195 = elm.request(req='22F195', positive='62', cache=False)
            if len(IdRsp_F195) > 8 and 'NR' not in IdRsp_F195 and 'BUS' not in IdRsp_F195:
                Version = IdRsp_F195[9:].strip().replace(' ', '').decode('hex').decode('ASCII', errors='ignore')

            Std = 'STD_B'
            vinRsp = elm.request(req='22F190', positive='62', cache=False)
            if len(vinRsp) > 58:
                VIN = vinRsp[9:59].strip().replace(' ', '').decode('hex').decode('ASCII', errors='ignore')
        except:
            pass
    if not DiagVersion.isalnum(): DiagVersion = '0'
    if not Supplier.isalnum(): Supplier = '000'
    if not Soft.isalnum(): Soft = '0000'
    if not Version.isalnum(): Version = '0000'
    return StartSession, DiagVersion, Supplier, Version, Soft, Std, VIN