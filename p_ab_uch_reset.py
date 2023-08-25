from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from mod_ddt import MyLabel
from kivy.uix.textinput import TextInput
import mod_globals

fs = mod_globals.fontSize

def calc_crc(vin=None):
    VIN=vin.encode("hex")
    VININT=unhexlify(VIN)

    crc16 = crcmod.predefined.Crc('x-25')
    crc16.update(VININT)
    crcle = crc16.hexdigest()
    # Seems that computed CRC is returned in little endian way
    # Convert it to big endian
    return crcle[2:4] + crcle[0:2]

class Virginizer():
    def __init__(self, ecu, title, info, check_req, check_status, check_status_val1, check_status_val2, check_status_val3, reset_req, reset_code, code, start_req, start_send, start_code, start_req_fa, start_send_fa, start_code_fa, txt=None, test=None, Vin=None):
        super(Virginizer, self).__init__()
        global LANG
        self.check_req = check_req
        self.check_status = check_status
        self.check_status_val1 = check_status_val1
        self.check_status_val2 = check_status_val2
        self.check_status_val3 = check_status_val3
        self.reset_req = reset_req
        self.reset_code = reset_code
        self.code = code
        self.start_req = start_req
        self.start_send = start_send
        self.start_code = start_code
        self.start_req_fa = start_req_fa
        self.start_send_fa = start_send_fa
        self.start_code_fa = start_code_fa
        self.txt = txt
        self.test = test
        self.Vin = Vin
        if mod_globals.opt_lang == 'ru':
            import lang_ru as LANG
        elif mod_globals.opt_lang == 'en':
            import lang_en as LANG
        else:
            import lang_fr as LANG
        self.ecu = ecu
        self.Window_size = mod_globals.windows_size
        
        grid = GridLayout(cols=1, padding=15, spacing=15, size_hint=(1, 1))
        infos2 = MyLabel(text=info, size_hint=(1, 1), bgcolor=(1, 0, 0, 1))
        self.butt_check = Button(text='Check ACU Virgin', size_hint=(1, 1), on_press=lambda x:self.check_virgin_status())
        self.butt_virg = Button(text='Virginize ACU', size_hint=(1, 1), on_press=lambda x:self.reset_ecu())
        btn_close = Button(text=LANG.b_close, size_hint=(1, 1))
        self.status_check = MyLabel(text='Waiting', size_hint=(1, 1), bgcolor=(0, 0.5, 0.5, 1))
        self.vin_read = MyLabel(text='VIN - READ: ', size_hint=(1, 1), bgcolor=(0, 0.5, 0.5, 1))
        self.vin_input = TextInput(text='', halign="center", multiline=True, readonly=True, size_hint=(1, 1))
        self.vin_write = MyLabel(text='VIN - WRITE', size_hint=(1, 1), bgcolor=(0, 0.5, 0.5, 1))
        self.vin_output = TextInput(text='', multiline=True, size_hint=(1, 1))
        self.butt_vin_write = Button(text='Write VIN', size_hint=(1, 1), disabled = True, on_press=lambda x:self.write_vin())
        self.vin_read.font_size = self.vin_read.height
        self.vin_output.font_size = self.vin_output.height//2
        self.vin_input.font_size = self.vin_input.height//2
        self.vin_write.font_size = self.vin_write.height
        if self.txt == 1 or self.txt == 2:
            self.butt_check.txt = 'Check UCH Virgin'
            self.butt_virg.txt = 'Virginize UCH'
            self.butt_virg.disabled = True
        grid.add_widget(infos2)
        grid.add_widget(self.butt_check)
        grid.add_widget(self.status_check)
        grid.add_widget(self.butt_virg)
        if self.Vin:
            self.butt_check.text = 'BLANK STATUS and VIN READ'
            grid.add_widget(self.vin_read)
            grid.add_widget(self.vin_input)
            grid.add_widget(self.vin_write)
            grid.add_widget(self.vin_output)
            grid.add_widget(self.butt_vin_write)
        grid.add_widget(btn_close)
        popup = Popup(title=title, title_size=fs*1.5, title_align='center', content=grid, size=(self.Window_size[0], self.Window_size[1]), size_hint=(None, None), auto_dismiss=True)
        popup.open()
        btn_close.bind(on_press=popup.dismiss)

    def read_vin(self):
        vin_read_request = self.ecu.requests[u'RDBLI - VIN']
        vin_values = vin_read_request.send_request({}, self.ecu, "61 81 68 69 70 65 65 65 65 65 65 65 65 65 65 65 65 65 66 00 00")
        self.vin_input.text = vin_values[u'VIN']

    def write_vin(self):
        try:
            vin = str(self.vin_output.text().toAscii()).upper()
            self.vin_output.text = vin
        except:
            self.status_check.text = "<font color='red'>VIN - INVALID</font>"
            return

        if len(vin) != 17:
            self.status_check.text = "<font color='res'>VIN - BAD LENGTH</font>"
            return

        crc = calc_crc(vin).decode('hex')
        self.start_diag_session()
        vin_wrtie_request = self.ecu.requests[u'WDBLI - VIN']
        write_response = vin_wrtie_request.send_request({u'VIN': vin, u'CRC VIN': crc}, self.ecu)
        if write_response is None:
            self.status_check.text = "<font color='orange'>VIN WRITE FAILED</font>"
            return

        self.status_check.text = "<font color='green'>VIN WRITE OK</font>"


    def start_diag_session_fa(self):
        sds_request = self.ecu.requests[self.start_req_fa]
        send_fa = {}
        if self.start_send_fa:
            send_fa = {self.start_send_fa: self.start_code_fa}
        sds_stream = " ".join(sds_request.build_data_stream(send_fa, self.ecu.datas))
        """if mod_globals.opt_demo:
            self.status_check.text = str("SdSFA stream  "+ sds_stream + '\n')
            return
        else:
            self.status_check.text = ''"""
        self.ecu.elm.start_session_can(sds_stream)

    def start_diag_session(self):
        sds_request = self.ecu.requests[self.start_req]
        if self.start_send:
            send = {self.start_send: self.start_code}
        else:
            send = {}
        sds_stream = " ".join(sds_request.build_data_stream(send, self.ecu.datas))
        """if mod_globals.opt_demo:
            self.status_check.text = str("SdS stream " + sds_stream + '\n')
            return
        else:
            self.status_check.text = ''"""
        self.ecu.elm.start_session_can(sds_stream)

    def check_virgin_status(self):
        self.start_diag_session()
        self.read_vin()
        check_request = self.ecu.requests[self.check_req]
        testR = ''
        if self.test == 1:
            testR = '62 02 04 00 00 00 00 00 00 00 00 00 00 00 00'
        if self.test == 2:
            testR = '62 01 64 00 00 00 00 00 00 00 00 00 00 00 00'
        if self.test == 3:
            testR = '62 01 64 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00'
        check_request_values = check_request.send_request({}, self.ecu, testR)
        if check_request_values is not None:
            if self.check_status in check_request_values:
                value = check_request_values[self.check_status]
                if value == self.check_status_val1:
                    self.status_check.bgcolor = (1,0,0,1)
                    if self.txt == 1:
                        self.butt_virg.disabled = True
                        self.status_check.text = 'UCH virgin'
                    elif self.txt == 2:
                        self.butt_virg.disabled = True
                        self.status_check.text = 'EPS not operational'
                    else:
                        self.status_check.text = 'CRASH DETECTED'
                elif value == self.check_status_val2:
                    if self.txt == 2:
                        self.butt_virg.disabled = True
                        self.status_check.text = 'EPS virgin'
                    else:
                        self.status_check.text = 'NO CRASH DETECTED'
                elif value == self.check_status_val3:
                    if self.txt == 1:
                        self.butt_virg.disabled = False
                        self.status_check.text = 'UCH coded'
                    elif self.txt == 2:
                        self.butt_virg.disabled = False
                        self.status_check.text = 'EPS coded'
                else:
                    self.status_check.bgcolor = (0,1,0,1)
                    if self.txt == 1:
                        self.butt_virg.disabled = False
                        self.status_check.text = 'UCH coded'
                    elif self.txt == 2:
                        self.butt_virg.disabled = False
                        self.status_check.text = 'EPS coded'
                    else:
                        self.status_check.text = 'NO CRASH DETECTED'
        else:
            self.status_check.text = 'UNEXPECTED RESPONSE'

    def reset_ecu(self):
        if self.start_req_fa:
            self.start_diag_session_fa()
        else:
            self.start_diag_session()
        reset_request = self.ecu.requests[self.reset_req]
        if self.reset_code:
            send = {self.reset_code: self.code}
        else:
            send = {}
        request_response = reset_request.send_request(send, self.ecu)
        if request_response.values() != 'None' or request_response is not None:
            self.status_check.text = 'CLEAR EXECUTED'
            self.status_check.bgcolor = (0,1,0,1)
        else:
            self.status_check.text = 'CLEAR FAILED'
            self.status_check.bgcolor = (1,0,0,1)