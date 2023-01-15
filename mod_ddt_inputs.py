import mod_globals
class ecu_inputs:
    def __init__(self, IValue, scr, decu=None):
        inputs = scr.findall('ns1:Input', mod_globals.ns)
        if inputs:
            for inp in inputs:
                try:
                    xText = inp.attrib['DataName']
                except:
                    xText = ''
                xReq = inp.attrib['RequestName']
                if not xText: xText = xReq
                xColor = inp.attrib['Color']
                xWidth = int(inp.attrib['Width'])
                if not xColor: xColor = '000000'
                xRect = inp.findall('ns1:Rectangle', mod_globals.ns)
                if xRect:
                    xrLeft = int(xRect[0].attrib['Left'])
                    xrTop = int(xRect[0].attrib['Top'])
                    xrHeight = int(xRect[0].attrib['Height'])
                    xrWidth = int(xRect[0].attrib['Width'])
                xFont = inp.findall('ns1:Font', mod_globals.ns)
                if xFont:
                    xfName = xFont[0].attrib['Name']
                    xfSize = float(xFont[0].attrib['Size'])
                    xfBold = xFont[0].attrib['Bold']
                    xfItalic = xFont[0].attrib['Italic']
                    xfColor = xFont[0].attrib['Color']
                if xrLeft < 0: xrLeft = 0
                if xrTop < 0: xrTop = 0
                xfBold = True if xfBold == '1' else False
                xfItalic = True if xfItalic == '1' else False
                xAlignment = 'middle'
                halign = 'center'
                IValue.append([xText, xReq, xColor, xWidth, xrLeft, xrTop, xrHeight, xrWidth, xfName, xfSize, xfBold, xfItalic, xfColor, xAlignment, halign])