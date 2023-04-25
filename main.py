# -*- coding: utf-8 -*-
try:
    from kivy_deps import sdl2, glew
except:
    pass
from kivy.utils import platform
from kivy.config import Config
Config.set('kivy', 'exit_on_escape', '0')
if platform != 'android':
    import ctypes
    user32 = ctypes.windll.user32
    Config.set('graphics', 'position', 'custom')
    Config.set('graphics', 'left', int(user32.GetSystemMetrics(0)/3))
    Config.set('graphics', 'top',  20)
    from kivy.core.window import Window
    Window.size = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    if Window.size[1] > Window.size[0]:
        fs = Window.size[1]*8.0/Window.size[0]
        Window.size = Window.size[0]*0.6, Window.size[0]*0.9
    else:
        fs = Window.size[0]*8.0/Window.size[1]
        Window.size = Window.size[1]*0.6, Window.size[1]*0.9
else:
    from kivy.core.window import Window
    if Window.size[1] > Window.size[0]:
        fs = Window.size[1]*8.0/Window.size[0]
    else:
        fs = Window.size[0]*8.0/Window.size[1]
from mod_db_manager import get_zip
from mod_elm import ELM
import mod_globals, mod_ddt_utils, mod_ddt
mod_globals.os = platform
from kivy import base
import webbrowser, time
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.switch import Switch
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.floatlayout import FloatLayout
import traceback
import os, sys, glob

__all__ = 'install_android'
__version__ = '0.12.24'

if mod_globals.os == 'android':
    fs = fs*2
    try:

        from jnius import cast, autoclass
        from android import mActivity, api_version
        import glob
        
        from android.permissions import request_permissions, check_permission, Permission

        permissions = []
        if api_version > 30:
            try:
                if (check_permission('android.permission.BLUETOOTH_CONNECT') == False):
                    permissions.append('android.permission.BLUETOOTH_CONNECT')
            except:
                pass
            try:
                if (check_permission('android.permission.BLUETOOTH_SCAN') == False):
                    permissions.append('android.permission.BLUETOOTH_SCAN')
            except:
                pass

        if api_version <= 29:
            try:
                if (check_permission('android.permission.WRITE_EXTERNAL_STORAGE') == False):
                    permissions.append('android.permission.WRITE_EXTERNAL_STORAGE')
            except:
                pass
            try:
                if (check_permission('android.permission.READ_EXTERNAL_STORAGE') == False):
                    permissions.append('android.permission.READ_EXTERNAL_STORAGE')
            except:
                pass

        try:
            request_permissions (permissions)
        except:
            print('Permission request error!')

        Environment = autoclass('android.os.Environment')       
        AndroidPythonActivity = autoclass('org.kivy.android.PythonActivity')

        try:
            if api_version > 29:
                Intent = autoclass("android.content.Intent")
                Settings = autoclass("android.provider.Settings")
                Uri = autoclass("android.net.Uri")
                if Environment.isExternalStorageManager():
                    pass
                else:
                    try:
                        activity = mActivity.getApplicationContext()
                        uri = Uri.parse("package:" + activity.getPackageName())
                        intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION, uri)
                        currentActivity = cast(
                        "android.app.Activity", AndroidPythonActivity.mActivity
                        )
                        currentActivity.startActivityForResult(intent, 101)
                    except:
                        intent = Intent()
                        intent.setAction(Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION)
                        currentActivity = cast(
                        "android.app.Activity", AndroidPythonActivity.mActivity
                        )
                        currentActivity.startActivityForResult(intent, 101)
        except:
            print('ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION unavailable')

        waitPermissionTimer = 0
        permissionIsGranted = False
        while (permissionIsGranted == False) & (waitPermissionTimer < 5):
            time.sleep(0.5)
            waitPermissionTimer = waitPermissionTimer + 0.5
            permissionIsGranted = True
            for perm in permissions:
                if (check_permission(perm) == False):
                    permissionIsGranted = False

            if api_version > 29:
                if (Environment.isExternalStorageManager() == False):
                    permissionIsGranted = False
        
        user_datadir = Environment.getExternalStorageDirectory().getAbsolutePath() + '/pyddt/'
        mod_globals.user_data_dir = user_datadir
        mod_globals.cache_dir = user_datadir + '/cache/'
        mod_globals.log_dir = user_datadir + '/logs/'
        mod_globals.dumps_dir = user_datadir + '/dumps/'

        AndroidActivityInfo = autoclass('android.content.pm.ActivityInfo')
        Params = autoclass('android.view.WindowManager$LayoutParams')
    except:
        mod_globals.ecu_root = '../'
        try:
            import serial
            from serial.tools import list_ports
        except:
            pass
