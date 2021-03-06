#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os, ast, time, pickle, copy, string
from shutil import copyfile
from kivy import base
from kivy.app import App
from kivy.base import EventLoop
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput
from mod_ddt_param import *
from mod_ddt_labels import *
from mod_ddt_inputs import *
from mod_ddt_buttons import *
from mod_ddt_dispalys import *
from mod_ddt_sends import *
from mod_ddt_request import *
from mod_ddt_data import *
import xml.etree.ElementTree as et

from mod_elm import *
import mod_globals, mod_ddt_utils, mod_db_manager, mod_scan_ecus, mod_ddt_ecu

os.chdir(os.path.dirname(os.path.realpath(sys.argv[0])))

fs = mod_globals.fontSize
class MyScatterLayout(ScatterLayout):
    def __init__(self, **kwargs):
        super(MyScatterLayout, self).__init__(**kwargs)
        if 'bgcolor' in kwargs:
            self.bgcolor = kwargs['bgcolor']
        else:
            self.bgcolor =(0, 0, 0, 0)
        with self.canvas.before:
            Color(self.bgcolor[0], self.bgcolor[1], self.bgcolor[2], self.bgcolor[3])
            Rectangle(pos=self.pos, size=self.size)

class DDTLauncher(App):

    def __init__(self, opt_car=None, elm=None, savedCAR=None):
        self.eculist = mod_ddt_utils.loadECUlist()
        self.Window_size = mod_globals.windows_size

        self.filterText = opt_car
        global fs
        fs = mod_globals.fontSize
        
        self.carecus = []
        self.v_xmlList = []
        self.v_dumpList = []
        self.dv_addr = []
        
        self.ecutree = {}
        
        self.elm = elm
        self.clock_event = None
        self.scf = 10.0
        self.v_proj = self.filterText.split(':')[0].strip()
        self.labels = TextInput(text=self.v_proj, size_hint=(0.6, None), padding=[0, fs/1.5], font_size=fs, height=3*fs)
        self.v_addr = ''
        self.v_vin = ''
        self.v_pcan = ''
        self.v_mcan = ''
        self.dv_xml = ''
        self.var_log = ''
        self.var_can2 = ''
        self.var_cfc = ''
        self.var_port = ''
        self.var_speed = ''
        self.label = {}
        self.var_dump = mod_globals.opt_dump
        self.pl = mod_ddt_utils.ddtProjects()
        if mod_globals.savedCAR != 'Select':
            self.LoadCarFile(mod_globals.savedCAR)
        else:
            self.CarDoubleClick()
        if mod_globals.opt_scan:
            self.ScanAllBtnClick()
        
        super(DDTLauncher, self).__init__()

    def build(self):
        p = len(self.carecus)
        if not mod_globals.opt_demo: height_g = fs*4.07*len([v for v in range(len(self.carecus)) if self.carecus[v]['xml']])
        else: height_g = fs*4.07*(p)
        if height_g == 0: height_g = 200
        self.Layout = GridLayout(cols=1, spacing=3, size_hint=(1, None), height=self.Window_size[1])
        self.Layout.add_widget(self.make_savedECU())
        self.startStopButton = Button(text='', size_hint=(1, 1))
        box = GridLayout(cols=4, spacing=5, size_hint=(1, None), height=height_g)
        box111 = GridLayout(cols=4, spacing=5, size_hint=(1, None), height=fs*3)
        cols = ['addr', 'prot', 'name', 'xml', 'dump']
        Cols = dict(addr=['Addr', (1,0,0,1)], prot=['Protocol', (1,0,0,1)], name=['Name', (1,0,0,1)], xml=['XML', (1,0,0,1)], dump=['Dump', (1,0,0,1)])
        for key in cols:
            if key == 'addr':
                continue
            elif key == 'name':
                box1 = BoxLayout(orientation='vertical', spacing=1, size_hint=(0.4, 1))
                box11 = BoxLayout(orientation='vertical', spacing=1, size_hint=(0.4, 1))
            elif key == 'dump':
                box11 = BoxLayout(orientation='vertical', spacing=1, size_hint=(0.7, 1))
                box1 = BoxLayout(orientation='vertical', spacing=1, size_hint=(0.7, 1))
            elif key == 'xml':
                box1 = BoxLayout(orientation='vertical', spacing=1, size_hint=(1, 1))
                box11 = BoxLayout(orientation='vertical', spacing=1, size_hint=(1, 1))
            else:
                box1 = BoxLayout(orientation='vertical', spacing=1, size_hint=(0.3, 1))
                box11 = BoxLayout(orientation='vertical', spacing=1, size_hint=(0.3, 1))
            box11.add_widget(MyLabel(text=Cols[key][0], size_hint=(1, None), height=fs*3, bgcolor=Cols[key][1]))
            for v in self.carecus:
                if v['xml'] == '' and not mod_globals.opt_demo: continue
                if key == 'addr':
                    continue
                elif key == 'name':
                    self.but_xml = MyButton(text=v[key], id=v['addr'], size_hint=(1, None), on_press=self.popup_xml, height=fs*4, font_size=fs)
                    self.label[v['addr']] = self.but_xml
                    box1.add_widget(self.but_xml)
                elif key == 'dump':
                    self.but_dump = MyButton(text=v[key], id=v['addr']+'_dump', size_hint=(1, None), font_size=fs, height=fs*4, on_release=self.popup_dump)
                    self.label[v['addr']+'_dump'] = self.but_dump
                    box1.add_widget(self.but_dump)
                elif key == 'xml':
                    self.but_xml = MyButton(text=v[key], id=v['addr']+'_xml', size_hint=(1, None), font_size=fs, height=fs*4, on_release=self.openECUS)
                    self.label[v['addr']+'_xml'] = self.but_xml
                    box1.add_widget(self.but_xml)
                else:
                    self.label_prot = MyLabel(text=v['prot'], font_size=fs/1.3, id=v['addr']+'_prot', size_hint=(1, None), height=fs*4, bgcolor=(0.8,0,0,0.8))
                    self.label[v['addr']+'_prot'] = self.label_prot
                    box1.add_widget(self.label_prot)
            box111.add_widget(box11)
            box.add_widget(box1)
        root = ScrollView(size_hint=(1, None), height=self.Window_size[1]-(fs*10))
        root.add_widget(box)
        self.Layout.add_widget(box111)
        self.Layout.add_widget(root)
        quitbutton = MyButton(text='<QUIT>', size_hint=(1, None), height=fs*4, on_release=self.EXIT)
        self.Layout.add_widget(quitbutton)
        return self.Layout

    def EXIT(self, dt):
        exit()

    def openECUS(self, bt):
        self.xml = bt.text
        self.lbltxt = Label(text='Open Screens', title_size=fs)
        self.title = 'Loading'
        popup_init = Popup(title='Loading', content=self.lbltxt, size=(400, 400), size_hint=(None, None))
        popup_init.open()
        EventLoop.idle()
        ecu = self.getSelectedECU(self.xml)
        if ecu==None or ecu['xml']=='':
            self.MyPopup(content='Selected ECU is undefined. Please scan it first.', stop=1)
            return None
        self.OpenECUScreens(ecu)
        EventLoop.window.remove_widget(popup_init)
        popup_init.dismiss()

    def OpenECUScreens(self, ce):
        if not mod_globals.opt_demo and self.var_dump:
            mod_globals.opt_dump = True
        else:
            mod_globals.opt_dump = False
        if 'CAN' in ce['prot']:
            pro = 'CAN'
        else:
            pro = 'KWP'
        ct1 = time.time()
        if ce['prot'].startswith('CAN'):
            self.elm.init_can()
        else:
            self.elm.init_iso()
        ct2 = time.time()
        if ct2-ct1 > 5:
            self.MyPopup(title='ERROR', content='ELM is not responding well.', stop=1)
            return
        self.setEcuAddress(ce)
        self.elm.start_session(ce['ses'])
        decucashfile = os.path.join(mod_globals.cache_dir, "ddt_" + ce['xml'][:-4] + ".p")
        if os.path.isfile(decucashfile):
            self.decu = pickle.load(open(decucashfile, "rb"))
        else:
            self.decu = DDTECU(None)
            self.decu.loadXml('ecus/'+ce['xml'])
            if len(self.decu.ecufname) > 0:
                pickle.dump(self.decu, open(decucashfile, "wb"))
        self.decu.setELM(self.elm)
        if len(self.decu.ecufname) == 0:
            return
        if '/' in self.decu.ecufname:
            xfn = self.decu.ecufname[:-4].split('/')[-1]
        else:
            xfn = self.decu.ecufname[:-4].split('\\')[-1]
        dumpIs = False
        for root, dirs, files in os.walk(mod_globals.dumps_dir):
            for f in files:
                if (xfn + '.') in f:
                    dumpIs = True
                    break
        if mod_globals.opt_demo:            
            if len(ce['dump'])==0:
                self.lbltxt = Label(text='Loading dump', title_size=fs)
                popup_init = Popup(title='Loading', content=self.lbltxt, size=(400, 400), size_hint=(None, None))
                popup_init.open()
                EventLoop.idle()
                self.decu.loadDump()
                popup_init.dismiss()
            else:
                self.lbltxt = Label(text='Loading dump', title_size=fs)
                popup_init = Popup(title='Loading', content=self.lbltxt, size=(400, 400), size_hint=(None, None))
                popup_init.open()
                self.decu.loadDump(os.path.join(mod_globals.dumps_dir, ce['dump']))
                popup_init.dismiss()
        elif mod_globals.opt_dump:
            self.lbltxt = Label(text='Save dump', title_size=fs)
            popup_init = Popup(title='Loading', content=self.lbltxt, size=(400, 400), size_hint=(None, None))
            popup_init.open()
            EventLoop.idle()
            ce['dump'] = self.guiSaveDump(self.decu)
            for ec in self.carecus:
                if ce['xml'][:-4] in ec['xml']:
                    ec['dump'] = ce['dump']
            self.renewEcuList()
            self.SaveBtnClick(self.labels.text, None)
            popup_init.dismiss()

        if not mod_db_manager.file_in_ddt(self.decu.ecufname):
            return None
        tree = mod_db_manager.get_file_from_ddt(self.decu.ecufname)
        xdoc = et.parse(tree).getroot()
        self.DDTScreen(xdoc)
        self.show_screen(ce['xml'], self.screens)

    def show_screen(self, xml, data):
        self.make_box = False
        self.start = False
        self.clock_event = ''
        box = GridLayout(cols=1, spacing=3, size_hint=(1, None), height=fs*4*(len(data) + 2))
        self.Layout.clear_widgets()
        if isinstance(data, dict): datas = sorted(data.keys())
        else: datas = data
        for x in datas:
            if x == 'ddt_all_commands': continue
            button = MyButton(text=x, id=x, size_hint=(1, None), height=fs*4, on_release=lambda x=xml:self.res_show_screen(x,data))
            box.add_widget(button)
        if 'ddt_all_commands' in data:
            button = MyButton(text='ddt_all_commands', id='ddt_all_commands', size_hint=(1, None), height=fs*4, on_release=lambda x=xml:self.res_show_screen(x,data))
            box.add_widget(button)
        quitbutton = MyButton(text='<BACK>', size_hint=(1, None), height=fs*4)
        if isinstance(data, list):
            quitbutton.bind(on_release=lambda x=x:self.res_show_screen(x,self.screens))
        else:
            quitbutton.bind(on_release=self.stop)
        roots = ScrollView(size_hint=(1, None), height=self.Window_size[1]-fs*4)
        roots.add_widget(box)
        self.Layout.add_widget(roots)
        self.Layout.add_widget(quitbutton)

    def res_show_screen(self, x, data=None):
        x = x.text
        if x == '<Read DTC>': self.readDTC()
        elif x == '<BACK>': self.show_screen(x,data)
        elif isinstance(data, dict): self.show_screen(x,data[x])
        elif isinstance(data, list): self.loadScreen(x)

    def update_dInputs(self):
        for i in self.iValueNeedUpdate.keys():
            self.iValueNeedUpdate[i] = True

    def drop(self, i, optionList, f, H, W):
        self.dropdowns[i] = DropDown()
        W = W*self.flayout.scale
        if W*self.flayout.scale > self.Window_size[0]: W = self.Window_size[0]
        for o in optionList:
            btn = MyButton(text=o, id=o, font_size=int(f)*self.flayout.scale, size_hint=(None,None), size=(W,H*self.flayout.scale))
            btn.bind(on_release=lambda btn = btn, i = i: self.select_option(btn.text, i))
            self.dropdowns[i].add_widget(btn)
        self.dropdowns[i].bind(on_select=lambda instance, x: setattr(self.triggers[i], 'text', x))
        self.dropdowns[i].open(self.triggers[i])

    def select_option(self, bt, i):
        self.dropdowns[i].dismiss()
        self.oLabels[i].text = bt
        self.triggers[i].text = bt

    def startStop(self):
        if self.start:
            self.start = False
            self.startStopButton.text = 'START'
            self.clock_event = ''
        else:
            self.start = True
            self.startStopButton.text = 'STOP'

    def update_values(self, dt):
        if not self.start:
            return
        self.decu.elm.clear_cache()
        self.elm.clear_cache()
        try:
            params = self.get_ecu_values()
        except:
            return
        for key, val in params.iteritems():
            if key in self.dLabels.keys():
                self.dLabels[key].text = val
            elif key in self.iLabels.keys() and self.iValueNeedUpdate[key]:
                self.iLabels[key].text = val
                self.iValueNeedUpdate[key] = False
            elif key in self.oLabels.keys() and self.iValueNeedUpdate[key]:
                self.oLabels[key].text = val
                self.iValueNeedUpdate[key] = False
            elif key in self.Labels.keys():
                self.Labels[key].text = val
        if self.start:
            self.clock_event = Clock.schedule_once(self.update_values, 0.02)

    def get_ecu_values(self):
        dct = {}
        if len(self.dValue):
            for d in self.dValue.keys():
                if self.dValue[d]['request'] not in self.REQ: continue
                EventLoop.window._mainloop()
                val = get_value(self.dValue[d], self.decu, self.elm)
                if ':' in val:
                    val = val.split(':')[1]
                if d in self.iValue.keys() and self.iValueNeedUpdate[d] and val != mod_globals.none_val:
                    val = '0x' + val
                dct[d] = val
        return dct

    def change_screen(self, dt=False):
        if self.make_box:
            self.make_box = False
            self.update_dInputs()
            self.loadScreen(self.currentscreen)
        else:
            self.update_dInputs()
            self.make_box = True
            self.loadScreen(self.currentscreen)
    
    def loadScreen(self, scr):
        self.Layout.clear_widgets()
        self.start = True
        self.startStopButton = MyButton(text='', size_hint=(1, 1))
        if self.start:
            self.startStopButton.text = 'STOP'
        else:
            self.startStopButton.text = 'START'
        self.currentscreen = scr
        
        if scr in self.Screens.keys():
            scr = self.Screens[scr]
        if type(scr) is str or type(scr) is unicode:
            self.loadSyntheticScreen(scr)
            return
        scr_w = int(scr.attrib["Width"])
        scr_h = int(scr.attrib["Height"])
        self.scr_c = int(scr.attrib["Color"])
        if scr_w *2 <= self.Window_size[0]: self.scf = 1
        self.size_screen = (scr_w / self.scf, scr_h / self.scf)
        self.out = False
        self.DValue = {}
        self.IValue = {}
        self.LValue = []
        self.BValue = {}
        self.SValue = {}

        self.label = {}
        self.Labels = {}
        self.oLabels = {}
        self.dLabels = {}
        self.iLabels = {}
        self.bValue = {}
        self.dValue = {}
        self.iValue = {}
        self.iValueNeedUpdate = {}

        self.REQ = []
        self.dReq = {}
        self.sReq_lst = []
        self.sReq_dl = {}
        self.images = []
        self.dBtnSend = {}

        self.ListOption = {}
        self.dropdowns = {}
        self.triggers = {}
        
        box1 = GridLayout(cols=3, size_hint=(1, None), height=fs*3)
        box2 = GridLayout(cols=1, spacing=5, padding=5, size=(self.Window_size[0], self.Window_size[1]-fs*3), size_hint=(None, None))
        box1.add_widget(self.startStopButton)
        box1.add_widget(MyButton(text='CLOSE', size_hint=(1, 1), on_release=lambda x:self.show_screen(x, self.screens)))
        box1.add_widget(MyButton(text='Change view', size_hint=(1, 1), on_release=self.change_screen))
        self.Layout.add_widget(box1)
        self.startStopButton.bind(on_release=lambda args:self.startStop())
        if scr_w > scr_h:
            src = (scr_w*1.0 / scr_h)
        else:
            src = (scr_h*1.0 / scr_w)
        if src > self.scf/3: src = self.scf / src
        while src < 1.5: src = src * 1.1
        labels = ecu_labels(self.LValue, scr)
        dispalys = ecu_dispalys(self.DValue, scr, self.decu)
        buttons = ecu_buttons(self.BValue, self.dBtnSend, scr)
        inputs = ecu_inputs(self.IValue, scr)
        sends = ecu_sends(self.sReq_lst, scr)
        max_y = fs*3*(len(self.DValue)+len(self.IValue))
        if self.make_box:
            self.Layout.add_widget(MyLabel(text=self.currentscreen, color=(0,0,0,1), bgcolor=self.hex_to_rgb(self.scr_c)))
            if len(self.BValue):
                for b in self.BValue:
                    self.bValue[eval(b)[0]['RequestName']] = {'send':b, 'xText':self.BValue[b][0]}
            if len(self.DValue) > 0:
                for d in self.DValue:
                    xText, xReq, xColor, xWidth, xrLeft, xrTop, xrHeight, xrWidth, xfName, xfSize, xfBold, xfItalic, xfColor, xAlignment, halign = self.DValue[d]
                    if xText in self.decu.req4data.keys() and self.decu.req4data[xText] in self.decu.requests.keys():
                        self.dReq[self.decu.req4data[xText]] = self.decu.requests[self.decu.req4data[xText]].ManuelSend
                    if xText+'_'+xReq not in self.dValue.keys():
                        self.dValue[xText+'_'+xReq] = {'value':mod_globals.none_val, 'name':xText, 'request':xReq}
                    box2.add_widget(self.make_box_params(xText, xReq))
            if len(self.IValue) > 0:
                for i in self.IValue:
                    xReq, xColor, xWidth, xrLeft, xrTop, xrHeight, xrWidth, xfName, xfSize, xfBold, xfItalic, xfColor, xAlignment, halign = self.IValue[i]
                    if i+'_'+xReq not in self.iValue.keys():
                        if i+'_'+xReq not in self.dValue.keys():
                            self.dValue[i+'_'+xReq] = {'value':mod_globals.none_val, 'name':i, 'request':xReq}
                        if i in self.decu.req4data.keys() and self.decu.req4data[i] in self.decu.requests.keys():
                            self.dReq[self.decu.req4data[i]] = self.decu.requests[self.decu.req4data[i]].ManuelSend
                        self.iValue[i+'_'+xReq] = {'value':'', 'name':i, 'request':xReq}
                        self.iValueNeedUpdate[i+'_'+xReq] = True
                    if i in self.decu.datas.keys() and len(self.decu.datas[i].List.keys()):
                        optionList = []
                        if i+'_'+xReq not in self.iValue.keys():
                            self.iValue[i+'_'+xReq] = {'value':'', 'name':i, 'request':xReq}
                            self.iValueNeedUpdate[i+'_'+xReq] = True
                        for ii in self.decu.datas[i].List.keys():
                            optionList.append(hex(int(ii)).replace("0x", "").upper() + ':' + self.decu.datas[i].List[ii])
                        self.ListOption[i+'_'+xReq] = optionList
                        self.iValue[i+'_'+xReq] = {'value':optionList[0], 'name':i, 'request':xReq}
                    else:
                        self.iValue[i+'_'+xReq] = {'value':'Enter here', 'name':i, 'request':xReq}
                    box2.add_widget(self.make_box_params(i, xReq))
            box2.size[1] = len(self.dValue) * fs * 5
            if len(self.BValue):
                dv = []
                for d in self.dValue.values():
                    dv.append(d['request'])
                for b in self.BValue:
                    xText = self.BValue[b][0]
                    button = MyButton(text=xText, size_hint=(1, 1), id=b, on_release = lambda btn=xText, key=b: self.buttonPressed(btn.text, btn.id))
                    if len(self.BValue) == 1:
                        box2.size[1] = int(box2.size[1]) + fs * 5
                        box2.add_widget(button)
                    else:
                        if eval(b)[0]['RequestName'] not in dv:
                            box2.size[1] = int(box2.size[1]) + fs * 5
                            box2.add_widget(button)
            root = ScrollView(size_hint=(1, None), height=self.Window_size[1]-fs*5)
            root.add_widget(box2)
            self.Layout.add_widget(root)
        else:
            self.flayout = MyScatterLayout(size_hint=(None, None), bgcolor=self.hex_to_rgb(self.scr_c), size=self.size_screen, do_rotation=False)
            if len(self.LValue) > 0:
                for l in sorted(self.LValue, key=lambda k: k['sq'], reverse=True):
                    xText, xColor, xrLeft, xrTop, xrHeight, xrWidth, xfName, xfSize, xfBold, xfItalic, xfColor, xAlignment, halign = l['values']
                    self.flayout.add_widget(MyLabel_scr(text=xText, id=xText, halign=halign, color=self.hex_to_rgb(xfColor), bold=xfBold, italic=xfItalic, font_size=xfSize*src, valign=xAlignment, bgcolor=self.hex_to_rgb(xColor),  size_hint=(None, None), size=(xrWidth/self.scf, xrHeight/self.scf), pos=(xrLeft/self.scf, self.size_screen[1]-(xrHeight+xrTop)/self.scf)))
            
            if len(self.DValue) > 0:
                for d in self.DValue:
                    xText, xReq, xColor, xWidth, xrLeft, xrTop, xrHeight, xrWidth, xfName, xfSize, xfBold, xfItalic, xfColor, xAlignment, halign = self.DValue[d]
                    self.dReq[xReq] = self.decu.requests[xReq].ManuelSend
                    if xText+'_'+xReq not in self.dValue.keys():
                        self.dValue[xText+'_'+xReq] = {'value':mod_globals.none_val, 'name':xText, 'request':xReq}
                    
                    if xWidth/self.scf < (xfSize*len(xText)) and xfSize*src > xrHeight/self.scf/2:
                        xSize = xrHeight/self.scf/src/2.5
                    else:
                        xSize = xfSize
                    if xWidth/self.scf > 40:
                        label = MyLabel_scr(text=xText, id=d, valign=xAlignment, color=self.hex_to_rgb(xfColor), bold=xfBold, italic=xfItalic, font_size=xSize*src, halign='left', bgcolor=self.hex_to_rgb(xColor), size_hint=(None, None), size=(xWidth/self.scf, xrHeight/self.scf), pos=(xrLeft/self.scf, self.size_screen[1]-(xrTop+xrHeight)/self.scf))
                        self.flayout.add_widget(label)
                    label_D = MyLabel_scr(text=self.dValue[xText+'_'+xReq]['value'], id=d, valign=xAlignment, bgcolor=(0, 1, 0.8, 1), color=self.hex_to_rgb(xfColor), bold=xfBold, italic=xfItalic, font_size=xfSize*src, size_hint=(None, None), size=((xrWidth - xWidth)/self.scf, xrHeight/self.scf), pos=((xrLeft + xWidth)/self.scf, self.size_screen[1]-(xrTop+xrHeight)/self.scf))
                    self.dLabels[xText+'_'+xReq] = label_D
                    self.flayout.add_widget(label_D)
            
            if len(self.BValue) > 0:
                for b in self.BValue:
                    xText, xrLeft, xrTop, xrHeight, xrWidth, xfName, xfSize, xfBold, xfItalic, xfColor, xAlignment, halign = self.BValue[b]
                    button = MyButton(text=xText, text_size=(xrWidth/self.scf, xrHeight/self.scf), valign='middle', id=b, color=self.hex_to_rgb(xfColor), bold=xfBold, halign=halign, italic=xfItalic, font_size=xfSize*src, size_hint=(None, None), size=(xrWidth/self.scf, xrHeight/self.scf), pos=(xrLeft/self.scf, self.size_screen[1]-(xrTop+xrHeight)/self.scf))
                    button.bind(on_release = lambda btn=xText, key=b: self.buttonPressed(btn.text, btn.id))
                    self.flayout.add_widget(button)
            
            if len(self.IValue) > 0:
                for i in self.IValue:
                    xReq, xColor, xWidth, xrLeft, xrTop, xrHeight, xrWidth, xfName, xfSize, xfBold, xfItalic, xfColor, xAlignment, halign = self.IValue[i]
                    if xWidth/self.scf > 40:
                        label = MyLabel_scr(text=i, id=i, valign=xAlignment, color=self.hex_to_rgb(xfColor), bold=xfBold, italic=xfItalic, halign='left', font_size=xfSize*src, bgcolor=self.hex_to_rgb(xColor), size_hint=(None, None), size=(xrWidth/self.scf, xrHeight/self.scf), pos=(xrLeft/self.scf, self.size_screen[1]-(xrTop+xrHeight)/self.scf))
                        self.flayout.add_widget(label)
                    if i+'_'+xReq not in self.iValue.keys():
                        if i+'_'+xReq not in self.dValue.keys():
                            self.dValue[i+'_'+xReq] = {'value':mod_globals.none_val, 'name':i, 'request':xReq}
                        if i in self.decu.req4data.keys() and self.decu.req4data[i] in self.decu.requests.keys():
                            self.dReq[self.decu.req4data[i]] = self.decu.requests[self.decu.req4data[i]].ManuelSend
                        self.iValue[i+'_'+xReq] = {'value':'', 'name':i, 'request':xReq}
                        self.iValueNeedUpdate[i+'_'+xReq] = True
                    if i in self.decu.datas.keys() and len(self.decu.datas[i].List.keys()):
                        optionList = []
                        if i+'_'+xReq not in self.iValue.keys():
                            self.iValue[i+'_'+xReq] = {'value':'', 'name':i, 'request':xReq}
                            self.iValueNeedUpdate[i+'_'+xReq] = True
                        for ii in self.decu.datas[i].List.keys():
                            optionList.append(
                                hex(int(ii)).replace("0x", "").upper() + ':' + self.decu.datas[i].List[ii])
                        self.iValue[i+'_'+xReq] = {'value':optionList[0], 'name':i, 'request':xReq}
                        self.dropdowns[i+'_'+xReq] = DropDown(auto_width=False, width=xrWidth)
                        for o in optionList:
                            btn = MyButton(text=o, id=o, font_size=xfSize*src*self.flayout.scale, size_hint_y=None, height=xrHeight)
                            btn.bind(on_release=lambda btn=btn, i=i: self.select_option(btn.text, i))
                            self.dropdowns[i+'_'+xReq].add_widget(btn)
                        self.triggers[i+'_'+xReq] = MyButton(text=self.iValue[i+'_'+xReq]['value'], id=i+'_'+xReq, size_hint=(None, None), font_size=xfSize*src, size=((xrWidth - xWidth)/self.scf, xrHeight/self.scf), pos=((xrLeft + xWidth)/self.scf, self.size_screen[1]-(xrTop+xrHeight)/self.scf))
                        self.triggers[i+'_'+xReq].bind(on_release=lambda bt,L=optionList,f=xfSize*src,H=xrHeight/self.scf,W=(xrWidth - xWidth)/self.scf:self.drop(bt.id, L, f, H, W))
                        self.oLabels[i+'_'+xReq] = self.triggers[i+'_'+xReq]
                        self.dropdowns[i+'_'+xReq].bind(on_select=lambda instance, x: setattr(self.triggers[i+'_'+xReq], 'text', x))
                        
                        self.flayout.add_widget(self.triggers[i+'_'+xReq])
                    else:
                        self.iValue[i+'_'+xReq] = {'value':'Enter here', 'name':i, 'request':xReq}
                        label_IT = TextInput(text=self.iValue[i+'_'+xReq]['value'], valign=xAlignment, color=xfColor, bgcolor=xColor, bold=xfBold, italic=xfItalic, font_size=xfSize*src, size_hint=(None, None), size=((xrWidth - xWidth)/self.scf, xrHeight/self.scf), pos=((xrLeft + xWidth)/self.scf, self.size_screen[1]-(xrTop+xrHeight)/self.scf))
                        self.iLabels[i+'_'+xReq] = label_IT
                        self.flayout.add_widget(label_IT)
            box2.add_widget(self.flayout)
            self.Layout.add_widget(box2)
        if self.sReq_lst:
            self.startScreen(self.sReq_lst)
        if self.dReq:
            self.startScreen(self.dReq)
        
        self.update_dInputs()
        if self.start:
            self.clock_event = Clock.schedule_once(self.update_values, 0.02)

    def loadSyntheticScreen(self, rq):
        self.start = True
        self.Layout.clear_widgets()
        read_cmd = self.decu.requests[rq].SentBytes
        if read_cmd[:2]=='21':
            read_cmd = read_cmd[:4]
            write_cmd = '3B'+read_cmd[2:4]
        elif read_cmd[:2]=='22':
            read_cmd = read_cmd[:6]
            write_cmd = '2E'+read_cmd[2:6]
        
        self.dBtnSend = {}
        self.dValue = {}
        self.iValue = {}
        self.Value = {}
        self.bValue = {}
        self.iValueNeedUpdate = {}
        self.ListOption = {}
        self.dReq = {}
        self.REQ = []
        self.sReq_lst = []
        self.Labels = {}
        self.oLabels = {}
        self.dLabels = {}
        self.iLabels = {}
        
        self.ListOption = {}
        self.dropdowns = {}
        self.triggers = {}
        
        
        wc = ''
        set1 = set(self.decu.requests[rq].ReceivedDI.keys())
        set2 = []
        for r in self.decu.requests.keys():
            if self.decu.requests[r].SentBytes.startswith(write_cmd):
                set2 = set(self.decu.requests[r].SentDI.keys())
                if set1 == set2:
                    wc = r
                    break
        del(set1)
        del(set2)
        self.ListOption = {}
        max_x = self.Window_size[0]
        max_y = fs*3.5*(len(self.decu.requests[rq].ReceivedDI))
        box = GridLayout(cols=1, spacing=3, size_hint=(1, None), height=max_y)
        xText = self.decu.requests[rq].SentBytes + ' - ' + rq
        self.Layout.add_widget(MyLabel(text=xText))
        pn = 0
        for xText, zzz in sorted(self.decu.requests[rq].ReceivedDI.items(), key=lambda item: item[1].FirstByte):
            pn += 1
            yTop = 30 + pn * 40
            if xText not in self.dValue.keys():
                self.dValue[xText+'_'+rq] = {'value':mod_globals.none_val, 'name':xText, 'request':rq}
                if xText in self.decu.req4data.keys() and self.decu.req4data[xText] in self.decu.requests.keys():
                    self.dReq[self.decu.req4data[xText]] = self.decu.requests[self.decu.req4data[xText]].ManuelSend
            if len(wc)==0:
                box.add_widget(self.make_box_params(xText, rq))
            else:
                if xText+'_'+rq not in self.iValue.keys():
                    if xText not in self.dValue.keys():
                        self.dValue[xText+'_'+rq] = {'value':'', 'name':xText, 'request':rq}
                    if xText in self.decu.req4data.keys() and self.decu.req4data[xText] in self.decu.requests.keys():
                        self.dReq[self.decu.req4data[xText]] = self.decu.requests[self.decu.req4data[xText]].ManuelSend
                    self.iValue[xText+'_'+rq] = {'value':'', 'name':xText, 'request':rq}
                    self.iValueNeedUpdate[xText+'_'+rq] = True
                if xText in self.decu.datas.keys() and len(self.decu.datas[xText].List.keys()):
                    optionList = []
                    if xText+'_'+rq not in self.iValue.keys():
                        self.iValue[xText+'_'+rq] = {'value':'', 'name':xText, 'request':rq}
                        self.iValueNeedUpdate[xText+'_'+rq] = True
                    for i in self.decu.datas[xText].List.keys():
                        optionList.append(
                            hex(int(i)).replace("0x", "").upper() + ':' + self.decu.datas[xText].List[i])
                    self.ListOption[xText+'_'+rq] = optionList
                    self.iValue[xText+'_'+rq] = {'value':optionList[0], 'name':xText, 'request':rq}
                else:
                    self.iValue[xText+'_'+rq] = {'value':'Enter here', 'name':xText, 'request':rq}
                box.add_widget(self.make_box_params(xText, rq))
        if len(wc) > 0:
            slist = []
            smap = {}
            smap['Delay'] = 1000
            smap['RequestName'] = wc
            slist.append(smap)
            self.dBtnSend[str(slist)] = slist
            pn = pn + 1
            yTop = 30 + pn * 40
            box.add_widget(MyButton(text="Write", size_hint=(1, None), id=xText, height=fs*3, on_release = lambda btn,key=str(slist): self.buttonPressed(btn, key)))
        root = ScrollView(size_hint=(1, None), height=self.Window_size[1]-fs*6)
        root.add_widget(box)
        self.Layout.add_widget(root)
        self.decu.clearELMcache()
        self.update_dInputs()
        self.sReq_lst.append(rq)
        if self.sReq_lst:
            self.startScreen(self.sReq_lst)
        if self.dReq:
            self.startScreen(self.dReq)
        self.Layout.add_widget(MyButton(text='CLOSE', size_hint=(1, None), height=fs*3, on_release=lambda x:self.show_screen(x, self.screens)))
        if self.start:
            self.clock_event = Clock.schedule_once(self.update_values, 0.02)

    def readDTC(self):
        if "ReadDTCInformation.ReportDTC" in self.decu.requests.keys():
            requests = self.decu.requests["ReadDTCInformation.ReportDTC"]
        elif "ReadDTC" in self.decu.requests.keys():
            requests = self.decu.requests["ReadDTC"]
        else:
            self.MyPopup(content="No ReadDTC request for that ECU")
            return False
        shiftbytecount = requests.ShiftBytesCount
        bytestosend = map(''.join, zip(*[iter(requests.SentBytes.encode('ascii'))]*2))
        dtcread_command = ''.join(bytestosend)
        can_response = self.elm.request(dtcread_command)
        moredtcread_command = None
        if 'MoreDTC' in requests.SentDI.keys():
            moredtcfirstbyte = int(requests.SentDI['MoreDTC'].FirstByte)
            bytestosend[moredtcfirstbyte - 1] = "FF"
            moredtcread_command = ''.join(bytestosend)
        if "RESPONSE" in can_response or "DATA" in can_response or 'INIT' in can_response or not can_response:
            self.MyPopup(content="Invalid response for ReadDTC command")
            return
        can_response = can_response.split(' ')
        if can_response[0].upper() == "7F":
            self.MyPopup(content="Read DTC returned an error")
            return
        if len(can_response) == 2:
            self.MyPopup(content="No DTC")
            return
        maxcount = 50
        if moredtcread_command is not None:
            while maxcount > 0:
                more_can_response = self.elm.request(moredtcread_command)
                more_can_response = more_can_response.split(' ')
                if more_can_response[0].upper() == 'WRONG':
                    break
                can_response += more_can_response[2:]
                maxcount -= 1
        numberofdtc = int('0x' + can_response[1], 16)
        
        self.Layout.clear_widgets()
        self.Layout.add_widget(MyLabel(text='<Read DTC>', height=fs*3, bgcolor=(0.8,0,0,1), markup=True))
        root = ScrollView(size_hint=(1, None), height=self.Window_size[1]-fs*9)
        
        box = GridLayout(cols=1, size_hint=(1, None), height=fs)
        for dn in range(0, numberofdtc):
            box.add_widget(MyLabel(text='', height=fs*0.4, bgcolor=(0,0,0.2,1)))
            ln = MyLabel(text='[b]DTC #%i' % dn + '[/b]', bgcolor=(0,0.5,0,1), markup=True)
            box.add_widget(ln)
            box.height = box.height + ln.height + fs*0.4
            for k in requests.ReceivedDI.keys():
                if k == "NDTC":
                    continue
                value_hex = get_value({'request':requests.Name,'name':k}, self.decu, self.elm, resp=' '.join(can_response))
                if value_hex is None:
                    continue
                if len(self.decu.datas[k].List) > 0:
                    if ':' not in value_hex:
                        value = int('0x' + value_hex, 16)
                        box.add_widget(MyLabel(text='', height=fs*0.2, bgcolor=(1,1,0,1)))
                        l = MyLabel(text='[b]'+k+'[/b] : [' + str(value) + '] ' + hex(value), bgcolor=(0,0,0.5,1), markup=True)
                        box.add_widget(l)
                        box.height = box.height + fs*0.2 + l.height
                    else:
                        value = value_hex.split(':', 1)
                        box.add_widget(MyLabel(text='', height=fs*0.2, bgcolor=(1,1,0,1)))
                        l = MyLabel(text='[b]'+k+'[/b] : [' + str(value[0]) + '] ' + value[1], bgcolor=(0,0,0.5,1), markup=True)
                        box.add_widget(l)
                        box.height = box.height + fs*0.2 + l.height
            can_response = can_response[shiftbytecount:]
        root.add_widget(box)
        self.Layout.add_widget(root)
        self.Layout.add_widget(MyButton(text='Clear ALL DTC', size_hint=(1, None), height=fs*3, on_release=lambda args:self.dialogClearDTC()))
        self.Layout.add_widget(MyButton(text='CLOSE', size_hint=(1, None), height=fs*3, on_release=lambda x:self.show_screen(x, self.screens)))

    def dialogClearDTC(self):
        self.ButtonConfirmation('You are about to clear diagnostic troubles codes.\nAe you sure this is what you want.', 'clearDTC')

    def clearDTC(self):
        self.popup_confirm.dismiss()
        self.Layout.clear_widgets()
        self.Layout.add_widget(MyLabel(text='Clearing DTC information', bgcolor=(0,0.5,0.5,1)))
        if 'ClearDiagnosticInformation.All' in self.decu.requests.keys():
            requests = self.decu.requests['ClearDiagnosticInformation.All']
        elif 'ClearDTC' in self.decu.requests.keys():
            requests = self.decu.requests['ClearDTC']
        elif 'Clear Diagnostic Information' in self.decu.requests.keys():
            requests = self.decu.requests['Clear Diagnostic Information']
        else:
            self.Layout.add_widget(MyLabel(text="No ClearDTC request for that ECU, will send default 14FF00", bgcolor=(0,0.5,0,1)))
            request = "14FF00"
        self.setEcuAddress(self.getSelectedECU(self.xml))
        response = self.elm.request(request)
        if 'WRONG' in response:
            self.Layout.add_widget(MyLabel(text='There was an error clearing DTC.\n\nClear DTC failed', bgcolor=(0,0.5,0,1)))
        else:
            self.Layout.add_widget(MyLabel(text='Clear DTC successfully done', bgcolor=(0,0.5,0,1)))
        self.Layout.add_widget(MyButton(text='CLOSE', size_hint=(1, None), height=fs*3, on_release=lambda x:self.show_screen(x, self.screens)))

    def ScanAllBtnClick(self):
        self.addr = mod_ddt_utils.ddtAddressing(self.v_proj, self.eculist)
        ecus = {}
        for key, val in self.addr.alist.items():
            if len(val['xml']) == 1:
                ecus[val['xml'].keys()[0]] = {'prot':val['xml'].values()[0], 'addr':key, 'iso8':val['iso8']}
            if len(val['xml']) > 1:
                for k, v in val['xml'].items():
                    ecus[k] = {'prot':v, 'addr':key, 'iso8':val['iso8']}
        vins = {}
        self.scantxt = Label(text='Init', title_size=fs)
        popup_scan = Popup(title='Scanning CAN bus', title_size=fs*1.5, title_align='center', content=self.scantxt, size=(400, 400), size_hint=(None, None))
        base.runTouchApp(slave=True)
        popup_scan.open()
        EventLoop.idle()
        i = 0
        self.detectedEcus = {}
        x = 0
        p1=0
        self.back_can = ''
        for xml in self.addr.alist.values():
            x = x +len(xml['xml'])
        self.scantxt.text = 'Scanning:' + str(i) + '/' + str(x) + ' Detected: ' + str(len(self.detectedEcus))
        EventLoop.idle()
        for Addr, pro in self.addr.alist.items():
            if len(pro['xml']):
                if len(pro['xml']) > 1:
                    for p in sorted(pro['xml'].items(), key=lambda o: o[1], reverse=True):
                        if Addr in self.detectedEcus.keys():
                            i += 1
                            continue
                        p1 = p1+1
                        i += 1
                        self.cheks(Addr, p, i, x, vins, pro['iso8'])
                else:
                    p1 = p1+1
                    i += 1
                    self.cheks(Addr, pro['xml'].items()[0], i, x, vins, pro['iso8'])
        self.elm.close_protocol()
        for ce in self.carecus:
            if ce['addr'] in self.detectedEcus.keys():
                ce['xml'] = self.detectedEcus[ce['addr']]['xml']
                ce['iso8'] = self.detectedEcus[ce['addr']]['iso8']
                ce['ses'] = self.detectedEcus[ce['addr']]['ses']
                ce['undef'] = self.detectedEcus[ce['addr']]['undef']
                ce['dump'] = self.detectedEcus[ce['addr']]['dump']
                ce['prot'] = self.detectedEcus[ce['addr']]['prot']
        if self.v_vin=='' and len(vins.keys()):
            self.v_vin = (max(vins.iteritems(), key=operator.itemgetter(1))[0])
        if len(self.v_vin) > 0 and self.v_vin.isalnum():
            try:
                mod_globals.savedCAR = 'savedCAR_'+self.v_vin+'.csv'
                self.SaveBtnClick(self.v_vin, None)
            except:
                mod_globals.savedCAR = 'savedCAR_'+self.v_proj+'.csv'
                self.SaveBtnClick(self.v_proj, None)
        else:
            mod_globals.savedCAR = 'savedCAR_'+self.v_proj+'.csv'
            self.SaveBtnClick(self.v_proj, None)
        EventLoop.window.remove_widget(popup_scan)
        popup_scan.dismiss()
        base.stopTouchApp()
        EventLoop.window.canvas.clear()
        mod_globals.opt_scan = False
        self.renewEcuList()

    def cheks(self, Addr, pro, i, x, vins, iso):

        if pro[1].startswith('CAN'):
            self.elm.init_can()
        else:
            self.elm.init_iso()
        self.back_can = pro[1][:3]
        self.scantxt.text = 'Scanning:' + str(i) + '/' + str(x) + ' Detected: ' + str(len(self.detectedEcus))
        EventLoop.idle()
        self.setEcuAddress({'addr':Addr, 'prot':pro[1], 'iso8':iso})
        StartSession, DiagVersion, Supplier, Version, Soft, Std, VIN = mod_scan_ecus.readECUIds(self.elm)
        if DiagVersion == '' and Supplier == '' and Soft == '' and Version == '': return
        xml = mod_ddt_ecu.ecuSearch(self.v_proj, Addr, DiagVersion, Supplier, Soft, Version, self.eculist, interactive = False)
        if xml:
            if isinstance(xml, list): xml = xml[0]
            self.detectedEcus[Addr] = {'prot':pro[1], 'xml':xml,'ses':StartSession, 'undef':'0', 'iso8':iso}
            self.getDumpListByXml(xml)
            if len(self.v_dumpList) > 0:
                self.detectedEcus[Addr]['dump'] = self.v_dumpList[-1]
            else:
                self.detectedEcus[Addr]['dump'] = ''
            if VIN!='':
                if VIN not in vins.keys():
                    vins[VIN] = 1
                else:
                    vins[VIN] = vins[VIN] + 1

    def hex_to_rgb(self, hex_string):
        hex_string = hex(int(hex_string)).split('x')[-1]
        if hex_string == '0': return 0.0, 0.0, 0.0, 1.0
        while len(hex_string)<6: hex_string = '0'+hex_string
        try:
            r_hex = round(int(hex_string[0:2], 16)/255.0, 2)
        except:
            r_hex = 0
        try:
            g_hex = round(int(hex_string[2:4], 16)/255.0, 2)
        except:
            g_hex = 0
        try:
            b_hex = round(int(hex_string[4:6], 16)/255.0, 2)
        except:
            b_hex = 0
        return r_hex, g_hex, b_hex, 1.0

    def startScreen(self, data):
        for r in data:
            try:
                if data[r]: continue
            except:
                pass
            req = self.decu.requests[r].SentBytes
            if (req[:2] not in ['10'] + AllowedList) and not mod_globals.opt_exp:
                continue
            if r not in self.REQ: self.REQ.append(r)

    def ButtonConfirmation(self, text, data=None):
        layout = GridLayout(cols=1, padding=10, spacing=10, size_hint=(1, 1))
        box1 = BoxLayout(orientation='vertical', size_hint=(1, 0.8), height=fs * 2.0)
        box2 = BoxLayout(orientation='horizontal', size_hint=(1, 0.2), height=fs * 2.0)
        button1 = MyButton(text='YES')
        if not 'ERROR' in text: box2.add_widget(button1)
        button2 = MyButton(text='NO')
        box2.add_widget(button2)
        layout.add_widget(MyLabel(text=text))
        layout.add_widget(box1)
        layout.add_widget(box2)
        root = ScrollView(size_hint=(1, 1), size=self.Window_size)
        root.add_widget(layout)
        self.popup_confirm = Popup(title='Please confirm', title_size=fs*1.5, title_align='center', content=root, size=self.Window_size, size_hint=(None, None))
        self.popup_confirm.open()
        if data == 'clearDTC':
            button1.bind(on_press=lambda k:self.clearDTC())
        else:
            button1.bind(on_press=lambda k:self.yes(data))
        button2.bind(on_release=self.no)

    def no(self, instance):
        self.popup_confirm.dismiss()
        self.start = True
        return False

    def yes(self, slist):
        self.popup_confirm.dismiss()
        confirmed = True
        if confirmed:
            for c in slist:
                r = c['r']
                rsp = '00'
                rsp = self.decu.elmRequest (c['c'], c['d'], cache=False)
        self.start = Clock.schedule_once(self.update_values, 0.02)
        self.update_dInputs()

    def buttonPressed(self, btn, key):
        self.start = False
        layout = GridLayout(cols=1, padding=10, spacing=10, size_hint=(1, 1))
        for i in self.iValue.keys():
            if i in self.iLabels:
                self.iValue[i]['value'] = self.iLabels[i].text
            elif i in self.oLabels:
                self.iValue[i]['value'] = self.oLabels[i].text
            elif i in self.Labels:
                self.iValue[i]['value'] = self.Labels[i].text
        self.decu.clearELMcache()
        if key in self.dBtnSend.keys():
            sends = self.dBtnSend[key]
        else:
            return
        slist = []
        smap = {}
        error = False
        for send in sends:
            delay = send['Delay']
            requestName = send['RequestName']
            r = self.decu.requests[requestName]
            sendCmd = self.decu.packValues (requestName, self.iValue)
            if 'ERROR' in sendCmd:
                self.ButtonConfirmation(sendCmd)
                return
            smap['d'] = delay
            smap['c'] = sendCmd
            smap['r'] = r
            slist.append (copy.deepcopy (smap))
        commandSet = '\n\n'
        for c in slist:
            commandSet += "%-10s Delay:%-3s (%s)\n" % (c['c'], c['d'], c['r'].Name)
        self.ButtonConfirmation(commandSet, self.yes(slist))

    def setEcuAddress(self, ce):
        ecudata = {'idTx': '',
                   'idRx': '',
                   'slowInit': '',
                   'fastInit': '',
                   'ModelId': ce['addr'],
                   'ecuname': 'ddt_unknown',
                   }
        if ce['prot'].startswith('CAN'):
            if ce['prot'] == 'CAN-250':
                ecudata['protocol'] = 'CAN_250'
                ecudata['brp'] = '01'
            else:
                ecudata['protocol'] = 'CAN_500'
                ecudata['brp'] = '0'

            ecudata['pin'] = 'can'
            self.elm.set_can_addr(ce['addr'], ecudata)
        if ce['prot'].startswith('KWP') or ce['prot'].startswith('ISO'):
            if ce['prot'] == 'KWP-FAST':
                ecudata['protocol'] = 'KWP_Fast'
                ecudata['fastInit'] = ce['addr']
                ecudata['slowInit'] = ''
                mod_globals.opt_si = False
            elif ce['prot'] == 'ISO8' and ce['iso8'] != '':
                ecudata['protocol'] = 'KWP_Slow'
                ecudata['fastInit'] = ''
                ecudata['slowInit'] = ce['iso8']
                mod_globals.opt_si = True
            else:
                ecudata['protocol'] = 'KWP_Slow'
                ecudata['fastInit'] = ''
                ecudata['slowInit'] = ce['addr']
                mod_globals.opt_si = True
            ecudata['pin'] = 'iso'
            self.elm.set_iso_addr(ce['addr'], ecudata)

    def getSelectedECU(self, xml):
        if len(self.ecutree)==0:
            pop = "Please select the project in the left list and then ECU in the bottom"
        else:
            pop = "Please select an ECU in the bottom list"
        if not xml:
            Clock.schedule_once(lambda args:self.MyPopup(content=pop), 0.1)
            return None
        else:
            try:
                line = [self.ecutree[v]['values'] for v in range(len(self.ecutree)) if xml in self.ecutree[v]['values']][0]
            except:
                self.MyPopup(content=pop)
                return None
            try:
                ecu = ast.literal_eval(line[4])
            except:
                import json
                ecu = ast.literal_eval(json.dumps(line[4], ensure_ascii=False).encode('utf8'))
            return ecu

    def popup_dump(self, bt):
        test = self.getDumpListByXml(self.label[bt.id[:-5]+'_xml'].text)
        lbltxt = Label(text='SCANNING DUMP FILE', title_size=fs)
        popup_init = Popup(title='Loading', title_size=fs*1.5, title_align='center', content=lbltxt, size_hint=(1, 1))
        popup_init.open()
        EventLoop.idle()
        sys.stdout.flush()
        id = bt.id
        layout = GridLayout(cols=1, spacing=5, size_hint=(1, None))
        layout.bind(minimum_height=layout.setter('height'))
        layout.add_widget(MyButton(text='CLEAR', size_hint=(1, None), height=fs*4, on_press=lambda bts,ids=bt.id: self.select_dump(bts, ids)))
        for v in self.v_dumpList:
            btn = MyButton(text=v, size_hint=(1, None), height=fs*4, on_press=lambda bts, ids = bt.id: self.select_dump(bts, ids))
            layout.add_widget(btn)
        self.root_dump = ScrollView(size_hint=(1, 1))
        self.root_dump.add_widget(layout)
        popup_init.dismiss()
        btn_close = MyButton(text='CLOSE', size_hint=(1, None), height=fs*4)
        layout.add_widget(btn_close)
        self.popup = Popup(title='Select dump', title_size=fs*1.5, title_align='center', content=self.root_dump, size_hint=(None, None), size=(self.Window_size[0], self.Window_size[1]*0.7))
        self.popup.open()
        btn_close.bind(on_press=self.popup.dismiss)

    def select_dump(self, bt, idds):
        addr = idds.split('_')[0]
        for n in self.carecus:
            if n['addr'] == addr:
                n['dump'] = bt.text
        if bt.text == 'CLEAR': bt.text = ''
        self.label[idds].text = bt.text
        self.popup.dismiss()
        self.renewEcuList()

    def getDumpListByXml(self, xmlname=None):
        if xmlname==None:
            self.v_dumpList = []
            try:
                xml = self.dv_xml[:-4]
            except:
                xml = ''
            for root, dirs, files in os.walk(os.path.join(mod_globals.user_data_dir, 'dumps')):
                for f in files:
                    if (xml + '.') in f:
                        self.v_dumpList.append(f)
        else:
            xmlname = xmlname[:-4]
            self.v_dumpList = []
            for root, dirs, files in os.walk(os.path.join(mod_globals.user_data_dir, 'dumps')):
                for f in files:
                    if (xmlname + '.') in f:
                        self.v_dumpList.append(f)
            
    def popup_xml(self, inst):
        lbltxt = Label(text='SCANNING XML FILE', title_size=fs)
        popup_init = Popup(title='Loading', title_size=fs*1.5, title_align='center', content=lbltxt, size_hint=(1, 1))
        popup_init.open()
        EventLoop.idle()
        sys.stdout.flush()
        self.dv_addr = inst
        layout = GridLayout(cols=1, spacing=5, size_hint=(1, None))
        layout.bind(minimum_height=layout.setter('height'))
        layout.add_widget(MyButton(text='CLEAR', size_hint=(1, None), id=inst.id, height=fs*4, on_press=lambda i,k='',v='': self.select_xml(i,k,v)))
        for k, v in self.addr.alist[inst.id]['xml'].iteritems():
            btn = MyButton(text=k, size_hint=(1, None), id=inst.id, height=fs*4, on_press=lambda i,k=k,v=v: self.select_xml(i,k,v))
            layout.add_widget(btn)
        btn_close = MyButton(text='CLOSE', size_hint=(1, None), height=fs*4)
        layout.add_widget(btn_close)
        self.root_xml = ScrollView(size_hint=(1, 1))
        self.root_xml.add_widget(layout)
        popup_init.dismiss()
        self.popup = Popup(title='Select xml ECU', title_size=fs*1.5, title_align='center', content=self.root_xml, size_hint=(None, None), size=(self.Window_size[0], self.Window_size[1]*0.9))
        self.popup.open()        
        btn_close.bind(on_press=self.popup.dismiss)

    def select_xml(self, bt, k, v):
        addr = bt.id
        for n in self.carecus:
            if n['addr'] == addr:
                n['prot'] = v
                n['xml'] = k
        self.label[addr+'_prot'].text = v
        self.label[addr+'_xml'].text = k
        self.popup.dismiss()
        self.renewEcuList()

    def make_savedECU(self):
        glay = GridLayout(cols=4, size_hint=(1, None), height=3*fs)
        label1 = MyLabel(text='Name savedCAR:', size_hint=(0.5, 1), bgcolor=(0,0.5,0,1))
        if self.v_vin.isalnum():
            self.labels.text = self.v_vin
        elif mod_globals.savedCAR[9:-4] != '' and mod_globals.savedCAR[9:-4].isalnum():
            self.labels.text = mod_globals.savedCAR[9:-4]
        self.savedECU = MyButton(text='Save', size_hint=(0.5, 1), on_press=lambda args: self.SaveBtnClick(self.labels.text))
        glay.add_widget(label1)
        glay.add_widget(MyLabel(text='savedCAR_', size_hint=(0.34, 1), halign='right', bgcolor=(0.5,0,0,1)))
        glay.add_widget(self.labels)
        glay.add_widget(self.savedECU)
        return glay

    def DDTScreen(self, xdoc):
        self.Screens = {}
        self.screens = {}
        self.screens['<Read DTC>'] = ''
        categs = xdoc.findall ("ns0:Target/ns1:Categories/ns1:Category", mod_globals.ns)
        if len(categs):
            for cat in categs:
                catname = cat.attrib["Name"]
                self.screens[catname] = []
                screens = cat.findall ("ns1:Screen", mod_globals.ns)
                if len(screens):
                    for scr in screens:
                        scrname = scr.attrib["Name"]
                        self.screens[catname].append(scrname)
                        self.Screens[scrname] = scr
        self.screens['ddt_all_commands'] = []
        for req in sorted(self.decu.requests.keys()):
            if self.decu.requests[req].SentBytes[:2] in ['21','22']:
                self.screens['ddt_all_commands'].append(req)

    def CarDoubleClick(self):
        self.addr = mod_ddt_utils.ddtAddressing(self.filterText.split(':')[0].strip(), self.eculist)
        for e in self.addr.alist:
            if len(self.addr.alist[e]['xml']) > 0:
                if len(self.addr.alist[e]['xml']) == 1:
                    v_xml = self.addr.alist[e]['xml'].keys()[0]
                    v_prot = self.addr.alist[e]['xml'].values()[0]
                else:
                    v_prot = ''
                    v_xml = ''
                ecu = {}
                ecu['undef'] = '1'
                ecu['iso8'] = self.addr.alist[e]['iso8']
                ecu['addr'] = e
                ecu['name'] = self.addr.alist[e]['FuncName']
                if not mod_globals.opt_scan:
                    ecu['xml'] = v_xml
                    ecu['prot'] = v_prot
                else:
                    ecu['xml'] = ''
                    ecu['prot'] = ''
                ecu['dump'] = ''
                ecu['ses'] = ''
                self.dv_addr = ecu['addr']
                self.carecus.append(ecu)
        self.renewEcuList()

    def getXmlListByProj(self):
        self.v_xmlList = []
        try:
            for t in self.eculist[self.dv_addr]['targets']:
                if self.v_proj.upper() in self.eculist[self.dv_addr]['targets'][t]['Projects']:
                    self.v_xmlList.append(t)
        except:
            pass

    def renewEcuList(self):
        self.ecutree = []
        for ecu in mod_ddt_utils.multikeysort(self.carecus, ['undef','addr']):
            columns = (ecu['prot'], ecu['name'], ecu['xml'], ecu['dump'], ecu)
            if ecu['undef']=='0':
                self.ecutree.append(dict(text=ecu['addr'], values=columns, tag='t1'))
            else:
                self.ecutree.append(dict(text=ecu['addr'], values=columns, tag=''))

    def SaveBtnClick(self, name, pop=True):
        if not name or not name.isalnum(): name = self.v_proj
        filename = os.path.join(mod_globals.user_data_dir, './savedCAR_'+str(name)+'.csv')
        with open(filename, 'w') as fout:
            car = ['car',self.v_proj, self.v_addr, self.v_pcan, self.v_mcan, self.v_vin]
            fout.write(';'.join(car)+'\n')
            for ecu in self.carecus:
                e = [ecu['undef'],
                     ecu['addr'],
                     ecu['iso8'],
                     ecu['prot'],
                     ecu['name'],
                     ecu['xml'],
                     ecu['dump'],
                     ecu['ses']]
                fout.write(unicode(';'.join(e)).encode("ascii", "ignore") + '\n')
        self.renewEcuList()
        mod_globals.savedCAR = 'savedCAR_'+str(name)+'.csv'
        copyfile(filename, os.path.join(mod_globals.user_data_dir, "./savedCAR_prev.csv"))
        if pop: self.MyPopup(content='Save file ECUS name savedCAR_'+name+'.csv', height=fs*30)
        return

    def LoadCarFile(self, filename):
        filename = os.path.join(mod_globals.user_data_dir, filename)
        if not os.path.isfile(filename):
            return
        with open(filename, 'r') as fin:
            lines = fin.read().splitlines()
 
        self.carecus = []
        for l in lines:
            l = l.strip()
            if len(l)==0 or l.startswith('#'):
                continue
            li = l.split(';')
            if li[0].lower()=='car':
                self.v_proj = li[1]
                self.v_addr = li[2]
                self.v_pcan = li[3]
                self.v_mcan = li[4]
                self.v_vin = li[5]
            else:
                ecu = {}
                ecu['undef'] = li[0]
                ecu['addr'] = li[1]
                ecu['iso8'] = li[2]
                ecu['prot'] = li[3]
                ecu['name'] = li[4]
                ecu['xml'] = li[5]
                ecu['dump'] = li[6]
                ecu['ses']  = li[7]
                self.carecus.append(ecu)
        self.addr = mod_ddt_utils.ddtAddressing(self.v_proj, self.eculist)
        self.renewEcuList()

    def make_box_params(self, i, v):
        glay = GridLayout(cols=2, size_hint=(1, 1))
        label1 = MyLabelBlue(text=i, halign='left', valign='middle', size_hint=(1, 1), font_size=fs)
        glay.add_widget(label1)
        if i+'_'+v in self.dValue:
            label_D = MyLabelGreen(text=self.dValue[i+'_'+v]['value'], size_hint=(1, 1))
            self.Labels[i+'_'+v] = label_D
            glay.add_widget(label_D)
        if i+'_'+v in self.iValue:
            glay.cols = 3
            if self.iValue[i+'_'+v]['value'] == 'Enter here':
                label_IT = TextInput(text=self.iValue[i+'_'+v]['value'], size_hint=(1, 1))
                self.Labels[i] = label_IT
                glay.add_widget(label_IT)
        if i+'_'+v in self.ListOption.keys():
            glay.cols = 3
            self.dropdowns[i+'_'+v] = DropDown(auto_width=False, width=self.Window_size[0]*0.8)
            for o in self.ListOption[i+'_'+v]:
                btn = MyButton(text=o, id=o, size_hint=(1, None), height=fs*3)
                btn.bind(on_release=lambda btn=btn, i=i+'_'+v: self.select_option(btn.text, i))
                self.dropdowns[i+'_'+v].add_widget(btn)
            self.triggers[i+'_'+v] = MyButton(text=self.ListOption[i+'_'+v][0], id=i, size_hint=(1, 1))
            self.triggers[i+'_'+v].bind(on_release=self.dropdowns[i+'_'+v].open)
            self.oLabels[i+'_'+v] = self.triggers[i+'_'+v]
            self.dropdowns[i+'_'+v].bind(on_select=lambda instance, x: setattr(self.triggers[i+'_'+v], 'text', x))
            glay.add_widget(self.triggers[i+'_'+v])
        if v in self.bValue.keys() and len(self.BValue) > 1:
            glay.cols = 4
            button = MyButton(text=self.bValue[v]['xText'], id=str(self.bValue[v]['send']), size_hint=(1, 1), on_release = lambda btn=self.bValue[v]['xText']: self.buttonPressed(btn.text, btn.id))
            glay.add_widget(button)
        if glay.cols == 2:
            glay.size_hint = (1, None)
            glay.height = fs * 3
        return glay

    def MyPopup(self, close=True, title=None, content=None, height=None, weigh=None, stop=None):
        if title:
            title = title
        else:
            title = 'INFO'
        if content:
            content = content
        else:
            content = 'INFO'
        if not height:
            height = self.Window_size[1]*0.7
        if not weigh:
            weigh = self.Window_size[0]*0.8
        label = MyLabel(text=content, size_hint=(1, 1))
        layout = GridLayout(cols=1, padding=10, spacing=20, size_hint=(1, 1))
        layout.add_widget(label)
        btn = MyButton(text='CLOSE')
        if close: layout.add_widget(btn)
        popup = Popup(title=title, title_size=fs*1.5, title_align='center', content=layout, size_hint=(None, None), size=(weigh, height))
        popup.open()
        if stop:
            btn.bind(on_press=self.stop)
        else:
            btn.bind(on_press=popup.dismiss)

    def guiSaveDump(self,decu):
        xmlname = decu.ecufname
        if xmlname.upper().endswith('.XML'):
            xmlname = xmlname[:-4]

        if '/' in xmlname:
            xmlname = xmlname.split('/')[-1]
        else:
            xmlname = xmlname.split('\\')[-1]
        dumpFileName = str(int(time.time())) + '_' + xmlname + '.txt'
        df = open(os.path.join(mod_globals.dumps_dir, dumpFileName), 'wt')
        decu.elm.clear_cache()

        max = len(decu.requests.keys())

        progressValue = 1

        im = ' from ' + str(max)
        i = 0
        for request in decu.requests.values():
            i = i + 1
            progressValue = progressValue + 1
            sys.stdout.flush()
            if request.SentBytes[:2] in AllowedList + ['17', '19']:
                if request.SentBytes[:2] == '19' and request.SentBytes[:2] != '1902':
                    continue
                pos = chr(ord(request.SentBytes[0]) + 4) + request.SentBytes[1]
                rsp = decu.elm.request(request.SentBytes, pos, False)
                if ':' in rsp: continue
                df.write('%s:%s\n' % (request.SentBytes, rsp))
        df.close()
        return dumpFileName

