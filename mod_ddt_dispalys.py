import mod_globals
class ecu_dispalys:
    def __init__(self, DValue, scr, decu=None):
        dispalys = scr.findall("ns1:Display", mod_globals.ns)
        if dispalys:
            for dispaly in dispalys:
                xReq = ""
                if "RequestName" in dispaly.attrib.keys():
                    xReq = dispaly.attrib["RequestName"]
                xText = ""
                if "DataName" in dispaly.attrib.keys():
                    xText = dispaly.attrib["DataName"]
                else:
                    if len(decu.requests[xReq].ReceivedDI) == 1:
                        xText = decu.requests[xReq].ReceivedDI.keys()[0]
                    else:
                        xText = xReq
                if "Color" in dispaly.attrib.keys():
                    xColor = dispaly.attrib["Color"]
                else:
                    xColor = '0000000'
                xWidth = ""
                if "Width" in dispaly.attrib.keys():
                    xWidth = int(dispaly.attrib["Width"])
                xRect = dispaly.findall("ns1:Rectangle", mod_globals.ns)
                if xRect:
                    xrLeft = int(xRect[0].attrib["Left"])
                    xrTop = int(xRect[0].attrib["Top"])
                    xrHeight = int(xRect[0].attrib["Height"])
                    xrWidth = int(xRect[0].attrib["Width"])
                xFont = dispaly.findall("ns1:Font", mod_globals.ns)
                if xFont:
                    xfName = xFont[0].attrib["Name"]
                    xfSize = float(xFont[0].attrib["Size"])
                    xfBold = xFont[0].attrib["Bold"]
                    xfItalic = xFont[0].attrib["Italic"]
                    xfColor = xFont[0].attrib["Color"]
                if xrLeft < 0: xrLeft = 0
                if xrTop < 0: xrTop = 0
                xfBold = True if xfBold == '1' else False
                xfItalic = True if xfItalic == '1' else False
                xAlignment = 'middle'
                halign = 'center'
                DValue.append([xText, xReq, xColor, xWidth, xrLeft, xrTop, xrHeight, xrWidth, xfName, xfSize, xfBold, xfItalic, xfColor, xAlignment, halign])