elif mod_globals.os == 'nt':
    import pip
    try:
        import serial
    except ImportError:
        pip.main(['install', 'pyserial'])
    try:
        import colorama
    except ImportError:
        pip.main(['install', 'colorama'])
        try:
            import colorama
        except ImportError:
            sys.exit()
    colorama.init()
else:
    try:
        import serial
        from serial.tools import list_ports
    except:
        pass

os.chdir(os.path.dirname(os.path.realpath(sys.argv[0])))
argv_glob = sys.argv
sys.argv = sys.argv[0:1]

def my_excepthook(excType, excValue, tb):
    message = traceback.format_exception(excType, excValue, tb)
    string = '__version__: '+__version__+'\n'+str(time.ctime())+'\n'
    for m in message:
        string += m
    error = TextInput(text=str(string))
    if mod_globals.os == 'android':
        with open(os.path.join(mod_globals.log_dir, 'crash_'+str(time.strftime("%Y-%m-%d-%H.%M.%S", time.localtime()))+'.txt'), 'w') as fout:
            fout.write(str(string))

    popup = Popup(title='Crash', content=error, size=(Window.size[0]*0.9, Window.size[1]*0.9), size_hint=(None, None), auto_dismiss=True, on_dismiss=exit)
    popup.open()
    base.runTouchApp()
    
    exit(2)

sys.excepthook = my_excepthook
resizeFont = False

def set_orientation_landscape():
    if mod_globals.os == 'android':
        activity = AndroidPythonActivity.mActivity
        activity.setRequestedOrientation(AndroidActivityInfo.SCREEN_ORIENTATION_LANDSCAPE)

def set_orientation_portrait():
    if mod_globals.os == 'android':
        activity = AndroidPythonActivity.mActivity
        activity.setRequestedOrientation(AndroidActivityInfo.SCREEN_ORIENTATION_PORTRAIT)