def DDT_START(filterText, elm=None):
    while 1:
        root = DDTLauncher(filterText, elm)
        root.run()

class MyLabel_scr(Label):
    def __init__(self, **kwargs):
        super(MyLabel_scr, self).__init__(**kwargs)
        if 'bgcolor' in kwargs:
            self.bgcolor = kwargs['bgcolor']
        else:
            self.bgcolor =(0, 0, 0, 0)
        self.bind(size=self.setter('text_size'))
        if 'halign' not in kwargs:
            self.halign = 'center'
        if 'valign' not in kwargs:
            self.valign = 'middle'
        if 'height' not in kwargs:
            self.height = self.size[1]
        if 'size' in kwargs:
            self.size[0] = self.size[0]*0.99
        if 'pos' in kwargs:
            self.pos[0] = self.pos[0]*1.01
    def on_size(self, *args):
        if not self.canvas:
            return
        self.canvas.before.clear()
        """with self.canvas.before:
            Color(0, 0, 0, 1)
            Rectangle(pos=(self.pos[0], self.pos[1]), size=(self.size[0], self.size[1]))"""
        with self.canvas.before:
            Color(self.bgcolor[0], self.bgcolor[1], self.bgcolor[2], self.bgcolor[3])
            Rectangle(pos=(self.pos[0]/1.01, self.pos[1]), size=(self.size[0]/0.99, self.size[1]))
            
