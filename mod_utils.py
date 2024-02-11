import sys, string
import mod_globals
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown
from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
import kivy.metrics

def MyPopup_close(title='', cont='', l=True, op=True, cl=None):
    fs = mod_globals.fontSize
    layout = GridLayout(cols=1, padding=5, spacing=10, size_hint=(1, 1))
    t = 'CLOSE'
    
    btn = MyButton(text=t, size_hint=(1, None), font_size=fs*2)
    layout.add_widget(cont)
    layout.add_widget(btn)
    pop = MyPopup(title=title, content=layout)
    if cl:
        btn.bind(on_press=lambda *args:exit())
    else:
        btn.bind(on_press=lambda *args:pop.dismiss())
    if op:
        pop.open()
    else:
        return pop

class MyPopup(Popup):
    close = ''
    def __init__(self, **kwargs):
        fs = mod_globals.fontSize
        super(MyPopup, self).__init__(**kwargs)
        if 'title' not in kwargs:
            self.title='INFO'
        if 'auto_dismiss' not in kwargs:
            self.auto_dismiss=True
        if 'title_size' not in kwargs:
            self.title_size=str(fs) + 'sp'
        if 'content' not in kwargs:
            self.content=MyLabel(text='LOADING', size_hint = (1, 1))
        if 'title_align' not in kwargs:
            self.title_align='center'
        if 'size_hint' not in kwargs:
            self.size_hint=(None, None)
            self.size=(Window.size[0]*0.95, Window.size[1]*0.95)

class MyButton(Button):
    def __init__(self, **kwargs):
        fs = mod_globals.fontSize
        id = ''
        if 'id' in kwargs:
            self.id = kwargs['id']
            del kwargs ['id']
        super(MyButton, self).__init__(**kwargs)
        self.bind(size=self.setter('text_size'))
        if 'halign' not in kwargs:
            self.halign = 'center'
        if 'size_hint' not in kwargs:
            self.size_hint = (1, None)
        if 'font_size' not in kwargs:
            self.font_size = fs
        if 'valign' not in kwargs:
            self.valign = 'middle'
        if 'height' not in kwargs:
            lines = len(self.text.split('\n'))
            simb = round((len(self.text) * self.font_size) / (Window.size[0] * self.size_hint[0]), 2)
            if lines < simb: lines = simb
            if lines < 2: lines = lines * 1.5
            self.height = lines * self.font_size * 1.5
        if mod_globals.os == 'android':
            self.font_size = self.font_size * 0.8
        self.height = kivy.metrics.dp(self.height)
        self.font_size = kivy.metrics.dp(self.font_size)

def pyren_encode(inp):
    return inp.encode('utf-8', errors='replace')

def pyren_decode(inp):
    try:
        if mod_globals.os == 'android':
            return inp.decode('utf-8', errors='replace')
        else:
            return inp.decode(sys.stdout.encoding, errors='replace')
    except:
        return inp

def pyren_decode_i(inp):
    if mod_globals.os == 'android':
        return inp.decode('utf-8', errors='ignore')
    else:
        return inp.decode(sys.stdout.encoding, errors='ignore')

def clearScreen():
    sys.stdout.write(chr(27) + '[2J' + chr(27) + '[;H')

def hex_VIN_plus_CRC(VIN, plusCRC=True):
    VIN = VIN.upper()
    hexVIN = ''
    CRC = 65535
    for c in VIN:
        b = ord(c)
        hexVIN = hexVIN + hex(b)[2:].upper()
        for i in range(8):
            if (CRC ^ b) & 1:
                CRC = CRC >> 1
                CRC = CRC ^ 33800
                b = b >> 1
            else:
                CRC = CRC >> 1
                b = b >> 1

    CRC = CRC ^ 65535
    b1 = CRC >> 8 & 255
    b2 = CRC & 255
    CRC = (b2 << 8 | b1) & 65535
    sCRC = hex(CRC)[2:].upper()
    sCRC = '0' * (4 - len(sCRC)) + sCRC
    if plusCRC:
        return hexVIN + sCRC
    else:
        return hexVIN

def ASCIITOHEX(ATH):
    ATH = ATH.upper()
    hexATH = ''.join(('{:02x}'.format(ord(c)) for c in ATH))
    return hexATH

def StringToIntToHex(DEC):
    DEC = int(DEC)
    hDEC = hex(DEC)
    return hDEC[2:].zfill(2).upper()

def getVIN(de, elm, getFirst = False):
    import os
    m_vin = set([])
    for e in de:
        if mod_globals.opt_demo:
            loadDumpToELM(e['ecuname'], elm)
        else:
            if e['pin'].lower() == 'can':
                elm.init_can()
                elm.set_can_addr(e['dst'], e)
            else:
                elm.init_iso()
                elm.set_iso_addr(e['dst'], e)
            elm.start_session(e['startDiagReq'])
        if e['stdType'].lower() == 'uds':
            rsp = elm.request(req='22F190', positive='62', cache=False)[9:59]
        else:
            rsp = elm.request(req='2181', positive='61', cache=False)[6:56]
        if True:
            vin = rsp.replace(' ', '').decode('HEX')
        else:
            continue

        if len(vin) == 17:
            m_vin.add(vin)
            if getFirst:
                return vin

    l_vin = m_vin
    if os.path.exists('savedVIN.txt'):
        with open('savedVIN.txt') as vinfile:
            vinlines = vinfile.readlines()
            for l in vinlines:
                l = l.strip()
                if '#' in l:
                    continue
                if len(l) == 17:
                    l_vin.add(l.upper())

    if len(l_vin) == 0 and not getFirst:
        exit()
    if len(l_vin) < 2:
        if True:
            ret = next(iter(l_vin))
        else:
            ret = ''

        return ret
    choice = Choice(l_vin, 'Choose VIN : ')
    return choice[0]

def isHex(s):
    return all(c in string.hexdigits for c in s)