class PYDDT(App):

    def __init__(self):
        
        self.button = {}
        self.textInput = {}
        self.ptree = {}
        
        self.elm = None
        super(PYDDT, self).__init__()
        Window.bind(on_keyboard=self.key_handler)

    def key_handler(self, window, keycode1, keycode2, text, modifiers):
        global resizeFont
        if resizeFont:
            return True
        if (keycode1 == 45 or keycode1 == 269) and mod_globals.fontSize > 10:
            mod_globals.fontSize = mod_globals.fontSize - 1
            resizeFont = True
            self.stop()
            return True
        if (keycode1 == 61 or keycode1 == 270) and mod_globals.fontSize < 40:
            mod_globals.fontSize = mod_globals.fontSize + 1
            resizeFont = True
            self.stop()
            return True
        if keycode1 == 27:
            exit()
        return False

    def build(self):
        if mod_globals.os == 'android':
            permissionIsGranted = True
            permissionErrorLayout = GridLayout(cols=1, padding=15, spacing=15, size_hint=(1, 1))
            permissionErrorLayout.add_widget(MyLabel(text='Permission not granted', font_size=(fs*0.9), height=fs*1.4, multiline=True, size_hint=(1, 1)))
            for perm in permissions:
                if (check_permission(perm) == False):
                    permissionIsGranted = False
                    permissionErrorLayout.add_widget(MyLabel(text=perm + ':' +str(check_permission(perm)), font_size=(fs*0.9), height=fs*1.4, multiline=True, size_hint=(1, 1)))
            if api_version > 29:
                if (Environment.isExternalStorageManager() == False):
                    permissionErrorLayout.add_widget(MyLabel(text='FILES_ACCESS_PERMISSION : False', font_size=(fs*0.9), height=fs*1.4, multiline=True, size_hint=(1, 1)))
                    permissionIsGranted = False
            if api_version == 29:
                if (Environment.isExternalStorageLegacy() == False):
                    permissionErrorLayout.add_widget(MyLabel(text='LegacyExternalStorage : False', font_size=(fs*0.9), height=fs*1.4, multiline=True, size_hint=(1, 1)))
                    permissionIsGranted = False
            permissionErrorLayout.add_widget(MyLabel(text='Android api: ' + str(api_version), font_size=(fs*0.9), height=fs*1.4, multiline=True, size_hint=(1, 1)))
            permissionErrorLayout.add_widget(MyLabel(text='Version: ' + str(__version__), font_size=(fs*0.9), height=fs*1.4, multiline=True, size_hint=(1, 1)))
            permissionErrorLayout.add_widget(MyButton(text='Click to exit and check permissions!!!', valign = 'middle', halign = 'center', size_hint=(1, 1), font_size=fs*1.5, height=fs*3, on_press=exit))
            if (permissionIsGranted == False):
                return permissionErrorLayout

        global LANG
        self.settings = mod_globals.Settings()
        if mod_globals.opt_lang == 'ru':
            import lang_ru as LANG
        elif mod_globals.opt_lang == 'en':
            import lang_en as LANG
        else:
            import lang_fr as LANG
        get_zip()
        Fl = FloatLayout()
        layout = GridLayout(cols=1, padding=5, spacing=10, size_hint=(1, None))
        layout.bind(minimum_height=layout.setter('height'))
        title = MyLabel(text='PyDDT', font_size=(fs*3), size_hint=(1, None))
        layout.add_widget(title)
        try:
            self.archive = str(mod_globals.db_archive_file).rpartition('/')[2]
        except:
            self.archive = str(mod_globals.db_archive_file).rpartition('\\')[2]
        if self.archive == 'None':
            self.archive = 'NOT BASE DDT2000'
            root = GridLayout(cols=1, padding=15, spacing=15, size_hint=(1, 1))
            linkB = MyButton(text='Click to download database.\n\nНажмите для скачивания базы.', valign = 'middle', halign = 'center', size_hint=(1, 1), font_size=fs*1.5, on_release=lambda args:webbrowser.open('https://t.me/c/1606228375/25'))
            exitB = MyButton(text='Click on the screen to exit and place the base in the folder /pyddt.\n\nНажмите на экран для выхода и поместите базу в папку /pyddt.', valign = 'middle', halign = 'center', size_hint=(1, 1), font_size=fs*1.5, on_press=exit)
            linkB.bind(size=linkB.setter('text_size'))
            exitB.bind(size=exitB.setter('text_size'))
            root.add_widget(linkB)
            root.add_widget(exitB)
            popup = Popup(title=self.archive, title_size=fs*1.5, title_align='center', content=root, size=(Window.size[0], Window.size[1]), size_hint=(None, None), auto_dismiss=True)
            return popup
        layout.add_widget(MyLabel(text='DB archive : ' + self.archive, font_size=(fs*0.9), height=fs*1.4, multiline=True, size_hint=(1, None)))
        layout.add_widget(MyButton(text=LANG.b_scan, id='scan', font_size=fs*2, on_press=self.scanALLecus, height=(fs * 4)))
        self.but_demo = MyButton(text=LANG.b_open, font_size=fs*2, id='demo', on_press=lambda bt:self.OpenEcu(bt), height=(fs * 4))
        layout.add_widget(self.but_demo)
        layout.add_widget(self.make_savedEcus())
        layout.add_widget(self.in_car())
        layout.add_widget(self.make_bt_device_entry())
        layout.add_widget(self.make_input_toggle(LANG.b_log, mod_globals.opt_log, 'down' if len(mod_globals.opt_log) > 0 else  'normal'))
        layout.add_widget(self.make_input(LANG.l_font_size, str(mod_globals.fontSize)))
        layout.add_widget(self.make_box_switch(LANG.l_dump, mod_globals.opt_dump))
        layout.add_widget(self.make_box_switch('CAN2', mod_globals.opt_can2))
        layout.add_widget(self.lang_app())
        root = ScrollView(size_hint=(1, 1))
        root.add_widget(layout)
        Fl.add_widget(root)
        Fl.add_widget(MyLabel(text='Version : ' + __version__ , size_hint =(.3, None), pos=(0, Window.size[1]-title.height/2), font_size=(fs*0.8), height=fs*1.4, multiline=True))
        return Fl

    def scanALLecus(self, instance):
        mod_globals.opt_scan = True
        self.finish(instance.id)
        self.settings.save()
        label = Label(text=LANG.l_n_car1, font_size=fs*3, size_hint=(1, 1), halign = 'center', valign = 'middle', text_size=(Window.size[0]*0.7, Window.size[1]*0.7))
        popup = Popup(title=LANG.error, title_size=fs*1.5, title_align='center', content=label, size=(Window.size[0]*0.8, Window.size[1]*0.8), size_hint=(None, None))
        if mod_globals.opt_car != LANG.b_select:
            lbltxt = Label(text=LANG.l_scan, font_size=fs)
            popup_init = Popup(title=LANG.l_load, title_size=fs*1.5, title_align='center', content=lbltxt, size=(Window.size[0]*0.8, Window.size[1]*0.8), size_hint=(None, None))
            popup_init.open()
            base.EventLoop.idle()
            popup_init.dismiss()
            base.EventLoop.window.canvas.clear()
            mod_ddt.DDT_START(mod_globals.opt_car, self.elm)
            base.EventLoop.idle()
        else:
            popup.open()
            return
    
    def OpenEcu(self, instance):
        if instance.id == 'demo': 
            mod_globals.opt_demo = True
        self.finish(instance.id)
        self.settings.save()
        label = Label(text=LANG.l_n_car2, font_size=fs*3, size_hint=(1, 1), halign = 'center', valign = 'middle', text_size=(Window.size[0]*0.7, Window.size[1]*0.7))
        popup = Popup(title=LANG.error, title_size=fs*1.5, title_align='center', content=label, size=(Window.size[0]*0.8, Window.size[1]*0.8), size_hint=(None, None))
        if mod_globals.opt_car !=LANG.b_select or mod_globals.savedCAR != LANG.b_select:
            instance.background_color= (0,1,0,1)
            if mod_globals.opt_demo:
                lbltxt = Label(text=LANG.l_demo)
            elif mod_globals.savedCAR != LANG.b_select:
                lbltxt = Label(text=LANG.l_savedcar, font_size=fs)
            else:
                lbltxt = Label(text=LANG.l_scan, font_size=fs)
            popup_init = Popup(title=LANG.l_load, title_size=fs*1.5, title_align='center', content=lbltxt, size=(Window.size[0]*0.8, Window.size[1]*0.8), size_hint=(None, None))
            popup_init.open()
            base.EventLoop.idle()
            sys.stdout.flush()
            popup_init.dismiss()
            self.stop()
            base.EventLoop.window.canvas.clear()
            mod_ddt.DDT_START(mod_globals.opt_car, self.elm)
        else:
            popup.open()
            return

    def make_savedEcus(self):
        ecus = sorted(glob.glob(os.path.join(mod_globals.user_data_dir, 'savedCAR_*.csv')))
        toggle = MyButton(text=LANG.b_savedcar, id='open', size_hint=(0.4, None), height=(fs * 3), on_press=lambda bt:self.OpenEcu(bt))
        self.ecus_dropdown = DropDown(height=(fs))
        glay = MyGridLayout(cols=2, padding=(fs/3), height=(fs * 4), size_hint=(1, None))
        for s_ecus in ecus:
            if s_ecus == 'savedCAR_prev.csv': continue
            s_ecus = os.path.split(s_ecus)[1]
            btn= MyButton(text=s_ecus, height=(fs * 3))
            btn.bind(on_release=lambda btn: self.ecus_dropdown.select(btn.text))
            self.ecus_dropdown.add_widget(btn)
        self.ecusbutton = MyButton(text=LANG.b_select, size_hint=(0.7, None), height=(fs * 3))
        self.ecusbutton.bind(on_release=self.ecus_dropdown.open)
        self.ecus_dropdown.bind(on_select=lambda instance, x: setattr(self.ecusbutton, 'text', x))
        glay.add_widget(toggle)
        glay.add_widget(self.ecusbutton)
        return glay

    def finish(self, instance):
        mod_globals.opt_car = self.carbutton.text
        mod_globals.savedCAR = self.ecusbutton.text
        #mod_globals.opt_car = 'x81 : Esp'
        if instance == 'scan':
            mod_globals.opt_demo = False
            mod_globals.opt_scan = True
        elif instance == 'demo' and mod_globals.savedCAR != LANG.b_select:
            mod_globals.opt_scan = False
            mod_globals.opt_demo = True
        elif instance == 'open' or mod_globals.opt_car == LANG.b_all_cars:
            mod_globals.opt_scan = False
        mod_globals.windows_size = Window.size
        mod_globals.opt_dump = self.button[LANG.l_dump].active
        mod_globals.opt_can2 = self.button['CAN2'].active
        #mod_globals.savedCAR = 'savedCAR_x95.csv'
        #mod_globals.savedCAR = 'savedCAR_XTAGFL110LY351920VESTA.csv'
        if self.button[LANG.b_log].state == 'down':
            mod_globals.opt_log = 'log.txt' if self.textInput[LANG.b_log].text == '' else self.textInput[LANG.b_log].text
        else:
            mod_globals.opt_log = ''
        if 'com1' in self.mainbutton.text.lower() or 'com6' in self.mainbutton.text.lower():
            mod_globals.opt_port = '127.0.0.1:35000'
        elif 'wifi' in self.mainbutton.text.lower():
            mod_globals.opt_port = '192.168.0.10:35000'
        else:
            bt_device = self.mainbutton.text.rsplit('>', 1)
            if mod_globals.os != 'android':
                try:
                    mod_globals.opt_port = bt_device[1]
                except:
                    mod_globals.opt_port = bt_device[0]
            else:
                mod_globals.opt_port = bt_device[0]
            if len(bt_device) > 1:
                mod_globals.opt_dev_address = bt_device[-1]
            mod_globals.bt_dev = self.mainbutton.text
        try:
            mod_globals.fontSize = int(self.textInput[LANG.l_font_size].text)
        except:
            mod_globals.fontSize = 20
        if mod_globals.opt_car != LANG.b_select or (mod_globals.savedCAR != LANG.b_select and not mod_globals.opt_scan):
            try:
                self.elm = ELM(mod_globals.opt_port, mod_globals.opt_speed, mod_globals.opt_log)
                #self.stop()
            except:
                labelText = '''
                    Could not connect to the ELM.

                    Possible causes:
                    - Bluetooth is not enabled
                    - other applications are connected to your ELM e.g Torque
                    - other device is using this ELM
                    - ELM got unpaired
                    - ELM is read under new name or it changed its name

                    Check your ELM connection and try again.
                '''
                lbltxt = Label(text=labelText, font_size=mod_globals.fontSize)
                popup_load = Popup(title='ELM connection error', title_size=fs*1.5, title_align='center', content=lbltxt, size=(Window.size[0]*0.9, Window.size[1]*0.9), auto_dismiss=True, on_dismiss=exit)
                popup_load.open()
                base.runTouchApp()
                exit(2)
                return
    def find_in_car(self, ins):
        glay = GridLayout(cols=1, size_hint=(1, 1))
        self.find = TextInput(text='', size_hint=(1, None), font_size=fs*1.5, multiline=False, height=(fs * 3), padding=[fs/2, fs/2])
        glay.add_widget(self.find)
        glay.add_widget(MyButton(text='FIND', height=(fs * 3), on_release=lambda btn:self.popup_in_car(btn.text)))
        self.popup = Popup(title='FIND CAR', title_size=fs*1.5, title_align='center', content=glay, size=(Window.size[0]*0.8, fs*12), size_hint=(None, None), auto_dismiss=True)
        self.popup.open()

    def in_car(self):
        self.avtosd = mod_ddt_utils.ddtProjects().plist
        glay = MyGridLayout(cols=3, padding=(fs/3), height=(fs * 4), size_hint=(1, None))
        label1 = MyLabel(text=LANG.l_car, halign='left', size_hint=(0.6, None), height=(fs * 3))
        label1.bind(size=label1.setter('text_size'))
        glay.add_widget(label1)
        self.dropdown = DropDown(height=(fs * 3))
        glay.add_widget(MyButton(text=LANG.b_find, size_hint=(0.5, None), height=(fs * 3), on_press=self.find_in_car))
        btn = MyButton(text=LANG.b_all_cars, height=(fs * 3))
        btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))
        self.dropdown.add_widget(btn)
        for avto in self.avtosd:
            btn = MyButton(text=avto['name'], height=(fs * 3))
            btn.bind(on_release=lambda bt, a=avto: self.popup_in_car(bt.text, a))
            self.dropdown.add_widget(btn)
        self.carbutton = MyButton(text=LANG.b_select, height=(fs * 3))
        self.carbutton.bind(on_release=self.dropdown.open)
        self.dropdown.bind(on_select=lambda instance, x: setattr(self.carbutton, 'text', x))
        glay.add_widget(self.carbutton)
        return glay

    def popup_in_car(self, text, avto=[]):
        try:
            self.popup.dismiss()
        except:
            pass
        layout = MyGridLayout(cols=1, padding=(fs/3), height=(fs * 4), size_hint=(1.0, None))
        layout.bind(minimum_height=layout.setter('height'))
        if text == 'FIND':
            for avto in self.avtosd:
                for car in avto['list']:
                    if self.find.text.lower() in str(car).lower():
                        btn = MyButton(text=car['code']+' : '+car['name'], font_size=fs*1.5, height=(fs * 3))
                        layout.add_widget(btn)
                        btn.bind(on_release=lambda btn: self.press_car(btn.text))
        else:
            for car in avto['list']:
                c = car['name']
                try:
                    if not c.startswith('('):
                        c = c.split('(')[0]
                except:
                    pass
                btn = MyButton(text=car['code']+' : '+c, font_size=fs*1.5, height=(fs * 3))
                layout.add_widget(btn)
                btn.bind(on_release=lambda btn: self.press_car(btn.text))
        root = ScrollView(size_hint=(1, 1), do_scroll_x=False, pos_hint={'center_x': 0.5,'center_y': 0.5})
        root.add_widget(layout)
        self.popup = Popup(title=text, title_size=fs*1.5, title_align='center', content=root, size=(Window.size[0]*0.9, Window.size[1]*0.9), size_hint=(None, None), auto_dismiss=True)
        self.popup.open()

    def press_car(self, btn):
        self.popup.dismiss()
        self.dropdown.select(btn)

    def make_box_switch(self, str1, active, callback = None):
        label1 = MyLabel(text=str1, halign='left', size_hint=(1, None), height=(fs * 3))
        sw = Switch(active=active, size_hint=(1, None), height=(fs * 3))
        if callback:
            sw.bind(active=callback)
        self.button[str1] = sw
        label1.bind(size=label1.setter('text_size'))
        glay = MyGridLayout(cols=2, padding=(fs/3), height=(fs * 4), size_hint=(1, None))
        glay.add_widget(label1)
        glay.add_widget(sw)
        return glay

    def make_bt_device_entry(self):
        ports = mod_ddt_utils.getPortList()
        label1 = MyLabel(text='ELM port', halign='left', size_hint=(0.7, None))
        self.bt_dropdown = DropDown(height=(fs * 2))
        label1.bind(size=label1.setter('text_size'))
        glay = MyGridLayout(cols=2, padding=(fs/3), height=(fs * 4), size_hint=(1, None))
        btn = MyButton(text='WiFi (192.168.0.10:35000)')
        btn.bind(on_release=lambda btn: self.bt_dropdown.select(btn.text))
        self.bt_dropdown.add_widget(btn)
        porte = ports.items()
        for name, address in porte:
            if mod_globals.opt_port == name:
                mod_globals.opt_dev_address = address
            btn = MyButton(text=name + '>' + address, font_size=fs)
            btn.bind(on_release=lambda btn: self.bt_dropdown.select(btn.text))
            self.bt_dropdown.add_widget(btn)
        self.mainbutton = MyButton(text='')
        self.mainbutton.bind(on_release=self.bt_dropdown.open)
        self.bt_dropdown.bind(on_select=lambda instance, x: setattr(self.mainbutton, 'text', x))
        self.bt_dropdown.select(mod_globals.opt_port)
        glay.add_widget(label1)
        glay.add_widget(self.mainbutton)
        return glay

    def lang_app(self):
        glay = MyGridLayout(cols=2, padding=(fs/3), height=(fs * 4), size_hint=(1, None))
        label = MyLabel(text=LANG.l_lang, font_size=fs*2, halign='left', size_hint=(1, None), height=(fs * 3))
        self.bt_lang = DropDown(height=(fs * 2))
        lang = {'English':'en','France':'fr','Русский':'ru',}
        for v, k in lang.items():
            but = MyButton(text=v, id=k, font_size=fs*2)
            but.bind(on_release=self.select_lang)
            self.bt_lang.add_widget(but)
        self.button_app = MyButton(text=LANG.b_lang, font_size=fs*2)
        self.button_app.bind(on_release=self.bt_lang.open)
        self.bt_lang.bind(on_select=lambda instance, x: setattr(self.button_app, 'text', x))
        glay.add_widget(label)
        glay.add_widget(self.button_app)
        return glay

    def select_lang(self, dt=None):
        mod_globals.opt_lang = dt.id
        self.settings.save()
        try:
            self.stop()
        except:
            pass
    
    def make_input_toggle(self, str1, iText, state):
        toggle = ToggleButton(state=state, text=str1, font_size=fs*1.5, size_hint=(1, None), height=(fs * 3))
        self.button[str1] = toggle
        ti = TextInput(text=iText, multiline=False, font_size=(fs*1.5), padding=[fs/2, fs/2])
        self.textInput[str1] = ti
        glay = MyGridLayout(cols=2, padding=(fs/3), height=(fs * 4), size_hint=(1, None))
        glay.add_widget(toggle)
        glay.add_widget(ti)
        return glay
    
    def make_input(self, str1, iText):
        label1 = MyLabel(text=str1, halign='left', size_hint=(1.5, None), height=(fs * 3))
        ti = TextInput(text=iText, multiline=False, font_size=(fs*1.5), padding=[fs/2, fs/2])
        self.textInput[str1] = ti
        glay = MyGridLayout(cols=2, padding=(fs/3), height=(fs * 4), size_hint=(1, None))
        glay.add_widget(label1)
        glay.add_widget(ti)
        return glay