class MyLabel(Label):
    global fs
    def __init__(self, **kwargs):
        fs = mod_globals.fontSize
        if 'bgcolor' in kwargs:
            self.bgcolor = kwargs['bgcolor']
        else:
            self.bgcolor =(0, 0, 0, 0)
        super(MyLabel, self).__init__(**kwargs)
        self.bind(size=self.setter('text_size'))
        if 'halign' not in kwargs:
            self.halign = 'center'
        if 'valign' not in kwargs:
            self.valign = 'middle'
        if 'font_size' not in kwargs:
            self.font_size = fs
        if 'size_hint' not in kwargs:
            self.size_hint =(1, None)
        if 'size' in kwargs:
            self.size[0] = self.size[0]+4
        if 'pos' in kwargs:
            self.pos[0] = self.pos[0]+4
        if 'height' not in kwargs:
            fmn = 1.3
            lines = len(self.text.split('\n'))
            simb = len(self.text) / 60
            if lines < simb: lines = simb
            if lines < 2: lines = 2
            if lines > 20: lines = 20
            if 1 > simb: lines = 2
            if fs > 20: 
                lines = lines * 1.05
            self.height = fmn * lines * fs

    def on_size(self, *args):
        if not self.canvas:
            return
        self.canvas.before.clear()
        with self.canvas.before:
            Color(self.bgcolor[0], self.bgcolor[1], self.bgcolor[2], self.bgcolor[3])
            Rectangle(pos=self.pos, size=self.size)

