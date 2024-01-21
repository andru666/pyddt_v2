#!/usr/bin/env python
import os as sysos
import pickle
ns = {'ns0': 'http://www-diag.renault.com/2002/ECU', 'ns1': 'http://www-diag.renault.com/2002/screens'}
opt_debug = True
debug_file = None
opt_port = ""
savedEcus = ''
opt_ecu = ''
opt_ecuid = ""
opt_ecuAddr = ""
opt_protocol = ""
opt_speed = 38400
opt_rate = 38400
opt_dev_address = ''
opt_car = ""
opt_log = ""
opt_ecuid_on = False
opt_demo = False
opt_scan = False
opt_csv = False
opt_csv_only = False
opt_csv_human = False
opt_usrkey = ""
opt_verbose = False
opt_cmd = True
opt_ddt = False
opt_si = False
opt_cfc0 = True
opt_n1c = False
opt_dev = False
opt_devses = '1086'
opt_exp = False
opt_dump = False
opt_can2 = False
opt_stn = False
opt_perform = False
state_scan = False
currentDDTscreen = None
ext_cur_DTC = "000000"
os = ""
language_dict = {}
opt_lang = 'en'
bt_dev = ''
ecu_root = ''
user_data_dir = "./"

ddt_arc = ""
ddtroot = ".."
db_archive_file = None
cache_dir = "./cache/"
crash_dir = "./crashs/"

log_dir = "./logs/"
dumps_dir = "./dumps/"
csv_dir = './csv/'
fontSize = 20
screen_orient = False

dumpName = ""
savedCAR = ''
opt_caf = False
opt_ddtxml = ""
opt_sd = False
opt_obdlink = False
opt_minordtc = False

none_val = "None"

vin = ""
windows_size = 600, 800
doc_server_proc = None