class MyButton(Button):
    def __init__(self, **kwargs):
        global fs
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
        if 'valign' not in kwargs:
            self.valign = 'middle'
        if 'height' not in kwargs:
            fmn = 1.7
            lines = len(self.text.split('\n'))
            simb = len(self.text) * 2.0 / self.width
            if 1 > simb: simb = 1
            if lines < simb: lines = simb
            if lines < 2: lines = 2
            if lines > 20: lines = 20
            if fs > 20: 
                lines = lines * 1.05
            self.height = fmn * lines * fs * simb
def destroy():
    exit()

def kivyScreenConfig():
    global resizeFont
    Window.bind(on_close=destroy)
    while 1:
        config = PYDDT()
        config.run()
    if not resizeFont:
        return
    resizeFont = False

def main():
    try:
        if not os.path.exists(mod_globals.cache_dir):
            os.makedirs(mod_globals.cache_dir)
        if not os.path.exists(mod_globals.log_dir):
            os.makedirs(mod_globals.log_dir)
        if not os.path.exists(mod_globals.dumps_dir):
            os.makedirs(mod_globals.dumps_dir)
    except:
        print('Dir creation error!')

    kivyScreenConfig()

class MyGridLayout(GridLayout):
    def __init__(self, **kwargs):
        if 'spadding' in kwargs:
            del kwargs ['spadding']
        super(MyGridLayout, self).__init__(**kwargs)
        self.pos_hint={"top": 1, "left": 1}
        
        if 'bgcolor' in kwargs:
            self.bgcolor = kwargs['bgcolor']
        else:
            self.bgcolor =(1, 0, 0, 1)
    def on_size(self, *args):
        if not self.canvas:
            return
        self.canvas.before.clear()
        with self.canvas.before:
            Color(self.bgcolor[0], self.bgcolor[1], self.bgcolor[2], self.bgcolor[3])
            Rectangle(pos=(self.pos[0],self.pos[1]), size=(self.size[0], self.size[1]))