class MyLabelGreen(Label):
    def __init__(self, mfs = None, **kwargs):
        super(MyLabelGreen, self).__init__(**kwargs)
        self.text_size = self.size
        self.bind(size=self.on_size)
        if 'halign' not in kwargs:
            self.halign = 'center'
    def on_size(self, widget, size):
        self.text_size =(size[0], None)
        self.texture_update()
        if self.size_hint_y is None and self.size_hint_x is not None:
            self.height = fs * fmn
        elif self.size_hint_x is None and self.size_hint_y is not None:
            self.width = self.texture_size[0]
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0, 1, 0, 0.25)
            Rectangle(pos=self.pos, size=self.size)
            

class MyLabelBlue(Label):
    def __init__(self, mfs = None, **kwargs):
        super(MyLabelBlue, self).__init__(**kwargs)
        self.text_size = self.size
        self.bind(size=self.on_size)
    def on_size(self, widget, size):
        self.text_size =(size[0], None)
        self.texture_update()
        if self.size_hint_y is None and self.size_hint_x is not None:
            self.height = fs * fmn
        elif self.size_hint_x is None and self.size_hint_y is not None:
            self.width = self.texture_size[0]
        self.toNormal()
    def toNormal(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0, 0, 1, 0.25)
            Rectangle(pos=self.pos, size=self.size)


