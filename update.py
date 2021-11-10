# -*- coding: utf-8 -*-
import argparse
import zipfile
from pathlib import Path
from time import sleep
import os
from shutil import rmtree

from at.input import FILE, input_path
from at.logger import log
from at.io.copyfuncs import copy_file
from at.utils import make_shortcut

my_parser = argparse.ArgumentParser()

my_parser.add_argument('--appname', action='store', type=str, default='ktima')
my_parser.add_argument('--package', action='store', type=str, default='')

args = my_parser.parse_args()

appname = args.appname
update_package = args.package

while not appname:
    appname = input("\nProvide appname:\n")

app_folder = Path.home().joinpath(f'.{appname}')
updatefolder = Path(os.environ.get('APPDATA')).joinpath(f".{appname}/.update")
temp_app = updatefolder.joinpath('app')
temp_arcgis = updatefolder.joinpath('arcgis')
desktop = Path.home().joinpath('Desktop')
app_exe = app_folder.joinpath(f'source/{appname}/{appname}.exe')
update_exe = app_folder.joinpath(f'source/{appname}/{appname}.exe')

rmtree(updatefolder, ignore_errors=True)

while not update_package:
    update_package = input_path("\nProvide update package file [.zip]:\n",
                                ensure=FILE)
try:
    version = update_package.split('_')[-1].strip('.zip')
except IndexError:
    version = 'unknown'

log.warning("\nDo not close this window until success message appears.")
log.warning("Reading and extracting update package...\n")

with zipfile.ZipFile(update_package, mode='r') as zf:
    zf.extractall(updatefolder)

sleep(4)

python_dir_exists = True

if temp_arcgis.exists():
    for p in temp_arcgis.iterdir():
        if p.stem == '!Toolboxes':
            if Path("C:/Program Files (x86)/ArcGIS/Desktop10.1").exists():
                _dst = Path.home().joinpath(f'.ktima-ArcGIS')
                copy_file(src=p,
                          dst=_dst)
            else:
                log.warning("ArcGIS toolboxes where not loaded")
        else:
            if Path("C:/Python27/ArcGIS10.1/Lib/site-packages").exists():
                copy_file(src=p,
                          dst="C:/Python27/ArcGIS10.1/Lib/site-packages/ktima",
                          save_name=p.stem)
            else:
                python_dir_exists = False

    if not python_dir_exists:
        log.warning("ArcGIS scripts where not loaded")

if temp_app.exists():
    if app_folder.exists():
        copy_file(src=temp_app,
                  dst=Path.home(),
                  save_name=f'.{appname}',
                  ignore=['update'])
    else:
        copy_file(src=temp_app,
                  dst=Path.home(),
                  save_name=f'.{appname}')

rmtree(updatefolder, ignore_errors=True)

if app_exe.exists():
    make_shortcut(src=app_exe, dst=desktop)

if update_exe.exists():
    make_shortcut(src=update_exe,
                  dst=desktop,
                  shortcut_name=f'update {appname}')


log.success(f'\n{appname} was successfully updated to version {version}')
sleep(4)
