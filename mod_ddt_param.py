import string
import mod_globals

def get_value(n, decu, elm, auto=True, request=None, responce=None, resp=None):
    try:
        r = decu.requests[n['request']].ReceivedDI[n['name']]
    except:
        r = decu.requests[n['request']].SentDI[n['name']]
    d = decu.datas[n['name']]
    if not resp:
        resp = elm.request(decu.requests[n['request']].SentBytes, '', True)
    resp = resp.strip().replace(' ', '')
    if not all((c in string.hexdigits for c in resp)):
        resp = ''
    resp = ' '.join((a + b for a, b in zip(resp[::2], resp[1::2])))
    if not r.FirstByte:
        r.FirstByte = 1
    hv = getHexVal(r, d, resp=resp)
    if hv == mod_globals.none_val:
        n['value'] = mod_globals.none_val
        return n

    if d.BytesASCII:
        res = bytes.fromhex(hv).decode('utf-8','replace')
        if not all(c in string.printable for c in res):
            if len(res) > 17:
                res = bytes.fromhex(hv[:-4]).decode('utf-8','replace')
            if not all(c in string.printable for c in res):
                res = hv
        n['value'] = res
        return n
    if d.Scaled:
        p = int(hv,16)
        if d.signed and p>(2**(d.BitsCount-1)-1):
            p = p-2**d.BitsCount
        res = (p*float(d.Step)+float(d.Offset))/float(d.DivideBy)
        if len(d.Format) and '.' in d.Format:
            acc = len(d.Format.split('.')[1])
            fmt = '%.'+str(acc)+'f'
            res = fmt%(res)
        res = str(res)
        if res.endswith('.0'): 
            res = res[:-2]
        if 'e-' in res:
            exp = int(res[-2:])
            if exp < 10:
                exp = 10
            res = "{:.{exp}f}".format(float(res), exp=exp)
        n['value'] = res
        return n
    n['value'] = hv
    return n

def getHexVal(r, d, auto=True, request=None, responce=None, resp=None):
    if resp==None:
        resp = self.elm.request(r.SentBytes, '', True, serviceDelay=1000)
    else:
        resp = resp
    sb = int(r.FirstByte) - 1
    bits = int(d.BitsCount)
    sbit = int(r.BitOffset)
    bytes = int((bits + sbit - 1) // 8 + 1)
    if r.Endian == 'Little':
        rshift = sbit
    else:
        rshift = ((bytes + 1) * 8 - (bits + sbit)) % 8
    if (sb * 3 + bytes * 3 - 1) > len(resp):
        return mod_globals.none_val
    hexval = resp[sb * 3:(sb + bytes) * 3 - 1]
    hexval = hexval.replace(' ', '')
    val = (int(hexval, 16) >> int(rshift)) & (2 ** bits - 1)
    hexval = hex(val)[2:]
    if hexval[-1:].upper() == 'L':
        hexval = hexval[:-1]
    if len(hexval) % 2:
        hexval = '0' + hexval
    if (len(hexval)/2)%bytes:
        hexval = '00' * (bytes - len(hexval)//2) + hexval
    if r.Endian == 'Little':
        a = hexval
        b = ''
        if not len(a) % 2:
            for i in range(0, len(a), 2):
                b = a[i:i + 2] + b

            hexval = b
    return hexval
