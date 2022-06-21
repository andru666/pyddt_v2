import mod_globals
class ecu_buttons:
    def __init__(self, BValue, dBtnSend, scr, decu=None):
        buttons = scr.findall("ns1:Button", mod_globals.ns)
        if buttons:
            for button in buttons:
                xText = button.attrib["Text"]
                xRect = button.findall("ns1:Rectangle", mod_globals.ns)
                if xRect:
                    xrLeft = int(xRect[0].attrib["Left"])
                    xrTop = int(xRect[0].attrib["Top"])
                    xrHeight = int(xRect[0].attrib["Height"])
                    xrWidth = int(xRect[0].attrib["Width"])
                xFont = button.findall ("ns1:Font", mod_globals.ns)
                if xFont:
                    xfName = xFont[0].attrib["Name"]
                    xfSize = float(xFont[0].attrib["Size"])
                    xfBold = xFont[0].attrib["Bold"]
                    xfItalic = xFont[0].attrib["Italic"]
                    if "Color" in xFont[0].attrib.keys():
                        xfColor = xFont[0].attrib["Color"]
                    else:
                        xfColor = '000000'
                xSends = button.findall("ns1:Send", mod_globals.ns)
                slist = []
                if len(xSends):
                    slist = []
                    for xSend in xSends:
                        smap = {}
                        xsDelay = xSend.attrib["Delay"]
                        xsRequestName = xSend.attrib["RequestName"]
                        smap['Delay'] = xsDelay
                        smap['RequestName'] = xsRequestName
                        if len(xsRequestName) > 0:
                            slist.append(smap)
                if len(slist):
                    dBtnSend[str(slist)] = slist
                if xrLeft < 0: xrLeft = 0
                if xrTop < 0: xrTop = 0
                xfBold = True if xfBold == '0' else False
                xfItalic = True if xfItalic == '0' else False
                xAlignment = 'middle'
                halign = 'center'
                BValue[str(slist)] = [xText, xrLeft, xrTop, xrHeight, xrWidth, xfName, xfSize, xfBold, xfItalic, xfColor, xAlignment, halign]