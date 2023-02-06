#ecufile = "MRSZ_X95_L38_L43_L47_20110505T101858"

from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from mod_ddt import MyLabel
import mod_globals

plugin_name = 'Megane3 AIRBAG Reset'
fs = mod_globals.fontSize

class Virginizer():
    def __init__(self, ecu):
        global LANG
        if mod_globals.opt_lang == 'ru':
            import lang_ru as LANG
        elif mod_globals.opt_lang == 'en':
            import lang_en as LANG
        else:
            import lang_fr as LANG
        super(Virginizer, self).__init__()
        self.ecu = ecu
        self.Window_size = mod_globals.windows_size

        grid = GridLayout(cols=1, padding=15, spacing=15, size_hint=(1, 1))
        infos1 = MyLabel(text='Megane III\nAIRBAG VIRGINIZER', size_hint=(1, 1), bgcolor=(0, 0, 1, 1))
        infos2 = MyLabel(text='THIS PLUGIN WILL UNLOCK AIRBAG CRASH DATA\nGO AWAY IF YOU HAVE NO IDEA OF WHAT IT MEANS', size_hint=(1, 1), bgcolor=(1, 0, 0, 1))
        grid.add_widget(infos1)
        grid.add_widget(infos2)
        butt_check = Button(text='Check ACU Virgin', size_hint=(1, 1), on_press=lambda x:self.check_virgin_status())
        butt_virg = Button(text='Virginize ACU', size_hint=(1, 1), on_press=lambda x:self.reset_ecu())
        grid.add_widget(butt_virg)
        btn_close = Button(text=LANG.b_close, size_hint=(1, 1))
        self.status_check = MyLabel(text='Waiting', size_hint=(1, 1), bgcolor=(0, 0.5, 0.5, 1))
        grid.add_widget(self.status_check)
        grid.add_widget(butt_check)
        grid.add_widget(btn_close)
        popup = Popup(title=plugin_name, title_size=fs*1.5, title_align='center', content=grid, size=(self.Window_size[0], self.Window_size[1]), size_hint=(None, None), auto_dismiss=True)
        popup.open()
        btn_close.bind(on_press=popup.dismiss)

    def start_diag_session_fa(self):
        sds_request = self.ecu.requests[u"Start Diagnostic Session"]

        sds_stream = " ".join(sds_request.build_data_stream({u"Session Name": u"systemSupplierSpecific"}, self.ecu.datas))
        if mod_globals.opt_demo:
            print("SdSFA stream", sds_stream)
            return
        self.ecu.elm.start_session_can(sds_stream)

    def start_diag_session(self):
        sds_request = self.ecu.requests[u"Start Diagnostic Session"]

        sds_stream = " ".join(sds_request.build_data_stream({u"Session Name": u"extendedDiagnosticSession"}, self.ecu.datas))
        if mod_globals.opt_demo:
            print("SdS stream", sds_stream)
            return
        self.ecu.elm.start_session_can(sds_stream)

    def check_virgin_status(self):
        self.status_check.text = 'check_virgin_status'
        self.start_diag_session()
        crash_reset_request = self.ecu.requests['Synthèse état UCE avant crash']
        
        values_dict = crash_reset_request.send_request({}, self.ecu, "62 02 04 00 00 00 00 00 00 00 00 00 00 00 00")
        
        if values_dict is None:
            self.status_check.text = 'UNEXPECTED RESPONSE'
        crash = values_dict['crash détecté']
        
        if crash == u'crash détecté':
            self.status_check.bgcolor = (1,0,0,1)
            self.status_check.text = 'CRASH DETECTED'
        else:
            self.status_check.bgcolor = (0,1,0,1)
            self.status_check.text = 'NO CRASH DETECTED'

    def reset_ecu(self):
        self.start_diag_session_fa()
        reset_request = self.ecu.requests['Reset crash ou accès au mode fournisseur']
        request_response = reset_request.send_request({u"code d'accès pour reset UCE": '27081977'}, self.ecu)
        if request_response.values() != 'None' or request_response is not None:
            self.status_check.text = 'CLEAR EXECUTED'
            self.status_check.bgcolor = (0,1,0,1)
        else:
            self.status_check.text = 'CLEAR FAILED'
            self.status_check.bgcolor = (1,0,0,1)

        
'''
import ecu
import options

_ = options.translator('ddt4all')

plugin_name = _("Megane3 AIRBAG Reset")
category = _("Airbag Tools")
need_hw = True
ecufile = "MRSZ_X95_L38_L43_L47_20110505T101858"

class Virginizer(gui.QDialog):
    def __init__(self):
        super(Virginizer, self).__init__()
        self.airbag_ecu = ecu.Ecu_file(ecufile, True)
        layout = gui.QVBoxLayout()
        infos = gui.QLabel(_("Megane III<br>"
                           "AIRBAG VIRGINIZER<br><font color='red'>THIS PLUGIN WILL UNLOCK AIRBAG CRASH DATA<br>"
                           "GO AWAY IF YOU HAVE NO IDEA OF WHAT IT MEANS</font>"))
        infos.setAlignment(core.Qt.AlignHCenter)
        check_button = gui.QPushButton(_("Check ACU Virgin"))
        self.status_check = gui.QLabel(_("Waiting"))
        self.status_check.setAlignment(core.Qt.AlignHCenter)
        self.virginize_button = gui.QPushButton(_("Virginize ACU"))
        layout.addWidget(infos)
        layout.addWidget(check_button)
        layout.addWidget(self.status_check)
        layout.addWidget(self.virginize_button)
        self.setLayout(layout)
        self.virginize_button.setEnabled(True)
        self.virginize_button.clicked.connect(self.reset_ecu)
        check_button.clicked.connect(self.check_virgin_status)
        self.ecu_connect()


    def start_diag_session_fa(self):
        sds_request = self.airbag_ecu.requests[u"Start Diagnostic Session"]

        sds_stream = " ".join(sds_request.build_data_stream({u"Session Name": u"systemSupplierSpecific"}))
        if options.simulation_mode:
            print("SdSFA stream", sds_stream)
            return
        options.elm.start_session_can(sds_stream)


def plugin_entry():
    v = Virginizer()
    v.exec_()
'''