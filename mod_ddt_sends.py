import mod_globals
class ecu_sends:
    def __init__(self, sReq_lst, scr, decu=None):
        sReq_dl = {}
        sends = scr.findall("ns1:Send", mod_globals.ns)
        if sends:
            for send in sends:
                sDelay = '0'
                if "Delay" in send.attrib.keys():
                    sDelay = send.attrib["Delay"]
                sRequestName = ''
                if "RequestName" in send.attrib.keys ():
                    sRequestName = send.attrib["RequestName"]
                sReq_dl[sRequestName] = sDelay
                sReq_lst.append (sRequestName)