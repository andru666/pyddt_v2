#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os, ast, time, pickle, copy, string
from shutil import copyfile
from datetime import datetime
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
fmn = 1.3
from mod_elm import *
import mod_globals, mod_ddt_utils, mod_db_manager, mod_scan_ecus, mod_ddt_ecu

os.chdir(os.path.dirname(os.path.realpath(sys.argv[0])))

fs = mod_globals.fontSize
class MyScatterLayout(ScatterLayout):
    def __init__(self, **kwargs):
        if 'bgcolor' in kwargs:
            self.bgcolor = kwargs['bgcolor']
            del kwargs ['bgcolor']
        else:
            self.bgcolor =(0, 0, 0, 0)
        super(MyScatterLayout, self).__init__(**kwargs)
        with self.canvas.before:
            Color(self.bgcolor[0], self.bgcolor[1], self.bgcolor[2], self.bgcolor[3])
            Rectangle(pos=self.pos, size=self.size)

class DDTLauncher(App):
    
    def __init__(self, opt_car=None, elm=None):
        global LANG
        if mod_globals.opt_lang == 'ru':
            import lang_ru as LANG
        elif mod_globals.opt_lang == 'en':
            import lang_en as LANG
        else:
            import lang_fr as LANG
        self.eculist = mod_ddt_utils.loadECUlist()
        self.Window_size = mod_globals.windows_size
        self.filterText = opt_car
        global fs
        fs = mod_globals.fontSize
        self.carecus = []
        self.v_dumpList = []
        self.dv_addr = []
        self.ecutree = {}
        self.elm = elm
        self.clock_event = None
        self.scf = 10.0
        if True:
            self.v_proj = self.filterText.split(':')[0].strip()
        else:
            self.v_proj = 'ALL_CARS'
        if self.v_proj == LANG.b_all_cars:
            self.v_proj = 'ALL_CARS'
            self.filterText = 'ALL_CARS'
        self.labels = TextInput(text=self.v_proj, size_hint=(0.6, None), padding=[0, fs/1.5], font_size=fs, height=3*fs)
        self.roll_back = False
        self.v_addr = ''
        self.Roll_back = ''
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
        if mod_globals.savedCAR != LANG.b_select:
            self.LoadCarFile(mod_globals.savedCAR)
        else:
            self.CarDoubleClick()
        if mod_globals.opt_scan:
            self.ScanAllBtnClick()
        super(DDTLauncher, self).__init__()

    def build(self):
        p = len(self.carecus)
        if not mod_globals.opt_demo: height_g = fs*5.07*len([v for v in range(len(self.carecus)) if self.carecus[v]['xml']])
        else: height_g = fs*5.07*(p)
        if height_g == 0: height_g = 200
        self.Layout = GridLayout(cols=1, spacing=3, size_hint=(1, None), height=self.Window_size[1])
        self.Layout.add_widget(self.make_savedECU())
        self.startStopButton = Button(text='', size_hint=(1, 1))
        box = GridLayout(cols=4, spacing=5, size_hint=(1, None), height=height_g)
        box111 = GridLayout(cols=4, spacing=5, size_hint=(1, None), height=fs*3)
        cols = ['addr', 'prot', 'name', 'xml', 'dump']
        Cols = dict(addr=['Addr', (1,0,0,1)], prot=[LANG.l_prot, (1,0,0,1)], name=[LANG.l_name, (1,0,0,1)], xml=['XML', (1,0,0,1)], dump=[LANG.l_dump, (1,0,0,1)])
        list_name = self.addr.list_name[LANG.lang]
        for key in cols:
            if key == 'addr':
                continue
            elif key == 'name':
                box1 = BoxLayout(orientation='vertical', spacing=1, size_hint=(0.5, 1))
                box11 = BoxLayout(orientation='vertical', spacing=1, size_hint=(0.5, 1))
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
            for v in sorted(self.carecus, key=lambda k: k['xml'], reverse=True):
                if v['xml'] == '' and not mod_globals.opt_demo: continue
                if key == 'addr':
                    continue
                elif key == 'name':
                    if v[key] in LANG.list_ru.keys():
                        name = LANG.list_ru[v[key]]
                    elif v[key] in list_name.keys():
                        name = list_name[v[key]]
                    elif v[key] in LANG.list_name.keys():
                        name = LANG.list_name[v[key]]
                    else:
                        name = v[key]
                    self.but_xml = MyButton(text=name, id=v['addr'], size_hint=(1, None), on_press=self.popup_xml, height=fs*5, font_size=fs*0.8)
                    self.label[v['addr']] = self.but_xml
                    box1.add_widget(self.but_xml)
                elif key == 'dump':
                    self.but_dump = MyButton(text=v[key], id=v['addr']+'_dump', size_hint=(1, None), font_size=fs, height=fs*5, on_release=self.popup_dump)
                    self.label[v['addr']+'_dump'] = self.but_dump
                    box1.add_widget(self.but_dump)
                elif key == 'xml':
                    self.but_xml = MyButton(text=v[key], id=v['addr']+'_xml', size_hint=(1, None), font_size=fs, height=fs*5, on_release=self.openECUS)
                    if v[key].startswith('not_ident'):
                        self.but_xml.text = LANG.not_ident
                    self.label[v['addr']+'_xml'] = self.but_xml
                    box1.add_widget(self.but_xml)
                else:
                    self.label_prot = MyLabel(text=v['prot'], font_size=fs/1.3, id=v['addr']+'_prot', size_hint=(1, None), height=fs*5, bgcolor=(0.8,0,0,0.8))
                    self.label[v['addr']+'_prot'] = self.label_prot
                    box1.add_widget(self.label_prot)
            box111.add_widget(box11)
            box.add_widget(box1)
        root = ScrollView(size_hint=(1, None), height=self.Window_size[1]-(fs*10))
        root.add_widget(box)
        self.Layout.add_widget(box111)
        self.Layout.add_widget(root)
        quitbutton = MyButton(text=LANG.b_quit, size_hint=(1, None), height=fs*4, on_release=self.EXIT)
        self.Layout.add_widget(quitbutton)
        return self.Layout

    def popup_xml(self, inst):
        lbltxt = Label(text=LANG.l_cont10)
        popup_init = Popup(title=LANG.l_load, title_size=fs*1.5, title_align='center', content=lbltxt, size_hint=(1, 1))
        popup_init.open()
        EventLoop.idle()
        sys.stdout.flush()
        self.dv_addr = inst.id
        layout = GridLayout(cols=1, spacing=5, size_hint=(1, None))
        layout.bind(minimum_height=layout.setter('height'))
        layout.add_widget(MyButton(text=LANG.b_clear1, size_hint=(1, None), id=inst.id, height=fs*4, on_press=lambda i,k='',v='': self.select_xml(i,k,v)))
        for k, v in sorted(self.addr.alist[inst.id]['xml'].items()):
            btn = MyButton(text=k, size_hint=(1, None), id=inst.id, height=fs*4, on_press=lambda i,k=k,v=v: self.select_xml(i,k,v))
            layout.add_widget(btn)
        btn_close = MyButton(text=LANG.b_close, size_hint=(1, None), height=fs*4)
        layout.add_widget(btn_close)
        self.root_xml = ScrollView(size_hint=(1, 1))
        self.root_xml.add_widget(layout)
        popup_init.dismiss()
        self.popup = Popup(title=LANG.l_title4+'\n'+inst.text, title_size=fs*1.5, title_align='center', content=self.root_xml, size_hint=(None, None), size=(self.Window_size[0], self.Window_size[1]*0.9))
        self.popup.open()        
        btn_close.bind(on_press=self.popup.dismiss)

    def EXIT(self, dt):
        exit()

    def openECUS(self, bt):
        self.Addr = bt.id
        self.xml = bt.text
        if self.xml == LANG.not_ident:
            self.not_ecu()
            return
        self.lbltxt = Label(text=LANG.l_op_scr)
        popup_init = Popup(title=LANG.l_load, content=self.lbltxt, size=(self.Window_size[0]*0.7, 400), size_hint=(None, None))
        popup_init.open()
        EventLoop.idle()
        ecu = self.getSelectedECU(self.xml)
        if ecu==None or ecu['xml']=='':
            self.MyPopup(content=LANG.l_cont1, stop=self.stop)
            return None
        self.OpenECUScreens(ecu)
        EventLoop.window.remove_widget(popup_init)
        popup_init.dismiss()

    def not_ecu(self):
        not_ident, DiagVersion, Supplier, Soft, Version = [i['xml'] for i in self.carecus if i['addr'] == self.Addr[:-4]][0].split('#')
        mod_ddt_ecu.ecuIdent(self.Addr[:-4], DiagVersion, Supplier, Soft, Version, self.eculist)

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
            self.MyPopup(title=LANG.error, content=LANG.l_cont2, stop=self.stop)
            return
        self.setEcuAddress(ce)
        self.elm.start_session(ce['ses'])
        decucashfile = os.path.join(mod_globals.cache_dir, ce['xml'][:-4] + ".p")
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
                self.lbltxt = Label(text=LANG.l_text1)
                popup_init = Popup(title=LANG.l_load, content=self.lbltxt, size=(self.Window_size[0]*0.7, 400), size_hint=(None, None))
                popup_init.open()
                EventLoop.idle()
                self.decu.loadDump()
                popup_init.dismiss()
            else:
                self.lbltxt = Label(text=LANG.l_text1)
                popup_init = Popup(title=LANG.l_load, content=self.lbltxt, size=(400, 400), size_hint=(None, None))
                popup_init.open()
                self.decu.loadDump(os.path.join(mod_globals.dumps_dir, ce['dump']))
                popup_init.dismiss()
        elif mod_globals.opt_dump:
            self.lbltxt = Label(text=LANG.l_text2)
            popup_init = Popup(title=LANG.l_load, content=self.lbltxt, size=(400, 400), size_hint=(None, None))
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
        box = GridLayout(cols=1, spacing=3, size_hint=(1, None), height=fs*4*(len(data) + 4))
        self.Layout.clear_widgets()
        if isinstance(data, dict): datas = sorted(data.keys())
        else: datas = data
        if LANG.b_read_dtc in data:
            button = MyButton(text=LANG.b_read_dtc, id=LANG.b_read_dtc, size_hint=(1, None), height=fs*4, on_release=lambda x=xml:self.res_show_screen(x,data))
            box.add_widget(button)
        for x in datas:
            if x == 'ddt_all_commands': continue
            if x == 'AIRBAG Reset': continue
            if x == LANG.l_text9: continue
            if x == LANG.b_read_dtc: continue
            button = MyButton(text=x.replace('ddt_all_commands', ''), id=x, size_hint=(1, None), height=fs*4, on_release=lambda x=xml:self.res_show_screen(x,data))
            box.add_widget(button)
        if 'ddt_all_commands' in data:
            button = MyButton(text='ddt_all_commands', id='ddt_all_commands', size_hint=(1, None), height=fs*4, on_release=lambda x=xml:self.res_show_screen(x,data))
            box.add_widget(button)
        if LANG.l_text9 in data:
            button = MyButton(text=LANG.l_text9, id=LANG.l_text9, size_hint=(1, None), height=fs*4, on_release=lambda x=xml:self.res_show_screen(x,data))
            box.add_widget(button)
        if 'AIRBAG Reset' in data:
            button = MyButton(text='AIRBAG Reset', id='AIRBAG Reset', size_hint=(1, None), height=fs*4, on_release=lambda x=xml:self.res_show_screen(x,data))
            box.add_widget(button)
        quitbutton = MyButton(text=LANG.b_back, id=LANG.b_back, size_hint=(1, None), height=fs*4)
        if isinstance(data, list):
            if len(data) == 0:
                self.MyPopup(content=LANG.l_cont13)
            quitbutton.bind(on_release=lambda x=xml:self.res_show_screen(x,self.screens))
        else:
            quitbutton.bind(on_release=self.stop)
        roots = ScrollView(size_hint=(1, None), height=self.Window_size[1]-fs*4)
        roots.add_widget(box)
        self.Layout.add_widget(roots)
        self.Layout.add_widget(quitbutton)

    def res_show_screen(self, xx, data=None):
        x = xx.id
        if x == LANG.l_text9: self.select_dump_RollBack(xx.id)
        elif x == 'AIRBAG Reset': self.airbag_reset()
        elif x == (LANG.b_read_dtc): self.readDTC()
        elif x == (LANG.b_back): self.show_screen(x,data)
        elif isinstance(data, dict): self.show_screen(x,data[x])
        elif isinstance(data, list): self.loadScreen(x, data)

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
            self.startStopButton.text = LANG.b_start
            self.clock_event = ''
        else:
            self.start = True
            self.startStopButton.text = LANG.b_stop

    def update_values(self, dt):
        if not self.start:
            return
        self.decu.elm.clear_cache()
        self.elm.clear_cache()
        if True:
            params = self.get_ecu_values()
        else:
            return
        for key, v in params.items():
            val = v['value']
            d = self.decu.datas[self.dValue[key]['name']]
            if val != 'None':
                if key in self.dLabels.keys():
                    if len(d.List.keys()):
                        listIndex = int(val,16)
                        if listIndex in d.List.keys():
                            if len(self.dLabels[key]) ==1: self.dLabels[key][0].text =  d.List[listIndex]
                            else:
                                for iD in self.dLabels[key]:
                                    iD.text =  d.List[listIndex]
                        else:
                            if len(self.dLabels[key]) ==1: self.dLabels[key][0].text =  val
                            else:
                                for iD in self.dLabels[key]:
                                    iD.text = val
                    elif d.Scaled:
                        if len(self.dLabels[key]) ==1: self.dLabels[key][0].text = val+' '+d.Unit
                        else:
                            for iD in self.dLabels[key]:
                                iD.text = val+' '+d.Unit
                    else:
                        if len(self.dLabels[key]) ==1: self.dLabels[key][0].text = val
                        else:
                            for iD in self.dLabels[key]:
                                iD.text = val
                else:
                    if key in self.dLabels.keys():
                        if len(self.dLabels[key]) == 1:
                            self.dLabels[key][0].text = val
                        else:
                            for iD in self.dLabels[key]:
                                iD.text = val
                if key in self.iLabels.keys():
                    if self.iValueNeedUpdate[key]:
                        self.iLabels[key].text = val
                        self.iValueNeedUpdate[key] = False
                if key+v['request'] in self.oLabels.keys():
                    if self.iValueNeedUpdate[key]:
                        if listIndex:
                            self.oLabels[key+v['request']].text = hex(listIndex)[2:]+':'+d.List[listIndex]
                        else:
                            self.oLabels[key+v['request']].text = val
                        self.iValueNeedUpdate[key] = False
                if key in self.Labels.keys():
                    self.Labels[key].text = val
        if self.start:
            self.clock_event = Clock.schedule_once(self.update_values, 0.02)

    def get_ecu_values(self):
        dct = {}
        if len(self.dValue):
            for d in self.dValue.keys():
                if self.dValue[d]['request'] not in self.REQ: continue
                EventLoop.window.mainloop()
                val = get_value(self.dValue[d], self.decu, self.elm)
                if ':' in val['value']:
                    val['value'] = val['value'].split(':')[1]
                if val['value'].isalnum() and len(val['value'])>30 and 'vin'.upper() in d.upper():
                    val['value'] = bytes.fromhex(val['value'])
                    while not val['value'].isalnum():
                        val['value'] = val['value'][:-1]
                        if len(val['value'])==0:break
                    val['value'] = val['value'].decode()
                self.dValue[d]['value'] = val['value'].strip()
                dct[d] = self.dValue[d]
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
    
    def loadScreen(self, scr, data):
        self.Layout.clear_widgets()
        self.start = True
        self.startStopButton = MyButton(text='', size_hint=(1, 1))
        if self.start:
            self.startStopButton.text = LANG.b_stop
        else:
            self.startStopButton.text = LANG.b_start
        self.currentscreen = scr
        if scr in self.Screens.keys():
            scr = self.Screens[scr]
        if type(scr) is str or type(scr) is str:
            self.loadSyntheticScreen(scr)
            return
        scr_w = int(scr.attrib["Width"])
        scr_h = int(scr.attrib["Height"])
        self.scr_c = int(scr.attrib["Color"])
        if scr_w *2 <= self.Window_size[0]: self.scf = 1
        self.size_screen = (scr_w / self.scf, scr_h / self.scf)
        self.out = False
        self.DValue = []
        self.IValue = []
        self.LValue = []
        self.BValue = []
        self.SValue = {}

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
        
        labe = False
        
        box1 = GridLayout(cols=3, size_hint=(1, None), height=fs*3)
        box2 = GridLayout(cols=1, spacing=5, padding=5)
        box1.add_widget(self.startStopButton)
        box1.add_widget(MyButton(text=LANG.b_close, size_hint=(1, 1), on_release=lambda x:self.show_screen(self.xml, data)))
        box1.add_widget(MyButton(text=LANG.b_change_view, size_hint=(1, 1), on_release=self.change_screen))
        self.Layout.add_widget(box1)
        self.startStopButton.bind(on_release=lambda args:self.startStop())
        if scr_w > scr_h:
            src = (scr_w*1.0 / scr_h)
        else:
            src = (scr_h*1.0 / scr_w)
        while src > 1.3: src = src / 1.1
        while src < 1.3: src = src * 1.1
        labels = ecu_labels(self.LValue, scr)
        dispalys = ecu_dispalys(self.DValue, scr, self.decu)
        buttons = ecu_buttons(self.BValue, self.dBtnSend, scr)
        inputs = ecu_inputs(self.IValue, scr)
        sends = ecu_sends(self.sReq_lst, scr)
        max_y = fs*3*(len(self.DValue)+len(self.IValue))
        if self.make_box:
            self.BOX2 = []
            box2.size_hint = (1, None)
            box2.height = 0
            self.Layout.add_widget(MyLabel(text=self.currentscreen, color=(0,0,0,1), bgcolor=self.hex_to_rgb(self.scr_c)))
            if len(self.BValue):
                for b in self.BValue:
                    self.bValue[eval(b[12])[0]['RequestName']] = {'send':b[12], 'xText':b[0]}
            if len(self.DValue) > 0:
                for d in self.DValue:
                    xText, xReq, xColor, xWidth, xrLeft, xrTop, xrHeight, xrWidth, xfName, xfSize, xfBold, xfItalic, xfColor, xAlignment, halign = d
                    if xText in self.decu.req4data.keys() and self.decu.req4data[xText] in self.decu.requests.keys():
                        self.dReq[self.decu.req4data[xText]] = self.decu.requests[self.decu.req4data[xText]].ManuelSend
                    if xText not in self.dValue.keys():
                        self.dValue[xText] = {'value':mod_globals.none_val, 'name':xText, 'request':xReq}
                    box2.height = box2.height + fs*3
                    if math.ceil((len(xText)*2.0)/(box2.width/2.0)) > 1:
                        box2.height = box2.height + fs
                    if math.ceil((len(xText)*2.0)/(box2.width/2.0)) > 2:
                        box2.height = box2.height + fs
                    box2.add_widget(self.make_box_params(xText, xReq))
            if len(self.IValue) > 0:
                for i in self.IValue:
                    i, xReq, xColor, xWidth, xrLeft, xrTop, xrHeight, xrWidth, xfName, xfSize, xfBold, xfItalic, xfColor, xAlignment, halign = i
                    if i not in self.iValue.keys():
                        box2.height = box2.height + fs
                        if i not in self.dValue.keys():
                            self.dValue[i] = {'value':mod_globals.none_val, 'name':i, 'request':xReq}
                        if i in self.decu.req4data.keys() and self.decu.req4data[i] in self.decu.requests.keys():
                            self.dReq[self.decu.req4data[i]] = self.decu.requests[self.decu.req4data[i]].ManuelSend
                        self.iValue[i] = {'value':'', 'name':i, 'request':xReq}
                        self.iValueNeedUpdate[i] = True
                    if i in self.decu.datas.keys() and len(self.decu.datas[i].List.keys()):
                        box2.height = box2.height + fs
                        optionList = []
                        if i not in self.iValue.keys():
                            self.iValue[i] = {'value':'', 'name':i, 'request':xReq}
                            self.iValueNeedUpdate[i] = True
                        for ii in self.decu.datas[i].List.keys():
                            optionList.append(hex(int(ii)).replace("0x", "").upper() + ':' + self.decu.datas[i].List[ii])
                        self.ListOption[i] = optionList
                        self.iValue[i] = {'value':optionList[0], 'name':i, 'request':xReq}
                    else:
                        box2.height = box2.height + fs
                        self.iValue[i] = {'value':LANG.l_enter_here, 'name':i, 'request':xReq}
                    box2.add_widget(self.make_box_params(i, xReq))
                    box2.height = box2.height + fs*3
                    if math.ceil((len(i)*3.0)/(box2.width/3.0)) > 1:
                        box2.height = box2.height + fs
                    if math.ceil((len(i)*3.0)/(box2.width/3.0)) > 2:
                        box2.height = box2.height + fs
            if len(self.BValue):
                dv = []
                for d in self.dValue.values():
                    dv.append(d['request'])
                for b in self.BValue:
                    xText = b[0]
                    button = MyButton(text=xText, size_hint=(1, 1), id=b[12], on_release = lambda btn=xText, key=b[12]: self.buttonPressed(btn.text, btn.id))
                    if len(self.BValue) == 1:
                        box2.height = box2.height + fs*3
                        box2.add_widget(button)
                    else:
                        if eval(b[12])[0]['RequestName'] not in dv:
                            box2.height = box2.height + fs*3
                            box2.add_widget(button)
            root = ScrollView(size_hint=(1, None), height=self.Window_size[1]-fs*5)
            root.add_widget(box2)
            self.Layout.add_widget(root)
        else:
            box2.size=(self.Window_size[0], self.Window_size[1]-fs*3)
            box2.size_hint=(None, None)
            self.flayout = MyScatterLayout(size_hint=(None, None), bgcolor=self.hex_to_rgb(self.scr_c), size=self.size_screen, do_rotation=False)
            if len(self.LValue) > 0:
                for l in sorted(self.LValue, key=lambda k: k['sq'], reverse=True):
                    xText, xColor, xrLeft, xrTop, xrHeight, xrWidth, xfName, xfSize, xfBold, xfItalic, xfColor, xAlignment, halign = l['values']
                    if not xText or int(l['sq']) > (scr_w * scr_h)/3:
                        labe = True
                    self.flayout.add_widget(MyLabel_scr(text=xText, id=xText, halign=halign, color=self.hex_to_rgb(xfColor), bold=xfBold, italic=xfItalic, font_size=xfSize*src, valign=xAlignment, bgcolor=self.hex_to_rgb(xColor),  size_hint=(None, None), size=(xrWidth/self.scf, xrHeight/self.scf), pos=(xrLeft/self.scf, self.size_screen[1]-(xrHeight+xrTop)/self.scf)))
            if len(self.DValue) > 0:
                for d in self.DValue:
                    xText, xReq, xColor, xWidth, xrLeft, xrTop, xrHeight, xrWidth, xfName, xfSize, xfBold, xfItalic, xfColor, xAlignment, halign = d
                    self.dReq[xReq] = self.decu.requests[xReq].ManuelSend
                    if xText not in self.dValue.keys():
                        self.dValue[xText] = {'value':mod_globals.none_val, 'name':xText, 'request':xReq}
                    if xWidth/self.scf < (xfSize*len(xText)) and xfSize*src > xrHeight/self.scf/2:
                        xSize = xrHeight/self.scf/src/2.5
                    else:
                        xSize = xfSize
                    if xWidth/self.scf > 40:
                        label = MyLabel_scr(text=xText, id=xText+'_'+xReq, valign=xAlignment, color=self.hex_to_rgb(xfColor), bold=xfBold, italic=xfItalic, font_size=xSize*src, halign='left', bgcolor=self.hex_to_rgb(xColor), size_hint=(None, None), size=(xWidth/self.scf, xrHeight/self.scf), pos=(xrLeft/self.scf, self.size_screen[1]-(xrTop+xrHeight)/self.scf))
                        self.flayout.add_widget(label)
                    if not labe and self.hex_to_rgb(self.scr_c) == self.hex_to_rgb(xColor):
                        xColor = int(xColor)/2
                    if xText not in self.dLabels.keys(): self.dLabels[xText] = []
                    label_D = MyLabel_scr(text=self.dValue[xText]['value'], id=xText+'_'+xReq, valign=xAlignment, bgcolor=self.hex_to_rgb(xColor), color=self.hex_to_rgb(xfColor), bold=xfBold, italic=xfItalic, font_size=xfSize*src, size_hint=(None, None), size=((xrWidth - xWidth)/self.scf, xrHeight/self.scf), pos=((xrLeft + xWidth)/self.scf, self.size_screen[1]-(xrTop+xrHeight)/self.scf))
                    self.dLabels[xText].append(label_D)
                    self.flayout.add_widget(label_D)
            if len(self.BValue) > 0:
                for b in self.BValue:
                    xText, xrLeft, xrTop, xrHeight, xrWidth, xfName, xfSize, xfBold, xfItalic, xfColor, xAlignment, halign, b = b
                    button = MyButton(text=xText, text_size=(xrWidth/self.scf, xrHeight/self.scf), valign='middle', id=b, color=self.hex_to_rgb(xfColor), bold=xfBold, halign=halign, italic=xfItalic, font_size=xfSize*src, size_hint=(None, None), size=(xrWidth/self.scf, xrHeight/self.scf), pos=(xrLeft/self.scf, self.size_screen[1]-(xrTop+xrHeight)/self.scf))
                    button.bind(on_release = lambda btn=xText, key=b: self.buttonPressed(btn.text, btn.id))
                    self.flayout.add_widget(button)
            
            if len(self.IValue) > 0:
                for i in self.IValue:
                    i, xReq, xColor, xWidth, xrLeft, xrTop, xrHeight, xrWidth, xfName, xfSize, xfBold, xfItalic, xfColor, xAlignment, halign = i
                    if xWidth/self.scf > 40:
                        label = MyLabel_scr(text=i, id=i, valign=xAlignment, color=self.hex_to_rgb(xfColor), bold=xfBold, italic=xfItalic, halign='left', font_size=xfSize*src, bgcolor=self.hex_to_rgb(xColor), size_hint=(None, None), size=(xWidth/self.scf, xrHeight/self.scf), pos=(xrLeft/self.scf, self.size_screen[1]-(xrTop+xrHeight)/self.scf))
                        self.flayout.add_widget(label)
                    if i+xReq not in self.iValue.keys():
                        if i not in self.dValue.keys():
                            self.dValue[i] = {'value':mod_globals.none_val, 'name':i, 'request':xReq}
                        if i in self.decu.req4data.keys() and self.decu.req4data[i] in self.decu.requests.keys():
                            self.dReq[self.decu.req4data[i]] = self.decu.requests[self.decu.req4data[i]].ManuelSend
                        self.iValue[i+xReq] = {'value':'', 'name':i, 'request':xReq}
                        self.iValueNeedUpdate[i] = True
                    if i in self.decu.datas.keys() and len(self.decu.datas[i].List.keys()):
                        optionList = []
                        if i+xReq not in self.iValue.keys():
                            self.iValue[i+xReq] = {'value':'', 'name':i, 'request':xReq}
                            self.iValueNeedUpdate[i] = True
                        for ii in self.decu.datas[i].List.keys():
                            optionList.append(
                                hex(int(ii)).replace("0x", "").upper() + ':' + self.decu.datas[i].List[ii])
                        self.iValue[i+xReq] = {'value':optionList[0], 'name':i, 'request':xReq}
                        self.dropdowns[i+xReq] = DropDown(auto_width=False, width=xrWidth)
                        for o in optionList:
                            btn = MyButton(text=o, id=o, font_size=xfSize*src*self.flayout.scale, size_hint_y=None, height=xrHeight)
                            btn.bind(on_release=lambda btn=btn, i=i+xReq: self.select_option(btn.text, i))
                            self.dropdowns[i+xReq].add_widget(btn)
                        self.triggers[i+xReq] = MyButton(text=self.iValue[i+xReq]['value'], id=i+xReq, size_hint=(None, None), font_size=xfSize*src, size=((xrWidth - xWidth)/self.scf, xrHeight/self.scf), pos=((xrLeft + xWidth)/self.scf, self.size_screen[1]-(xrTop+xrHeight)/self.scf))
                        self.triggers[i+xReq].bind(on_release=lambda bt,L=optionList,f=xfSize*src,H=xrHeight/self.scf,W=(xrWidth - xWidth)/self.scf:self.drop(bt.id, L, f, H, W))
                        self.oLabels[i+xReq] = self.triggers[i+xReq]
                        self.dropdowns[i+xReq].bind(on_select=lambda instance, x: setattr(self.triggers[i+xReq], 'text', x))
                        self.flayout.add_widget(self.triggers[i+xReq])
                    else:
                        self.iValue[i+xReq] = {'value':LANG.l_enter_here, 'name':i, 'request':xReq}
                        label_IT = TextInput(text=self.iValue[i+xReq]['value'], font_size=xfSize*src, size_hint=(None, None), size=((xrWidth - xWidth)/self.scf, xrHeight/self.scf), pos=((xrLeft + xWidth)/self.scf, self.size_screen[1]-(xrTop+xrHeight)/self.scf))
                        self.iLabels[i] = label_IT
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
        rq = rq.replace('ddt_all_commands', '')
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
        max_y = fs*4*(len(self.decu.requests[rq].ReceivedDI))
        box = GridLayout(cols=1, spacing=3, size_hint=(1, None), height=fs+3)
        xText = self.decu.requests[rq].SentBytes + ' - ' + rq
        
        header = MyLabel(text=xText)
        self.Layout.add_widget(header)
        pn = 0
        for xText, zzz in sorted(self.decu.requests[rq].ReceivedDI.items(), key=lambda item: item[1].FirstByte):
            pn += 1
            if xText not in self.dValue.keys():
                self.dValue[xText] = {'value':mod_globals.none_val, 'name':xText, 'request':rq}
                if xText in self.decu.req4data.keys() and self.decu.req4data[xText] in self.decu.requests.keys():
                    self.dReq[self.decu.req4data[xText]] = self.decu.requests[self.decu.req4data[xText]].ManuelSend
            if len(wc)==0:
                box_params = self.make_box_params(xText, '')
                box.height += box_params.height
                box.add_widget(box_params)
            else:
                if xText not in self.iValue.keys():
                    if xText not in self.dValue.keys():
                        self.dValue[xText] = {'value':'', 'name':xText, 'request':rq}
                    if xText in self.decu.req4data.keys() and self.decu.req4data[xText] in self.decu.requests.keys():
                        self.dReq[self.decu.req4data[xText]] = self.decu.requests[self.decu.req4data[xText]].ManuelSend
                    self.iValue[xText] = {'value':'', 'name':xText, 'request':rq}
                    self.iValueNeedUpdate[xText] = True
                if xText in self.decu.datas.keys() and len(self.decu.datas[xText].List.keys()):
                    optionList = []
                    if xText not in self.iValue.keys():
                        self.iValue[xText] = {'value':'', 'name':xText, 'request':rq}
                        self.iValueNeedUpdate[xText] = True
                    for i in self.decu.datas[xText].List.keys():
                        optionList.append(
                            hex(int(i)).replace("0x", "").upper() + ':' + self.decu.datas[xText].List[i])
                    self.ListOption[xText] = optionList
                    self.iValue[xText] = {'value':optionList[0], 'name':xText, 'request':rq}
                else:
                    self.iValue[xText] = {'value':LANG.l_enter_here, 'name':xText, 'request':rq}
                box_params = self.make_box_params(xText, '')
                box.height += box_params.height
                box.add_widget(box_params)
        if len(wc) > 0:
            slist = []
            smap = {}
            smap['Delay'] = 1000
            smap['RequestName'] = wc
            slist.append(smap)
            self.dBtnSend[str(slist)] = slist
            box.height = box.height + fs*3.0
            box.add_widget(MyButton(text=LANG.b_write, size_hint=(1, None), id=xText, height=fs*3, on_release = lambda btn,key=str(slist): self.buttonPressed(btn, key)))
        root = ScrollView(size_hint=(1, 1))
        root.add_widget(box)
        self.Layout.add_widget(root)
        self.decu.clearELMcache()
        self.update_dInputs()
        self.sReq_lst.append(rq)
        if self.sReq_lst:
            self.startScreen(self.sReq_lst)
        if self.dReq:
            self.startScreen(self.dReq)
        self.Layout.add_widget(MyButton(text=LANG.b_close, size_hint=(1, None), height=fs*3, on_release=lambda x:self.show_screen(self.xml, self.screens)))
        if self.start:
            self.clock_event = Clock.schedule_once(self.update_values, 0.02)

    def airbag_reset(self):
        print(self.decu.requests.keys())
        if "Reset crash ou accès au mode fournisseur" in self.decu.requests.keys():
            requests = self.decu.requests["Reset crash ou accès au mode fournisseur"]
        elif "Reset Crash" in self.decu.requests.keys():
            requests = self.decu.requests["Reset Crash"]
        else:
            print('not Reset crash ou accès au mode fournisseur')
            self.MyPopup(content=LANG.l_cont3)
            return False
        print(requests)
        

    def readDTC(self):
        if "ReadDTCInformation.ReportDTC" in self.decu.requests.keys():
            requests = self.decu.requests["ReadDTCInformation.ReportDTC"]
        elif "ReadDTC" in self.decu.requests.keys():
            requests = self.decu.requests["ReadDTC"]
        else:
            self.MyPopup(content=LANG.l_cont3)
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
        if "RESPONSE" in can_response or "DATA" in can_response or 'None' in str(can_response) or 'INIT' in can_response or not can_response:
            self.MyPopup(content=LANG.l_cont4)
            return
        can_response = can_response.rstrip().split(' ')
        if can_response[0].upper() == "7F":
            self.MyPopup(content=LANG.l_cont5)
            return
        if len(can_response) <= 2:
            self.MyPopup(content=LANG.l_cont6)
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
        self.Layout.add_widget(MyLabel(text=LANG.l_title6, height=fs*3, bgcolor=(0.8,0,0,1), markup=True))
        root = ScrollView(size_hint=(1, None), height=self.Window_size[1]-fs*9)
        self.data_dtc = {}
        tree = mod_db_manager.get_file_from_ddt(self.decu.ecufname)
        xdoc = et.parse(tree).getroot()
        ns = {'ns0': 'http://www-diag.renault.com/2002/ECU', 'ns1': 'http://www-diag.renault.com/2002/screens'}
        devices = xdoc.findall('ns0:Target/ns0:Devices', ns)
        if devices:
            for device in devices[0]:
                if 'DTC' in device.attrib:
                    self.data_dtc[hex(int(device.attrib['DTC'])).replace("0x", "").upper()] = {}
                    if 'FreezeFrame' in device.attrib:
                        self.data_dtc[hex(int(device.attrib['DTC'])).replace("0x", "").upper()]['FreezeFrame'] = device.attrib['FreezeFrame']
                    self.data_dtc[hex(int(device.attrib['DTC'])).replace("0x", "").upper()]['name'] = device.attrib['Name']
        box = GridLayout(cols=1, size_hint=(1, None), height=fs)
        for dn in range(0, numberofdtc):
            DTC = ''.join(can_response[2:4])
            ln = MyButton(text='[b]DTC #%i' % dn + '[/b] ' + DTC, id=DTC, bgcolor=(0,0.5,0,1), markup=True)
            if DTC in self.data_dtc.keys():
                self.data_dtc[DTC]['resp'] = ' '.join(can_response)
                self.data_dtc[DTC]['requests'] = requests
                ln.bind(on_press=self.show_DTC)
                ln.text += ' : ' + self.data_dtc[DTC]['name']
            box.add_widget(MyLabel(text='', height=fs*0.4, bgcolor=(0,0,0.2,1)))
            box.add_widget(ln)
            box.height = box.height + ln.height + fs*0.4
            can_response = can_response[shiftbytecount:]
        root.add_widget(box)
        self.Layout.add_widget(root)
        self.Layout.add_widget(MyButton(text=LANG.b_clear, size_hint=(1, None), height=fs*3, on_release=lambda args:self.dialogClearDTC()))
        self.Layout.add_widget(MyButton(text=LANG.b_close, size_hint=(1, None), height=fs*3, on_release=lambda x:self.show_screen(x, self.screens)))

    def show_DTC(self, dt):
        requests = self.data_dtc[dt.id]['requests']
        box = GridLayout(cols=1, spacing=5, size_hint=(1, None))
        box.height = len(requests.ReceivedDI.keys()) * fs*3
        for k in requests.ReceivedDI.keys():
            if k == "NDTC" or k == "FirstDTC": continue
            value_hex = get_value({'request':requests.Name,'name':k}, self.decu, self.elm, resp=self.data_dtc[dt.id]['resp'])
            if value_hex['value'] == None or value_hex['value'] == 'None': continue
            glay = GridLayout(cols=2, size_hint=(1, None))
            glay.height = fs*2*math.ceil(len(k)*1.0/(glay.width*0.7/2))
            label1 = MyLabelBlue(text=k, halign='left', valign='middle', size_hint=(0.6, 1), font_size=fs)
            glay.add_widget(label1)
            if ':' not in value_hex['value']:
                value = int('0x' + value_hex['value'], 16)
                value = '[' + str(value) + '] ' + hex(value)
            else:
                value = value_hex['value'].split(':', 1)
                value = '[' + str(value[0]) + '] ' + value[1]
            v_h = fs*2*math.ceil(len(value)*1.0/(glay.width*0.4/2))
            if v_h > glay.height:
                glay.height = v_h
            label2 = MyLabelGreen(text=value, size_hint=(0.4, 1))
            glay.add_widget(label2)
            box.add_widget(glay)
        if 'FreezeFrame' in self.data_dtc[dt.id]:
            box.add_widget(Label(text='Момент проявления неисправности', size_hint=(1, None), height=fs*3))
            requests_mem = self.decu.requests[self.data_dtc[dt.id]['FreezeFrame']]
            box.height += len(requests_mem.ReceivedDI.keys()) * fs*3
            dtcread_command = requests_mem.SentBytes.encode('ascii')
            if dtcread_command == '1200040000':
                dtcread_command = '120004'+dt.id
            resp = self.elm.request(dtcread_command)
            for k in requests_mem.ReceivedDI.keys():
                glay = GridLayout(cols=2, size_hint=(1, None))
                glay.height = fs*2*math.ceil(len(k)*1.0/(glay.width*0.7/2))
                label1 = MyLabelBlue(text=k, halign='left', valign='middle', size_hint=(0.6, 1), font_size=fs)
                glay.add_widget(label1)
                value = get_value({'request':requests_mem.Name,'name':k}, self.decu, self.elm, resp=resp)
                if ':' in value['value']:
                    value = value['value'].split(':', 1)[1]
                v_h = fs*2*math.ceil(len(value['value'])*1.0/(glay.width*0.4/2))
                if v_h > glay.height:
                    glay.height = v_h
                label2 = MyLabelGreen(text=value, size_hint=(0.4, 1))
                glay.add_widget(label2)
                box.add_widget(glay)
        root = ScrollView(size_hint=(1, 1))
        root.add_widget(box)
        self.MyPopup(title=self.data_dtc[dt.id]['name'], content_box=root, height=self.Window_size[1], weigh=self.Window_size[0])

    def dialogClearDTC(self):
        self.ButtonConfirmation(LANG.l_cont12, 'clearDTC')

    def clearDTC(self):
        self.popup_confirm.dismiss()
        self.Layout.clear_widgets()
        self.Layout.add_widget(MyLabel(text=LANG.l_text5, bgcolor=(0,0.5,0.5,1)))
        if 'ClearDiagnosticInformation.All' in self.decu.requests.keys():
            requests = self.decu.requests['ClearDiagnosticInformation.All'].SentBytes
        elif 'ClearDTC' in self.decu.requests.keys():
            requests = self.decu.requests['ClearDTC'].SentBytes
        elif 'Clear Diagnostic Information' in self.decu.requests.keys():
            requests = self.decu.requests['Clear Diagnostic Information'].SentBytes
        else:
            self.Layout.add_widget(MyLabel(text=LANG.l_text6, bgcolor=(0,0.5,0,1)))
            requests = "14FF00"
        self.setEcuAdrequestsdress(self.getSelectedECU(self.xml))
        response = self.elm.request(requests)
        if 'WRONG' in response:
            self.Layout.add_widget(MyLabel(text=LANG.l_text7, bgcolor=(0,0.5,0,1)))
        else:
            self.Layout.add_widget(MyLabel(text=LANG.l_text8, bgcolor=(0,0.5,0,1)))
        self.Layout.add_widget(MyButton(text=LANG.b_close, size_hint=(1, None), height=fs*3, on_release=lambda x:self.show_screen(x, self.screens)))

    def ScanAllBtnClick(self):
        if self.elm.lf!=0:
            self.elm.lf.write("#load: "+self.filterText+"\n")
            self.elm.lf.flush()  
        self.addr = mod_ddt_utils.ddtAddressing(self.v_proj, self.eculist)
        vins = {}
        self.scantxt = Label(text='Init', width=self.Window_size[0]*0.95)
        popup_scan = Popup(title=LANG.l_title1, title_size=fs*1.5, title_align='center', content=self.scantxt, size=(self.Window_size[0], 400), size_hint=(None, None))
        popup_scan.open()
        
        EventLoop.idle()
        i = 0
        self.detectedEcus = {}
        x = 0
        p1=0
        self.back_can = ''
        p_xml = {}
        self.scantxt.text = LANG.l_cont7 + str(i) + '/' + str(len(self.addr.alist)) + LANG.l_cont8 + str(len(self.detectedEcus))
        EventLoop.idle()
        
        if self.v_proj == 'ALL_CARS':
            for p in ['KWP','CAN-500','CAN-250']:
                if p == 'KWP':
                    p1 = 'KWP'
                    self.elm.init_iso()
                else:
                    p1 = 'CAN'
                    self.elm.init_can()
                for Addr, pro in self.addr.alist.items():
                    self.cheks(Addr, pro['xml'].keys(), p1, pro['iso8'], i, len(self.addr.alist), vins)
                    i += 1
        else:
            for Addr, pro in self.addr.alist.items():
                p_xml[Addr] = {'CAN':[], 'KWP':[], 'iso8':pro['iso8']}
                for x, p in pro['xml'].items():
                    if p.startswith('CAN'):
                        p_xml[Addr]['CAN'].append(x)
                    else:
                        p_xml[Addr]['KWP'].append(x)
            for Addr, pro in p_xml.items():
                if len(pro['KWP']):
                    self.elm.init_iso()
                    self.cheks(Addr, pro['KWP'], 'KWP', pro['iso8'], i, len(p_xml), vins)
                if len(pro['CAN']):
                    self.elm.init_can()
                    self.cheks(Addr, pro['CAN'], 'CAN', pro['iso8'], i, len(p_xml), vins)
                i += 1
        self.elm.close_protocol()
        for ce in self.carecus:
            if ce['addr'] in self.detectedEcus.keys():
                ce['xml'] = self.detectedEcus[ce['addr']]['xml']
                if ce['xml'].startswith('not_ident'):
                    self.scantxt.text = u'Есть не определенные блоки группы %s автомобиля %s '%(str(ce['addr']),str(self.v_proj))
                    EventLoop.idle()
                    Not, DiagVersion, Supplier, Soft, Version = ce['xml'].split('#')
                    xml = mod_ddt_ecu.ecuSearch(self.v_proj, ce['addr'], DiagVersion, Supplier, Soft, Version, self.eculist)
                    if xml:
                        if isinstance(xml, list): xml = xml[0]
                        ce['xml'] = xml
                ce['iso8'] = self.detectedEcus[ce['addr']]['iso8']
                ce['ses'] = self.detectedEcus[ce['addr']]['ses']
                ce['undef'] = self.detectedEcus[ce['addr']]['undef']
                ce['dump'] = self.detectedEcus[ce['addr']]['dump']
                ce['prot'] = self.detectedEcus[ce['addr']]['prot']
        self.renewEcuList()
        if self.v_vin=='' and len(vins.keys()):
            self.v_vin = (max(vins.items(), key=operator.itemgetter(1))[0])
        if len(self.v_vin) > 0 and self.v_vin.isalnum():
            if True:
                mod_globals.savedCAR = 'savedCAR_'+self.v_vin+'.csv'
                self.SaveBtnClick(self.v_vin, None)
            else:
                mod_globals.savedCAR = 'savedCAR_'+self.v_proj+'.csv'
                self.SaveBtnClick(self.v_proj, None)
        else:
            mod_globals.savedCAR = 'savedCAR_'+self.v_proj+'.csv'
            self.SaveBtnClick(self.v_proj, None)
        popup_scan.dismiss()
        base.stopTouchApp()
        EventLoop.window.canvas.clear()
        mod_globals.opt_scan = False

    def cheks(self, Addr, xml, pro, iso, i=None, x=None, vins=None):
        self.scantxt.text = LANG.l_cont7 + str(i) + '/' + str(x) + LANG.l_cont8 + str(len(self.detectedEcus))
        self.setEcuAddress({'addr':Addr, 'xml':Addr, 'prot':pro, 'iso8':iso})
        StartSession, DiagVersion, Supplier, Soft, Version, Std, VIN = mod_scan_ecus.readECUIds(self.elm)
        if DiagVersion == '' and Supplier == '' and Soft == '' and Version == '': return
        xml = mod_ddt_ecu.ecuSearch(self.v_proj, Addr, DiagVersion, Supplier, Soft, Version, self.eculist, xml)
        if xml:
            if isinstance(xml, list): xml = xml[0]
            self.detectedEcus[Addr] = {'prot':pro, 'xml':xml,'ses':StartSession, 'undef':'0', 'iso8':iso}
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
        if True:
            r_hex = round(int(hex_string[0:2], 16)/255.0, 2)
        else:
            r_hex = 0
        if True:
            g_hex = round(int(hex_string[2:4], 16)/255.0, 2)
        else:
            g_hex = 0
        if True:
            b_hex = round(int(hex_string[4:6], 16)/255.0, 2)
        else:
            b_hex = 0
        return b_hex, g_hex, r_hex, 1.0

    def startScreen(self, data):
        if type(data) == dict:
            for r in data:
                if True:
                    if data[r]: continue
                else:
                    pass
                req = self.decu.requests[r].SentBytes
                if (req[:2] not in ['10'] + AllowedList) and not mod_globals.opt_exp:
                    continue
                if r not in self.REQ: self.REQ.append(r)

    def ButtonConfirmation(self, text, data=None):
        layout = GridLayout(cols=1, padding=10, spacing=10, size_hint=(1, 1))
        layout1 = GridLayout(cols=1, padding=5, spacing=5, size_hint=(1, None), height=fs*3*(len(text.split('\n'))+1.5))
        box2 = BoxLayout(orientation='horizontal', size_hint=(1, 0.15))
        if data == 'clearDTC':
            button1 = MyButton(text=LANG.l_text3, size_hint=(1, 1), on_release=lambda k:self.clearDTC())
        else:
            button1 = MyButton(text=LANG.l_text3, size_hint=(1, 1), on_release=lambda k:self.yes(data))
        if not 'ERROR' in text: box2.add_widget(button1)
        button2 = MyButton(text=LANG.l_text4, size_hint=(1, 1))
        box2.add_widget(button2)
        for i in text.split('\n'):
            if i == '': continue
            lab = MyLabel(text=i, size_hint=(1, None), height=fs*3, bgcolor=(0.5,0,0,1))
            layout1.add_widget(lab)
        root = ScrollView(size_hint=(1, 0.85))
        root.add_widget(layout1)
        layout.add_widget(root)
        layout.add_widget(box2)
        button2.bind(on_release=self.no)
        self.popup_confirm = Popup(title=LANG.l_title2, title_size=fs*1.5, title_align='center', content=layout, size=self.Window_size, size_hint=(None, None))
        self.popup_confirm.open()

    def no(self, instance):
        if True:
            self.popup_confirm.dismiss()
        else:
            pass
        self.start = True
        self.start = Clock.schedule_once(self.update_values, 0.02)
        return False

    def yes(self, slist):
        if True:
            self.popup_confirm.dismiss()
        else:
            pass
        confirmed = True
        layout = GridLayout(cols=1, padding=5, spacing=5, size_hint=(1, None), height=fs*4)
        if confirmed:
            for c in slist:
                rsp = '00'
                rsp = self.decu.elmRequest (c['c'], c['d'], cache=False)
                tmstr = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                layout.add_widget(MyLabel(text=tmstr+' >   '+c['c']+'\nRcvd:'+rsp, size_hint=(1, None), height=fs*4, bgcolor=(0,0.5,0,1)))
                layout.height += fs*4
        layout.height += fs*4.5
        root = ScrollView(size_hint=(1, 0.85))
        root.add_widget(layout)
        
        self.MyPopup(content_box=root)
        self.start = Clock.schedule_once(self.update_values, 0.02)
        if True:
            self.update_dInputs()
        else:
            pass

    def buttonPressed(self, btn, key):
        self.start = False
        for i, v in self.iValue.items():
            if i[:-len(v['request'])] in self.iLabels:
                self.iValue[i]['value'] = self.iLabels[i[:-len(v['request'])]].text
            elif i in self.oLabels:
                self.iValue[i]['value'] = self.oLabels[i].text
            elif i[:-len(v['request'])] in self.Labels:
                self.iValue[i]['value'] = self.Labels[i[:-len(v['request'])]].text

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
        commandSet = ''
        for c in slist:
            commandSet += "%-10s Delay:%-3s (%s)\n" % (c['c'], c['d'], c['r'].Name)
        self.ButtonConfirmation(commandSet, slist)

    def setEcuAddress(self, ce):
        ecudata = {'idTx': '',
                   'idRx': '',
                   'slowInit': '',
                   'fastInit': '',
                   'ModelId': ce['addr'],
                   'ecuname': ce['xml'],
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
                ecu = ast.literal_eval(str(json.dumps(line[4], ensure_ascii=False).encode('utf8')))
                ecu = line[4]
            return ecu

    def popup_dump(self, bt):
        try:
            bt = bt.id
        except:
            pass
        if bt.endswith('dump'): self.getDumpListByXml(self.label[bt[:-5]+'_xml'].text)
        else: self.getDumpListByXml(self.label[bt].text)
        lbltxt = Label(text=LANG.l_cont9)
        popup_init = Popup(title=LANG.l_load, title_size=fs*1.5, title_align='center', content=lbltxt, size_hint=(1, 1))
        popup_init.open()
        EventLoop.idle()
        sys.stdout.flush()
        layout = GridLayout(cols=1, spacing=5, size_hint=(1, None))
        layout.bind(minimum_height=layout.setter('height'))
        layout.add_widget(MyButton(text=LANG.b_clear1, size_hint=(1, None), height=fs*4, on_press=lambda bts,ids=bt: self.select_dump(bts, ids)))
        for v in self.v_dumpList:
            btn = MyButton(text=v, size_hint=(1, None), height=fs*4, on_press=lambda bts, ids = bt: self.select_dump(bts, ids))
            layout.add_widget(btn)
        self.root_dump = ScrollView(size_hint=(1, 1))
        self.root_dump.add_widget(layout)
        popup_init.dismiss()
        btn_close = MyButton(text=LANG.b_close, size_hint=(1, None), height=fs*4)
        layout.add_widget(btn_close)
        self.popup = Popup(title=LANG.l_title3, title_size=fs*1.5, title_align='center', content=self.root_dump, size_hint=(None, None), size=(self.Window_size[0], self.Window_size[1]*0.7))
        self.popup.open()
        btn_close.bind(on_press=self.popup.dismiss)

    def select_dump(self, bt, idds):
        if not self.roll_back:
            addr = idds.split('_')[0]
            for n in self.carecus:
                if n['addr'] == addr:
                    n['dump'] = bt.text
            if bt.text == LANG.b_clear1: bt.text = ''
            self.label[idds].text = bt.text
            self.renewEcuList()
        else:
            self.Roll_back = os.path.join(mod_globals.dumps_dir, bt.text)
            self.dumpRollBack()
        self.popup.dismiss()

    def getDumpListByXml(self, xmlname=None):
        if xmlname==None:
            self.v_dumpList = []
            if True:
                xml = self.dv_xml[:-4]
            else:
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
        if '_' in mod_globals.savedCAR:
            self.labels.text = mod_globals.savedCAR.split('_', 1)[1][:-4]
        else:
            self.labels.text = self.v_vin
        self.savedECU = MyButton(text=LANG.b_saved, size_hint=(0.3, 1), on_press=lambda args: self.SaveBtnClick(self.labels.text))
        glay.add_widget(MyLabel(text='savedCAR_', size_hint=(0.2, 1), halign='right', bgcolor=(0.5,0,0,1)))
        glay.add_widget(self.labels)
        glay.add_widget(self.savedECU)
        return glay

    def DDTScreen(self, xdoc):
        self.Screens = {}
        self.screens = {}
        self.screens[LANG.b_read_dtc] = ''
        #if self.Addr[:-4] == '2C': self.screens['AIRBAG Reset'] = ''
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
        self.screens[LANG.l_text9] = []
        for req in sorted(self.decu.requests.keys()):
            if self.decu.requests[req].SentBytes[:2] in ['21','22']:
                self.screens['ddt_all_commands'].append('ddt_all_commands'+req)

    def CarDoubleClick(self):
        self.addr = mod_ddt_utils.ddtAddressing(self.v_proj, self.eculist)
        for e in self.addr.alist:
            if len(self.addr.alist[e]['xml']) > 0:
                v_prot = ''
                v_xml = ''
                ecu = {}
                ecu['undef'] = '1'
                ecu['iso8'] = self.addr.alist[e]['iso8']
                ecu['XId'] = self.addr.alist[e]['XId']
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

    def renewEcuList(self):
        self.ecutree = []
        for ecu in mod_ddt_utils.multikeysort(self.carecus, ['undef','addr']):
            columns = (ecu['prot'], ecu['name'], ecu['xml'], ecu['dump'], ecu)
            if ecu['undef']=='0':
                self.ecutree.append(dict(text=ecu['addr'], values=columns, tag='t1'))
            else:
                self.ecutree.append(dict(text=ecu['addr'], values=columns, tag=''))

    def SaveBtnClick(self, name, pop=True):
        if not name:
            name = self.v_proj
        filename = os.path.join(mod_globals.user_data_dir, './savedCAR_'+str(name)+'.csv')
        with open(filename, 'w') as fout:
            car = ['car',self.v_proj, self.v_addr, self.v_pcan, self.v_mcan, self.v_vin]
            fout.write(';'.join(car)+'\n')
            for ecu in self.carecus:
                e = [ecu['undef'],
                     ecu['addr'],
                     ecu['XId'],
                     ecu['iso8'],
                     ecu['prot'],
                     ecu['name'],
                     ecu['xml'],
                     ecu['dump'],
                     ecu['ses']]
                fout.write(';'.join(e).encode('utf-8').decode('utf-8') + '\n')
        self.renewEcuList()
        mod_globals.savedCAR = 'savedCAR_'+str(name)+'.csv'
        copyfile(filename, os.path.join(mod_globals.user_data_dir, "./savedCAR_prev.csv"))
        if pop: self.MyPopup(content=LANG.l_cont11+name+'.csv', height=fs*30)
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
                ecu['XId'] = li[2]
                ecu['iso8'] = li[3]
                ecu['prot'] = li[4]
                ecu['name'] = li[5]
                ecu['xml'] = li[6]
                ecu['dump'] = li[7]
                ecu['ses']  = li[8]
                self.carecus.append(ecu)
        self.addr = mod_ddt_utils.ddtAddressing(self.v_proj, self.eculist)
        self.renewEcuList()

    def make_box_params(self, i, v):
        if self.make_box:
            self.BOX2.append(i)
        glay = GridLayout(cols=2, size_hint=(1, None), height=fs*6)
        label1 = MyLabelBlue(text=i, halign='left', valign='middle', size_hint=(0.5, 1), font_size=fs)
        glay.add_widget(label1)
        if i in self.iValue:
            glay.cols = 3
            if self.iValue[i]['value'] == LANG.l_enter_here:
                label_IT = TextInput(text=self.iValue[i]['value'], size_hint=(1, 1))
                self.Labels[i] = label_IT
                glay.add_widget(label_IT)
        elif i in self.dValue:
            label_D = MyLabelGreen(text=self.dValue[i]['value'], text_size=(None, fs*4), size_hint=(1, 1))
            self.Labels[i] = label_D
            glay.add_widget(label_D)
        if i in self.ListOption.keys():
            glay.cols = 3
            self.dropdowns[i+v] = DropDown(auto_width=False, width=self.Window_size[0]*0.8)
            for o in self.ListOption[i]:
                btn = MyButton(text=o, id=o, size_hint=(1, None), height=fs*3)
                btn.bind(on_release=lambda btn=btn, i=i+v: self.select_option(btn.text, i))
                self.dropdowns[i+v].add_widget(btn)
            self.triggers[i+v] = MyButton(text=self.ListOption[i][0], id=i+v, size_hint=(1, 1))
            self.triggers[i+v].bind(on_release=self.dropdowns[i+v].open)
            self.oLabels[i+v] = self.triggers[i+v]
            self.dropdowns[i+v].bind(on_select=lambda instance, x: setattr(self.triggers[i+v], 'text', x))
            glay.add_widget(self.triggers[i+v])
        
        if v in self.bValue.keys() and len(self.BValue) > 1:
            glay.cols = 4
            button = MyButton(text=self.bValue[v]['xText'], id=str(self.bValue[v]['send']), size_hint=(1, 1), on_release = lambda btn=self.bValue[v]['xText']: self.buttonPressed(btn.text, btn.id))
            glay.add_widget(button)
        if glay.cols == 2:
            glay.size_hint = (1, 1)
        return glay

    def select_dump_RollBack(self, xml):
        self.roll_back = True
        self.popup_dump(self.Addr)

    def dumpRollBack(self):
        self.roll_back = False
        fname = self.Roll_back
        
        if fname == '':
            return
        fname = fname
        (conf_2, cv_2) = self.decu.makeConf()

        savedMode = mod_globals.opt_demo
        mod_globals.opt_demo = True
        saveDumpName = mod_globals.dumpName
        self.decu.loadDump (fname)
        (conf_1, cv_1) = self.decu.makeConf(indump=True)

        mod_globals.dumpName = saveDumpName
        mod_globals.opt_demo = savedMode

        if mod_globals.opt_demo:
            self.decu.loadDump(mod_globals.dumpName)
        else:
            self.decu.clearELMcache()
        diff = list(set(conf_1)-set(conf_2))
        if len(diff) == 0:
            self.MyPopup(title=LANG.l_title7, content=LANG.l_cont14)
            return
        # show confirmation dialog if approve is True
        confirmed = True
        xText = ''
        sendDelay = '1000'
        slist = []
        smap = {}
        for i in diff:
            xText += "%-10s Delay:%s\n" % (i,sendDelay)
            smap['d'] = sendDelay
            smap['c'] = i
            slist.append (copy.deepcopy (smap))
        self.ButtonConfirmation(xText, slist)
        
        del(conf_1)
        del(conf_2)
        del(cv_1)
        del(cv_2)

    def askDumpName(self):
        flist = []
        for root, dirs, files in os.walk ("./dumps"):
            for f in files:
                if self.decu.ecufname.split ('/')[-1][:-4] in f:
                    if True:
                        uda = f.split ('_')[0]
                        fda = datetime.datetime.fromtimestamp (int (uda)).strftime ('%Y/%m/%d %H:%M:%S')
                        flist.append (fda + '\t#\t' + f)
                    else:
                        return ""
        if len (flist) == 0:
            return ""
    
        ch = ListDialog (self.root, "Choose dump for roll back", flist).show ()
    
        if True:
            fname = './dumps/' + ch.split ("#")[1].strip ()
        else:
            return ""
    
        # check dump file
        if self.decu.ecufname.split ('/')[-1][:-4] not in fname:
            return ""
    
        return fname

    def MyPopup(self, close=True, title=None, content_box=None, content=None, height=None, weigh=None, stop=None):
        if title:
            title = title
        else:
            title = 'INFO'
        if content:
            content = content
        else:
            content = 'INFO'
        if not height:
            height = self.Window_size[1]*0.9
        if not weigh:
            weigh = self.Window_size[0]*0.9
        layout = GridLayout(cols=1, padding=10, spacing=20, size_hint=(1, 1))
        if not content_box:
            label = MyLabel(text=content, size_hint=(1, 1))
            if label.height > self.Window_size[1] * 0.8:
                label.height = self.Window_size[1] *0.6
        else:
            label = content_box
        layout.add_widget(label)
        btn = MyButton(text=LANG.b_close, height=fs*3)
        if close: layout.add_widget(btn)
        popup = Popup(title=title, title_size=fs*1.5, title_align='center', content=layout, size_hint=(None, None), size=(weigh, height))
        popup.open()
        if stop:
            btn.bind(on_press=stop)
        else:
            btn.bind(on_press=popup.dismiss)

    def guiSaveDump(self, decu):
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
        if 'bgcolor' in kwargs:
            self.bgcolor = kwargs['bgcolor']
            del kwargs ['bgcolor']
        else:
            self.bgcolor =(0, 0, 0, 0)
        if 'id' in kwargs:
            self.id = kwargs['id']
            del kwargs ['id']
        super(MyLabel_scr, self).__init__(**kwargs)
        
        self.bind(size=self.setter('text_size'))
        if 'halign' not in kwargs:
            self.halign = 'center'
        if 'valign' not in kwargs:
            self.valign = 'middle'
        if 'height' not in kwargs:
            self.height = self.size[1]
        if 'size' in kwargs:
            self.size[0] = self.size[0]/0.9999
        if 'pos' in kwargs:
            self.pos[0] = self.pos[0]/0.9999
    def on_size(self, *args):
        if not self.canvas:
            return
        self.canvas.before.clear()
        """with self.canvas.before:
            Color(0, 0, 0, 1)
            Rectangle(pos=(self.pos[0], self.pos[1]), size=(self.size[0], self.size[1]))"""
        with self.canvas.before:
            Color(self.bgcolor[0], self.bgcolor[1], self.bgcolor[2], self.bgcolor[3])
            Rectangle(pos=(self.pos[0], self.pos[1]), size=(self.size[0], self.size[1]))
            
class MyLabel(Label):
    global fs
    id = ''
    def __init__(self, **kwargs):
        fs = mod_globals.fontSize
        if 'bgcolor' in kwargs:
            self.bgcolor = kwargs['bgcolor']
            del kwargs ['bgcolor']
        else:
            self.bgcolor =(0, 0, 0, 0)
        
        if 'id' in kwargs:
            self.id = kwargs['id']
            del kwargs ['id']

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
            self.size[0] = self.size[0]/0.9999
        if 'pos' in kwargs:
            self.pos[0] = self.pos[0]/0.9999
        if 'height' not in kwargs:
            fmn = 1.4
            lines = len(self.text.split('\n'))
            simb = len(self.text) * 1.0 / self.width
            if 1 > simb: lines = 2
            if lines < simb: lines = simb
            if lines < 2: lines = 2
            if lines > 20: lines = 20
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
        self.bind(size=self.setter('text_size'))
        if 'text_size' not in kwargs:
            self.text_size =(self.size[0], None)
        if 'halign' not in kwargs:
            self.halign = 'center'
        if 'valign' not in kwargs:
            self.valign = 'middle'
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
        self.bind(size=self.setter('text_size'))
        if 'text_size' not in kwargs:
            self.text_size =(self.size[0], None)
        if 'halign' not in kwargs:
            self.halign = 'center'
        if 'valign' not in kwargs:
            self.valign = 'middle'
    def on_size(self, widget, size):
        
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
    id = ''
    def __init__(self, **kwargs):
        if 'id' in kwargs:
            self.id = kwargs['id']
            del kwargs ['id']
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
    global LANG
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
        global LANG
        global eculist
        self.elm = 0
        self.cecu = cecu
        self.ecufname = '' 
        self.requests = {}
        self.datas = {}
        self.req4data = {}
        self.cmd4data = {}
        self.req4sent = {}
        LANGmap = {}
        self.BaudRate = '500000'
        self.Multipoint = '1'
    
    def __del__(self):
        if True:
            del(self.elm)
            del(self.cecu)
            del(self.ecufname)
            del(self.requests)
            del(self.datas)
            del(self.req4data)
            del(self.cmd4data)
            del(self.req4sent)
            del(LANGmap)
            del(self.BaudRate)
            del(self.Multipoint)
        else:
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
        
        if key in LANGmap.keys():
            return LANGmap[key]
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
            n = [v for v in iValues.keys() if (v.startswith(d.Name) and v.endswith(requestName))]
            if not len(n):
                n = [v for v in iValues.keys() if v.endswith(requestName)]
                if not len(n):
                    n = [v for v in iValues.keys() if v.startswith(d.Name)]
                    if not len(n):
                        continue
            if True:
                value = iValues[n[0]]['value'].strip()
            else:
                value = iValues[d.Name].strip()
            value = self.getValueFromInput(d, value)
            littleEndian = True if sdi.Endian=="Little" else False
            sb = sdi.FirstByte - 1 
            bits = d.BitsCount
            sbit = sdi.BitOffset
            bytes =(bits+sbit-1)//8 + 1
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
        if value == LANG.l_enter_here:
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
            if len(value)<(d.BitsCount//8):
                value += ' '*(d.BitsCount//8 - len(value))
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

    def getValueForConfig(self, d):

        res = 'ERROR'

        if d in self.req4data.keys ():
            rcmd = self.req4data[d]
        else:
            return res

        self.ddecu = DDTECU(None)
        self.ddecu.datas = self.datas
        self.ddecu.requests = self.requests
        res = get_value({'request':rcmd, 'name':d}, self.ddecu, self.elm)
        if not self.datas[d].BytesASCII:
            if res['value'] != mod_globals.none_val:
                res = '0x' + res['value']
            else:
                res = res['value']

        if (res==mod_globals.none_val):
            res = self.getValueForConfig_second_cmd(d,rcmd)
        return res
        
    def getValueForConfig_second_cmd(self, d, first_cmd):
        res = 'ERROR'
        rcmd = ''
        for c in self.requests.keys():
            if c == first_cmd: continue
            if d in self.requests[c].ReceivedDI.keys():
                rcmd = c
                break

        if rcmd == '':
            return 'ERROR'

        res = get_value({'request':rcmd, 'name':d}, self.ddecu, self.elm)
        if not self.datas[d].BytesASCII:
            if res['value'] != mod_globals.none_val:
                res = '0x' + res['value']
            else:
                res = res['value']

        return res

    def makeConf( self, indump = False, annotate = False ):

        config = []
        conf_v = {}
        config_ann = []
        
        sentValues = {}
        for r in sorted( self.requests.values(), key = lambda x: x.SentBytes):
            if not (r.SentBytes[0:2].upper () == '3B' or r.SentBytes[0:2].upper () == '2E') or len (r.SentDI) == 0:
                continue
            
            if annotate:
                config_ann.append('#'*60)
                config_ann.append('# '+r.Name)

            sentValues.clear ()
            for di in sorted(r.SentDI.values(), key = lambda x: x.FirstByte*8+x.BitOffset):
                d = di.Name
                
                if indump:
                    if d in self.req4data.keys ():
                        first_cmd = self.req4data[d]
                        i_r_cmd = self.requests[self.req4data[d]].SentBytes
                        if i_r_cmd not in self.elm.ecudump.keys() or (i_r_cmd in self.elm.ecudump.keys() and self.elm.ecudump[i_r_cmd]==''):
                            second_is = False
                            for c in self.requests.keys():
                                if c == first_cmd: continue
                                if d in self.requests[c].ReceivedDI.keys():
                                    second_is = True
                                    break
                                if not second_is:
                                    continue
                                    
                val = self.getValueForConfig( d )

                if 'ERROR' in val:
                    continue
                    
                sentValues[d] = val
                conf_v[d] = val
                
                if annotate:
                    val_ann = self.getValue(d)
                    config_ann.append('##         '+d + ' = ' + val_ann)

            if len (sentValues) != len (r.SentDI):
                if len (r.SentDI) == 2 and r.SentBytes[0:2].upper () == '3B':
                    SDIs = sorted(r.SentDI.values(), key=operator.attrgetter("FirstByte","BitOffset"))
                    if len(self.datas[SDIs[0].Name].List)>0:
                        for list_el_key in self.datas[SDIs[0].Name].List.keys():
                            list_el_val = self.datas[SDIs[0].Name].List[list_el_key]
                            found = False
                            fdk = ""
                            for datas_keys in self.datas.keys():
                                if datas_keys in list_el_val:
                                    if len(datas_keys)>len(fdk):
                                        fdk = datas_keys
                                    found = True
                            if found:
                                if SDIs[0].Name not in sentValues.keys():
                                    sentValues[SDIs[0].Name] = ''
                                sentValues[SDIs[0].Name] = hex(list_el_key)
                                if SDIs[1].Name not in sentValues.keys():
                                    sentValues[SDIs[1].Name] = ''
                                sentValues[SDIs[1].Name] = self.getValueForConfig(fdk)
                                conf_v[SDIs[1].Name] = self.getValueForConfig(fdk)
                                sendCmd = self.packValues (r.Name, sentValues)
                                config.append(sendCmd)
                                if annotate:
                                    config_ann.append(sendCmd)
                                    config_ann.append('')
                continue
            else:
                sendCmd = self.packValues (r.Name, sentValues)
                if 'ERROR' in sendCmd:
                    continue
                config.append (sendCmd)
                if annotate:
                    config_ann.append(sendCmd)
                    config_ann.append('')

        sentValues.clear ()

        if annotate:
            return config_ann, conf_v
        else:
            return config, conf_v
