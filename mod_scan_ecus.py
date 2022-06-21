#!/usr/bin/env python
from xml.dom.minidom import parse
import xml.dom.minidom
import pickle

import mod_db_manager
import mod_elm as m_elm
import sys
import glob
import os
import string

opt_demo = False

families = {'1': '13712',
 '2': '13002',
 '3': '13010',
 '4': '13713',
 '5': '13016',
 '6': '13715',
 '7': '60761',
 '8': '13004',
 '9': '13012',
 '10': '13718',
 '11': '13719',
 '12': '13003',
 '13': '19763',
 '14': '13722',
 '15': '17782',
 '16': '7301',
 '17': '58508',
 '18': '13005',
 '19': '55948',
 '20': '13727',
 '21': '13920',
 '22': '23586',
 '23': '7305',
 '24': '51605',
 '25': '15664',
 '26': '15666',
 '27': '18638',
 '28': '15665',
 '29': '19606',
 '30': '61183',
 '31': '58925',
 '32': '58926',
 '33': '24282',
 '34': '60773',
 '35': '60777',
 '36': '60778',
 '37': '61750',
 '38': '53126',
 '39': '61751',
 '40': '8711',
 '41': '24353',
 '42': '61293',
 '43': '5773',
 '44': '63135',
 '45': 'C3P_73545',
 '46': '61883',
 '47': '58943',
 '48': '61882',
 '49': '62658',
 '50': '13009',
 '51': '30504',
 '52': '13019',
 '53': '31980',
 '54': '31981',
 '55': '13922',
 '56': '13921',
 '57': '62659',
 '58': '62660',
 '59': '62661',
 '60': '11331',
 '61': '11332',
 '62': '9446',
 '63': '55050',
 '64': '62720',
 '65': '29705',
 '66': '29706',
 '67': '62721',
 '68': '62722',
 '69': '62723',
 '70': '57741',
 '72': '8992',
 '73': '61294',
 '74': '62724',
 '76': '11297',
 '77': '56580',
 '78': '61295',
 '79': '60146',
 '80': '51172',
 '81': '51173',
 '86': '57713',
 '87': '60779',
 '88': '63847',
 '89': '63848',
 '90': '4672',
 '91': '51666',
 '92': '53725',
 '93': '55049',
 '94': '56538',
 '95': '56539',
 '96': '56540',
 '97': '56562',
 '98': '57970',
 '99': '58003'} 

def readECUIds( elm ):

    elm.clear_cache()

    StartSession = ''
    DiagVersion = ''
    Supplier = ''
    Version = ''
    Soft = ''
    Std = ''
    VIN = ''
    rsp = ''

    if elm.startSession == '':
        res = elm.request(req='10C0', positive='50', cache=False)

        if res=='' or 'ERROR' in res:
            return StartSession, DiagVersion, Supplier, Version, Soft, Std, VIN

        if res.startswith('50'):
            StartSession = '10C0'
        else:
            res = elm.request(req='1003', positive='50', cache=False)
            if res.startswith('50'):
                StartSession = '1003'
            else:
                res = elm.request(req='10A0', positive='50', cache=False)
                if res.startswith('50'):
                    StartSession = '10A0'
                else:
                    res = elm.request(req='10B0', positive='50', cache=False)
                    if res.startswith('50'):
                        StartSession = '10B0'
    else:
        StartSession = elm.startSession
        res = elm.request(req=elm.startSession, positive='50', cache=False)

    if not res.startswith('50'):
        pass

    IdRsp = elm.request(req='2180', positive='61', cache=False)
    if len(IdRsp) > 59:
        DiagVersion = str(int(IdRsp[21:23], 16))
        Supplier = IdRsp[24:32].replace(' ', '').strip().decode('hex').decode('ASCII', errors='ignore')
        Soft = IdRsp[48:53].strip().replace(' ', '')
        Version = IdRsp[54:59].strip().replace(' ', '')
        if not DiagVersion.isalnum(): DiagVersion = '0'
        if not Supplier.isalnum(): Supplier = '000'
        if not Soft.isalnum(): Soft = '0000'
        if not Version.isalnum(): Version = '0000'

        Std = 'STD_A'

        vinRsp = elm.request(req='2181', positive='61', cache=False)
        if len(vinRsp)>55 and 'NR' not in vinRsp:
            VIN = vinRsp[6:56].strip().replace(' ', '').decode('hex').decode('ASCII', errors='ignore')
    else:
        try:
            IdRsp_F1A0 = elm.request(req='22F1A0', positive='62', cache=False)
            if len(IdRsp_F1A0) > 8 and 'NR' not in IdRsp_F1A0 and 'BUS' not in IdRsp_F1A0:
                DiagVersion = str(int(IdRsp_F1A0[9:11], 16))
            IdRsp_F18A = elm.request(req='22F18A', positive='62', cache=False)
            if len(IdRsp_F18A) > 8 and 'NR' not in IdRsp_F18A and 'BUS' not in IdRsp_F18A:
                Supplier = IdRsp_F18A[9:].strip().replace(' ', '').decode('hex').decode('ASCII', errors='ignore')

            IdRsp_F194 = elm.request(req='22F194', positive='62', cache=False)
            if len(IdRsp_F194) > 8 and 'NR' not in IdRsp_F194 and 'BUS' not in IdRsp_F194:
                Soft = IdRsp_F194[9:].strip().replace(' ', '').decode('hex').decode('ASCII', errors='ignore')
            IdRsp_F195 = elm.request(req='22F195', positive='62', cache=False)
            if len(IdRsp_F195) > 8 and 'NR' not in IdRsp_F195 and 'BUS' not in IdRsp_F195:
                Version = IdRsp_F195[9:].strip().replace(' ', '').decode('hex').decode('ASCII', errors='ignore')

            Std = 'STD_B'
            vinRsp = elm.request(req='22F190', positive='62', cache=False)
            if len(vinRsp) > 58:
                VIN = vinRsp[9:59].strip().replace(' ', '').decode('hex').decode('ASCII', errors='ignore')
        except:
            pass

    return StartSession, DiagVersion, Supplier, Version, Soft, Std, VIN