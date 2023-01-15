import mod_globals
class ecu_labels:
    def __init__(self, LValue, scr, decu=None):
        labels = scr.findall("ns1:Label", mod_globals.ns)
        if labels:
            slab = []
            for label in labels:
                xRect = label.findall("ns1:Rectangle", mod_globals.ns)
                if xRect:
                    xrHeight = int(xRect[0].attrib["Height"])
                    xrWidth = int(xRect[0].attrib["Width"])
                else:
                    xrHeight = 1
                    xrWidth = 1
                sq = xrHeight * xrWidth
                sl = {}
                sl['sq'] = sq
                sl['lb'] = label
                slab.append(sl)
            for lab in sorted(slab, key=lambda k: k['sq'], reverse=True):
                label = lab['lb']
                xText = label.attrib["Text"]
                xColor = label.attrib["Color"]
                xAlignment = label.attrib["Alignment"]
                xRect = label.findall("ns1:Rectangle", mod_globals.ns)
                if xRect:
                    xrLeft = int(xRect[0].attrib["Left"])
                    xrTop = int(xRect[0].attrib["Top"])
                    xrHeight = int(xRect[0].attrib["Height"])
                    xrWidth = int(xRect[0].attrib["Width"])
                xFont = label.findall ("ns1:Font", mod_globals.ns)
                if xFont:
                    xfName = xFont[0].attrib["Name"]
                    xfSize = float(xFont[0].attrib["Size"])
                    xfBold = xFont[0].attrib["Bold"]
                    xfItalic = xFont[0].attrib["Italic"]
                    xfColor = xFont[0].attrib["Color"]
                if xText == 'New label': continue
                if xrLeft < 0: xrLeft = 0
                if xrTop < 0: xrTop = 0
                xfBold = True if xfBold == '1' else False
                xfItalic = True if xfItalic == '1' else False
                if xAlignment == '1':
                    xAlignment = 'middle'
                    halign = 'center'
                elif xAlignment == '2':
                    xAlignment = 'top'
                    halign = 'center'
                else:
                    xAlignment = 'top'
                    halign = 'left'
                LValue.append({'sq':lab['sq'], 'values':[xText, xColor, xrLeft, xrTop, xrHeight, xrWidth, xfName, xfSize, xfBold, xfItalic, xfColor, xAlignment, halign]})