class MyButton(Button):
    global fs
    def __init__(self, **kwargs):
        super(MyButton, self).__init__(**kwargs)
        self.bind(size=self.setter('text_size'))
        if 'halign' not in kwargs:
            self.halign = 'center'
        if 'valign' not in kwargs:
            self.valign = 'middle'
        if 'font_size' not in kwargs:
            self.font_size = fs
        if 'size_hint' not in kwargs:
            self.size_hint = (1, None)



class DDTECU():
    elm = None
    screen = None
    cecu = None
    ecufname = '' 
    requests = {}
    datas = {}
    req4data = {}
    cmd4data = {}
    req4sent = {}
    langmap = {}
    defaultEndian = 'Big'
    sentRequests = []
    BaudRate = '500000'
    Multipoint = '1'
    
    def __init__(self, cecu):
    
        global eculist
        self.elm = 0
        self.cecu = cecu
        self.ecufname = '' 
        self.requests = {}
        self.datas = {}
        self.req4data = {}
        self.cmd4data = {}
        self.req4sent = {}
        self.langmap = {}
        self.BaudRate = '500000'
        self.Multipoint = '1'
    
    def __del__(self):
        try:
            del(self.elm)
            del(self.cecu)
            del(self.ecufname)
            del(self.requests)
            del(self.datas)
            del(self.req4data)
            del(self.cmd4data)
            del(self.req4sent)
            del(self.langmap)
            del(self.BaudRate)
            del(self.Multipoint)
        except:
            pass
    
    def setELM(self, elm):
        self.elm = elm

    def translate(self, data):
        
        if data in self.datas.keys():
            d = self.datas[data]
        else:
            return data        

        if data in self.req4data.keys() and self.req4data[data] in self.requests.keys():
            r = self.requests[self.req4data[data]]
        else: return data
        
        sentBytes = r.SentBytes
        startByte = r.ReceivedDI[data].FirstByte
        startBit = r.ReceivedDI[data].BitOffset
        bitLength = d.BitsCount
        
        if bitLength%8:
            startBit = 7-startBit
            if r.ReceivedDI[data].Endian=="Big":
                startBit = 7 - startBit
        else:
            startBit = 0
        
        key = "%s:%s:%s:%s"%(sentBytes,str(startByte), str(startBit), str(bitLength))
        
        if key in self.langmap.keys():
            return self.langmap[key]
        else:
            return data

    def loadXml(self, xmlfile = ''):
        if len(xmlfile):
            self.ecufname = xmlfile
        
        if not mod_db_manager.file_in_ddt(self.ecufname):
            return
        
        tree = mod_db_manager.get_file_from_ddt(self.ecufname)
        root = et.parse(tree).getroot()
        cans = root.findall('ns0:Target/ns0:CAN', mod_globals.ns)
        if cans:
            for can in cans:
                self.BaudRate = can.attrib["BaudRate"]
                self.Multipoint = can.attrib["Multipoint"]
        rq_class = decu_requests(self.requests, root)
        dt_class = decu_datas(self.datas, root)
        
        for r in self.requests.values():
            self.req4sent[r.SentBytes] = r.Name
            for di in r.ReceivedDI.values():
                if di.Ref or di.Name not in self.req4data.keys():
                    self.req4data[di.Name] = r.Name
            for di in r.SentDI.values():
                if di.Name not in self.cmd4data.keys():
                    self.cmd4data[di.Name] = r.Name

    def packValues(self, requestName, iValues):
        r = self.requests[requestName]
        cmdPatt = r.SentBytes
        for sdi in r.SentDI.values():
        
            d = self.datas[sdi.Name]
            if d.Name+'_'+requestName not in iValues.keys():
                continue
            value = iValues[d.Name+'_'+requestName]['value'].strip()
            value = self.getValueFromInput(d, value)
            littleEndian = True if sdi.Endian=="Little" else False
            sb = sdi.FirstByte - 1 
            bits = d.BitsCount
            sbit = sdi.BitOffset
            bytes =(bits+sbit-1)/8 + 1
            if littleEndian:
                lshift = sbit
            else:
                lshift =((bytes+1)*8 -(bits+sbit))%8
                
            try:
                val = int(value,16)
            except:
                return 'ERROR: Wrong HEX value in parametr(%s) : "%s"' %(d.Name, value)
            val =(val&(2**bits-1))<<lshift
            value = hex(val)[2:]
            if value[-1:].upper()=='L':
                value = value[:-1]
            if len(value)%2:
                value = '0'+value

            if value.upper().startswith('0X'): value = value[2:]
            value = value.zfill(bytes*2).upper()
            if not all(c in string.hexdigits for c in value) and len(value)==bytes*2:
                return 'ERROR: Wrong value in parametr:%s(it should have %d bytes)' %(d.Name, d.BytesCount)

            base = cmdPatt[sb*2:(sb+bytes)*2]
            binbase = int(base,16)
            binvalue = int(value,16)
            mask =(2**bits-1)<<lshift
            
            binvalue = binbase ^(mask & binbase) | binvalue

            value = hex(binvalue)[2:].upper()
            if value[-1:].upper()=='L':
                value = value[:-1]
            value = value[-bytes*2:].zfill(bytes*2)

            cmdPatt = cmdPatt[0:sb*2] + value + cmdPatt[(sb+bytes)*2:]

        return cmdPatt

    def getValueFromInput(self, d, value):
        if value == 'Enter here':
            return 'ERROR: Wrong value in parametr:%s(it should have %d bytes), be decimal or starts with 0x for hex' %(
                    d.Name, d.BytesCount)
        if len(d.List.keys()) and ':' in value:
            value = value.split(':')[0]

        if d.Scaled:
            if ' ' in value:
                value = value.split(' ')[0]
            if value.upper().startswith('0X'):
                value = value[2:]
            else:
                if not all((c in string.digits or c == '.' or c == ',' or c == '-' or c == 'e' or c == 'E') for c in value):
                    return 'ERROR: Wrong value in parametr:%s(it should have %d bytes), be decimal or starts with 0x for hex' %(
                    d.Name, d.BytesCount)
                flv =(float(value) * float(d.DivideBy) - float(d.Offset)) / float(d.Step)
                value = hex(int(flv))
        if d.BytesASCII:
            hst = ''
            if len(value)<(d.BitsCount/8):
                value += ' '*(d.BitsCount/8 - len(value))
            for c in value:
                hst = hst + hex(ord(c))[2:].zfill(2)
            value = hst
        return value

    def elmRequest(self, req, delay='0', positive='', cache=True):
        if req.startswith('10'):
            self.elm.startSession = req
            
        if type(delay) is str:
            delay = int(delay)
            
        if delay>0 and delay<1000: delay = 1000

        rsp = self.elm.request(req, positive, cache , serviceDelay=delay)

        #if self.screen != None and(not cache or req not in self.sentRequests):
            #tmstr = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        if cache and req not in self.sentRequests:
            self.sentRequests.append(req)

        return rsp

    def loadDump(self, dumpname=''):
        global ecudump
        
        ecudump = {}
        
        xmlname = self.ecufname.split('/')[-1]
        if xmlname.upper().endswith('.XML'):
            xmlname = xmlname[:-4]

        if len(dumpname)==0 or not os.path.exists(dumpname):
            flist = []
         
            for root, dirs, files in os.walk(mod_globals.dumps_dir):
                for f in files:
                    if(xmlname+'.') in f:
                        flist.append(f)
                        
            if len(flist)==0: return
            flist.sort()
            dumpname = os.path.join(mod_globals.dumps_dir, flist[-1])

        mod_globals.dumpName = dumpname
        df = open(dumpname,'rt')
        lines = df.readlines()
        df.close()
        
        for l in lines:
            l = l.strip().replace('\n','')
            if l.count(':')==1:
                req,rsp = l.split(':')
                ecudump[req] = rsp
        
        self.elm.setDump(ecudump)
        
    def clearELMcache(self):
        self.elm.clear_cache()
        self.sentRequests = []