list_name = {'ABS-VDC_29b': 'ABS-VDC_29b', 'WBCB': 'Wireless Charger Base Station', 'PIU CMZ2': 'PIU Cabin master Z2', 'DCM Nissan': 'Data Communication Module Nissan', 'DCM Renault': 'Data Communication Module', 'EPS': 'Electric Power Steering', 'Tachometer': 'Tachometer', 'SIB': 'Secured Interface Box', 'PDCM': 'Passenger Door Control module', 'MIU': 'Multimedia Interface Unit', 'Steering Wheel Switch': 'Steering Wheel Switch Pad ', 'Fuel System CMG4': 'Fuel System Control Modul 4th Generation', 'FRRAD': 'Laser radar for Adaptive Cruise Control System', 'BCB-OBC_29b': 'Battery Charger Block_29bits', 'Touchpad, Telephone Key pad': 'Touchpad, Telephone Key Pad ', 'Renault RemoteEntry': 'Intelligent KEY', 'SCO_29b': 'Signal Converter Unit', 'ECM-eVTC': 'ECM-eVTC', 'UPC-EMM': 'USM', 'GW': 'Gateway', 'LIB 12V': 'LIB', 'Injection Nissan': 'ECM - NISSAN', 'SCU': 'Shift By Wire', 'HeadUnit': 'Headunit ', 'SCCM': 'SCCM', 'INSULATOR': 'CAN1-CAN2 Gateway', 'VXU': 'VehicleToVehicle Unit', 'BSW': 'Blind Spot Warning', 'SVT': 'Stolen Vehicle Tracker', 'FCAM': 'Front camera', 'PIU Rright': 'PIU Rear Right', 'BEV - SRVM': 'Bird Eye View - Smart Rear View Mirror', 'S-GW': 'Security Gateway', 'IPA': 'Intelligent Parking Assist', 'UBP': 'Uncoupled Brake Pedal', 'LBC2_29b': 'Lithium Battery Controller 2_29bits', '4WD': '4 wheels Drive', 'SOW Front Right': 'Side Obstacle Warning Front Right', 'MemoSeatPassenger - LDCM': 'Memo Seat passenger-Left Door Control module', 'E-ACT-EBA_29b': 'E-ACT-EBA_29b_29bits', '4WS': '4 wheels Steering', 'Superviseur-DCDC_29b': 'Supervisor-DCDC_29bits', 'CAN2': 'Secondary CAN network', 'TDB': 'Meter Cluster', 'APB': 'Automatic Parking Brake', 'HFM': 'Hand Free Module', 'DMC': 'Drive Monitor Camera ', 'DLOCK': 'Diff Lock Control System', 'UDM_29b': 'Urea dosing Control Module_29bits', 'HVAC 2': 'Air Conditioning', 'GBA': 'Gear Box Actuator', 'ESP-Sub': 'EPS-Sub', 'SCCM_29': 'SCCM_29', 'LBC (HEV)_29b': 'Lithium Battery Controller_29bits', 'ABS-VDC': 'ABS-VDC', 'DMS': 'Driving Modes Selector', 'RSCU': 'RR Seat Master Unit', 'HSPL': 'Hospitality Light ECU', 'HERMES': 'HERMES', 'LKS': 'Lane Keep System', 'EMCU': 'Energy Management Control Unit', 'HUD2': 'Head Up Display (P2)', 'Parking Sonar': 'Parking Sonar', 'Tacograph': 'Tachograph Control Module ', 'TCU': 'Top Control Unit', 'SOW Rear Right': 'Side Obstacle Warning Rear Right', 'Nav2': 'Nav2', 'Nav4': 'Nav4', 'LIDAR': 'Longitudinal Radar', 'HMD': 'Head Up Display', 'SOW Rear Left': 'Side Obstacle Warning Rear Left', 'RIGHT_HEAD_LAMP': 'RIGHT_HEAD_LAMP', 'CGW2': 'Central Gateway 2', 'Common Powertrain': 'Common Powertrain Controller ', 'BSG 48v': 'BSG 48v', 'DDR': 'Diagnostic Data Recorder', 'ASDR': 'Automatic Sliding Door Right', 'ASDL': 'Automatic Sliding Door Left', 'BLE RP': 'Blue tooth ECU Remote Park', 'SB': 'Smart Beam', 'CCGW': 'CCGW', 'ESUS-VADA-AIRSUS': 'Suspension Power Module-Variable Damping', 'Rear View Cam': 'Rear View Camera - Surround View System ', 'AFS': 'Auto FrontLighting System', 'BMS 12V Main LIB': 'BMS 12V Man LIB', 'LBC2': 'Lithium Battery Controller 2', 'CSHV Airbag Vehicle stopped': 'CSHV', 'ANC': 'Active Noise Control unit', 'WCGS': 'Wireless Charger Smartphone', 'Airbag-SRS': 'Airbag-SRS', 'HLS': 'High Beam Lighting System', 'AVM': 'Around View Monitoring System', 'Controlographe': 'Tachograph', 'Accessory Switch Module': 'Accessory Switch Module', 'DOP_RES': 'Remote Starter', 'SSG': 'Separated Starter Generator', 'AFBCU': 'Additional Function Body Control Unit', '(H) EVC': 'Electrical Vehicle Control module', 'ACC': 'ACC', 'CAN Adapter - BAC': 'Network CAN Adapter', 'Additional Heater': 'Heat Controller', 'CHADeMo': 'Charger-Hevc convertor(CCM-CSCM)', 'ELOP': 'ELOP', 'Selective Catalytic Reduction': 'Selective Catalytic Reduction Control Module ', 'BCB': 'Battery Charger Block', 'VCCU': 'Vehicle Charger Controler Unit', 'S-GW4': 'Security Gateway4', 'ATR': 'Active Torque Rod', 'DDCM': 'Driver Door Control module', 'S-GW3': 'Security Gateway3', 'Magic Bumper': 'Magic Bumper', 'Navigation-UCC-ITM': 'Navigation-UCC-ITM', 'SMB': 'Side Magic Bumper', 'PEB': 'Power Electronic Box', 'S-GW2': 'Gateway Z2', 'FCP': 'Front Control Panel', 'PCU Rcar B': 'PCU Rcar Bicore', 'PIU Scabin': 'PIU SubCabin Z3', 'ECM': 'Engine Control Module', 'ODS': 'ODS Module', 'INV-RE1_29b': 'INV-RE1_29bits', 'PCU Rcar R': 'PCU Rcar R7', 'LEFT_HEAD_LAMP': 'LEFT_HEAD_LAMP', 'LNG': 'LNG', 'Emergency Service': 'Hardware for Enhanced Remote   Mobility  Emergency Services ', 'ADP': 'Auto Drive Positioner', 'CLD': 'CLD', 'COMP': 'Compressor', 'PTC AMP': 'Positive Temperature Coefficient heater amplifier', 'TPMS': 'Tyre Pressure Measurement System', 'PBD-PTL': 'Power Back Door-Power Trank LID', 'Speech Controller': 'Speech Controller', 'EVAP_29b': 'EVAP_29bits', 'Step_Up': 'Step_Up', 'HMI Gateway': 'HMI Gateway ', 'EPS (HEV)': 'Electric Power Steering (HEV)', 'Intelligent Bat Sensor': 'Intelligent Battery Sensor ', 'PIU CMZ3': 'PIU Cabin master Z3', 'METER-sub': 'Meter - Sub ECU', 'BMS Master': 'BMS Master', 'LBC (HEV)': 'Lithium Battery Controller', 'SWSP': 'SWSP', 'Central Display Module': 'Central Display Module ', 'Tel': 'TEL', 'SBW': 'Steering by Wire', 'SR': 'Scene Recorder', 'INV-ME_29b': 'INV-ME_29bits', 'SOUND (AMP)': 'SOUND (AMP)', 'Cluster': 'Instrument Cluster ', 'Engineering': 'Engineering module', 'HLL - CLG': 'HLL - CLG', '(H) EVC-HCM-VCM_29b': 'Vehicle Control Module_29bits', 'PIU Rleft': 'PIU Rear Left', 'HD Map': 'HD Map', 'BAT': 'CAN BAT Interface', 'HVSG_29bits': 'HVSG_29bits', 'USM_29': 'USM_29', 'AAM': 'Additionnal Adaptation Module', 'INV-RE2_29b': 'INV-RE2_29b', 'RCP': 'Rear Control Panel', 'AAU': 'Audio Amplifier Unit', 'MC HEV': 'Motor Control (Hybrid Vehicle)', 'WSU': 'Wind Shield Unit', 'CAN': 'Primary CAN network', 'DIU': 'Digital-Display Interface Unit', 'Battery Controller': 'Battery Controller', 'PSB DR': 'Pre-crash seat belt DR', 'Ablade': 'Volet Aerodynamique', 'HVAC': 'Climate Control', 'HLM_LT': 'HLM_LT', 'ADAS-Sub': 'ADAS-sub', 'LBC (EV)': 'Lithium Battery Controller', 'PPS': 'Pedestrian Protection System', 'C Box': 'C Box', 'ST1': 'Steer Control Unit 1', 'ST2': 'Steer Control Unit 2', 'ECM_29': 'Engine Control Module_29bits', 'Central Control Unit': 'Central Control Unit front ', 'UCH': 'Body Control Module', 'BLE VK': 'Blue tooth ECU Virtual Key', 'AT_29b': 'Automatic Gearbox_29bits', 'HFCK': 'Hand Free Car Kit', 'Magic Folding-RDCM': 'Magic Folding-Right Door Control module', 'Charger': 'Battery Charger', 'Alarm': 'Alarm', 'PIU Hleft': 'PIU Hood Left Z3', 'VCM': 'Vehicle Control Module', 'PCU Aurix': 'PCU Aurix', 'ADB-LCU': 'Adaptive driving beam', 'VCR': 'VCR', 'AT': 'Automatic Transmission', 'Audio': 'Audio Unit', 'Steering Column': 'Steering Column Control Module ', 'Transfert Case': 'Transfer Case ', 'VSP': 'Vehicle Sound for Pedestrian', 'IDM-CDM': 'Integrated Dynamics Control Module', 'EBA': 'EBA', 'PSB PS': 'Pre-crash seat belt Passenger', 'PLC-PLGW': 'Power Line connection- Power Line GateWay', 'ADB-R': 'ADB-R', 'HLM_RT': 'HLM_RT', 'ADB-L': 'ADB-L', 'ASBM ': 'ASBM ', 'Superviseur-DCDC': 'Supervisor-DCDC', 'Tuner Box': 'Tuner Box, Digital Audio Broadcasting - NTG5 ', 'UDM': 'Urea dosing Control Module', 'Transpondeur': 'Immobilizer', 'SOW Front Left': 'Side Obstacle Warning Front Left'}

