#Embedded file name: /build/PyCLIP/android/app/mod_zip.py
import os
import re
import glob
import pickle
import zipfile
import mod_globals

ARCHIVE_FILE = 'DDT2000data.zip'
ZIPARCHIVE = None

def get_zip():
    global ARCHIVE_FILE
    global ZIPARCHIVE
    if ZIPARCHIVE is not None:
        return ZIPARCHIVE
    arh_list = sorted(glob.glob(os.path.join(mod_globals.user_data_dir, 'DDT2000data*.zip')), reverse=True)
    if len(arh_list):
        ARCHIVE_FILE = arh_list[0]
    else:
        arh_list = sorted(glob.glob(os.path.join('./', 'DDT2000data*.zip')), reverse=True)
        if len(arh_list):
            ARCHIVE_FILE = arh_list[0]
    if not os.path.exists(ARCHIVE_FILE):
        return
    mod_globals.db_archive_file = ARCHIVE_FILE
    mod_globals.ddt_arc = zipfile.ZipFile(ARCHIVE_FILE, mode='r')
    ZIPARCHIVE = mod_globals.ddt_arc

def get_file_list_from_ddt( pattern ):
    file_list = mod_globals.ddt_arc.namelist()
    regex = re.compile(pattern)
    return list(filter(regex.search, file_list))

def file_in_ddt( pattern ):
    file_list = mod_globals.ddt_arc.namelist()
    if '(' in pattern:
        pattern = pattern.replace('(','\(')
    if ')' in pattern:
        pattern = pattern.replace(')', '\)')
    regex = re.compile(pattern)
    li = list(filter(regex.search, file_list))
    return len(li)

def get_file_content(filename, zf=None):
    if not zf:
        zf = get_zip()
    return zf.read(filename)

def path_in_ddt( pattern ):
    file_list = mod_globals.ddt_arc.namelist()
    regex = re.compile(pattern)
    li = list(filter(regex.search, file_list))
    if len(li)>0:
        return True
    else:
        return False

def get_file_from_ddt( filename ):
    return mod_globals.ddt_arc.open(filename, 'r')

def extract_from_ddt_to_cache( filename ):
    targ_file = os.path.join(mod_globals.cache_dir, filename)
    try:
        source = mod_globals.ddt_arc.open(filename)
        if not os.path.exists(os.path.dirname(targ_file)):
            os.makedirs(os.path.dirname(targ_file))
        target = open(targ_file, "wb")
        with source, target:
            shutil.copyfileobj(source, target)
        return targ_file
    except:
        return False

if __name__ == '__main__':
    exit()