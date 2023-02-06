from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from mod_ddt import MyLabel
import mod_globals

fs = mod_globals.fontSize

class Virginizer():
    def __init__(self, ecu, title, info, check_req, check_status, reset_req, reset_code, code, start_req, start_send, start_code, start_code_fa):
        global LANG
        self.check_req = check_req
        self.check_status = check_status
        self.reset_req = reset_req
        self.reset_code = reset_code
        self.code = code
        self.start_req = start_req
        self.start_send = start_send
        self.start_code = start_code
        self.start_code_fa = start_code_fa
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
        infos2 = MyLabel(text=info, size_hint=(1, 1), bgcolor=(1, 0, 0, 1))
        grid.add_widget(infos2)
        butt_check = Button(text='Check ACU Virgin', size_hint=(1, 1), on_press=lambda x:self.check_virgin_status())
        butt_virg = Button(text='Virginize ACU', size_hint=(1, 1), on_press=lambda x:self.reset_ecu())
        grid.add_widget(butt_virg)
        btn_close = Button(text=LANG.b_close, size_hint=(1, 1))
        self.status_check = MyLabel(text='Waiting', size_hint=(1, 1), bgcolor=(0, 0.5, 0.5, 1))
        grid.add_widget(self.status_check)
        grid.add_widget(butt_check)
        grid.add_widget(btn_close)
        popup = Popup(title=title, title_size=fs*1.5, title_align='center', content=grid, size=(self.Window_size[0], self.Window_size[1]), size_hint=(None, None), auto_dismiss=True)
        popup.open()
        btn_close.bind(on_press=popup.dismiss)

    def start_diag_session_fa(self):
        sds_request = self.ecu.requests[self.start_req]

        sds_stream = " ".join(sds_request.build_data_stream({self.start_send: self.start_code_fa}, self.ecu.datas))
        if mod_globals.opt_demo:
            self.status_check.text = str("SdSFA stream  "+ sds_stream + '\n')
            return
        else:
            self.status_check.text = ''
        self.ecu.elm.start_session_can(sds_stream)

    def start_diag_session(self):
        sds_request = self.ecu.requests[self.start_req]
        if self.start_send:
            send = {self.start_send: self.start_code}
        else:
            send = {}
        sds_stream = " ".join(sds_request.build_data_stream(send, self.ecu.datas))
        if mod_globals.opt_demo:
            self.status_check.text = str("SdS stream " + sds_stream + '\n')
            return
        else:
            self.status_check.text = ''
        self.ecu.elm.start_session_can(sds_stream)

    def check_virgin_status(self):
        self.start_diag_session()
        crash_reset_request = self.ecu.requests[self.check_req]
        values_dict = crash_reset_request.send_request({}, self.ecu, "62 02 04 00 00 00 00 00 00 00 00 00 00 00 00")
        if values_dict is not None:
            crash = values_dict[self.check_status]
            if crash == self.check_status:
                self.status_check.bgcolor = (1,0,0,1)
                self.status_check.text += 'CRASH DETECTED'
            else:
                self.status_check.bgcolor = (0,1,0,1)
                self.status_check.text += 'NO CRASH DETECTED'
        else:
            self.status_check.text += 'UNEXPECTED RESPONSE'

    def reset_ecu(self):
        if self.start_code_fa:
            self.start_diag_session_fa()
        else:
            self.start_diag_session()
        reset_request = self.ecu.requests[self.reset_req]
        request_response = reset_request.send_request({self.reset_code: self.code}, self.ecu)
        if request_response.values() != 'None' or request_response is not None:
            self.status_check.text += 'CLEAR EXECUTED'
            self.status_check.bgcolor = (0,1,0,1)
        else:
            self.status_check.text += 'CLEAR FAILED'
            self.status_check.bgcolor = (1,0,0,1)