class Settings:
    opt_ecu = ''
    port = ''
    lang = ''
    log = True
    logName = 'log.txt'
    cfc = False
    si = False
    demo = False
    fontSize = 20
    screen_orient = False
    useDump = False
    csv = False
    dev_address = ''
    
    def __init__(self):
        global opt_ecu
        global opt_si
        global opt_log
        global opt_dump
        global fontSize
        global opt_port
        global opt_lang
        global opt_cfc0
        global screen_orient
        global opt_csv
        global opt_dev_address
        self.load()
        opt_ecu = self.opt_ecu
        opt_si = self.si
        opt_log = self.logName
        opt_dump = self.useDump
        fontSize = self.fontSize
        opt_port = self.port
        opt_lang = self.lang
        opt_cfc0 = self.cfc
        screen_orient = self.screen_orient
        opt_csv = self.csv
        opt_dev_address = self.dev_address

    def __del__(self):
        self.save()
        
    def load(self):
        if not sysos.path.isfile(user_data_dir + '/settings.p'):
            self.save()
        try:
            with open(user_data_dir + 'settings.p', 'rb') as f:
                tmp_dict = pickle.load(f)
        except:
            sysos.remove(user_data_dir + '/settings.p')
            self.save()
            with open(user_data_dir + 'settings.p', 'rb') as f:
                tmp_dict = pickle.load(f)
        self.__dict__.update(tmp_dict)        
    
    def save(self):
        self.opt_ecu = opt_ecu
        self.si = opt_si
        self.lang = opt_lang
        self.logName = opt_log
        self.useDump = opt_dump
        self.fontSize = fontSize
        self.port = opt_port
        self.cfc = opt_cfc0
        self.screen_orient = screen_orient
        self.csv = opt_csv
        self.dev_address = opt_dev_address
        with open(user_data_dir + 'settings.p', 'wb') as f:
            pickle.dump(self.__dict__, f)