class MyLabel(Label):
    global fs
    def __init__(self, **kwargs):
        if 'bgcolor' in kwargs:
            self.bgcolor = kwargs['bgcolor']
        else:
            self.bgcolor = (0.5, 0.5, 0, 1)
        
        if 'multiline' in kwargs:
            del kwargs ['multiline']
        
        super(MyLabel, self).__init__(**kwargs)
        self.bind(size=self.setter('text_size'))
        if 'halign' not in kwargs:
            self.halign = 'center'
        if 'valign' not in kwargs:
            self.valign = 'middle'
        if 'font_size' not in kwargs:
            self.font_size = fs * 1.8
        if 'size_hint' not in kwargs:
            self.size_hint = (1, None)
        if 'height' not in kwargs:
            fmn = 1.7
            lines = len(self.text.split('\n'))
            simb = len(self.text) / 60
            if lines < simb: lines = simb
            if lines < 7: lines = 5
            if lines > 20: lines = 15
            if 1 > simb: lines = 1.5
            if fs > 20: 
                lines = lines * 1.05
                fmn = 1.5
            self.height = fmn * lines * fs
    
    def on_size(self, *args):
        if not self.canvas:
            return
        self.canvas.before.clear()
        with self.canvas.before:
            Color(self.bgcolor[0], self.bgcolor[1], self.bgcolor[2], self.bgcolor[3])
            Rectangle(pos=self.pos, size=self.size)

if __name__ == '__main__':
    main()