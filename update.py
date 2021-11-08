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

updatefolder = Path(os.environ.get('APPDATA')).joinpath(f".{appname}/.update")
rmtree(updatefolder, ignore_errors=True)

while not update_package:
    update_package = input_path("\nProvide update package file [.zip]:\n",
                                ensure=FILE)
try:
    version = update_package.split('_')[-1].strip('.zip')
except IndexError:
    version = 'unknown'

password = f"{appname}-{version}"

log.warning("\nDo not close this window until success message appears.")
log.warning("Reading and extracting update package. This might take some time...\n")


with zipfile.ZipFile(update_package, mode='r') as zf:
    zf.extractall(updatefolder, pwd=bytes(password, 'utf-8'))

sleep(2)

python_dir_exists = True

if updatefolder.joinpath('arcgis').exists():
    for p in updatefolder.joinpath('arcgis').iterdir():
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

if updatefolder.joinpath('ktima').exists():
    if Path.home().joinpath(f'.{appname}').exists():
        copy_file(src=updatefolder.joinpath('ktima'),
                  dst=Path.home(),
                  save_name=f'.{appname}',
                  ignore=['update.exe'])
    else:
        copy_file(src=updatefolder.joinpath('ktima'),
                  dst=Path.home(),
                  save_name=f'.{appname}')


rmtree(updatefolder, ignore_errors=True)

app_folder = Path.home().joinpath(f'.{appname}')

if app_folder.joinpath('ktima.exe').exists():
    make_shortcut(src=app_folder.joinpath('ktima.exe'),
                  dst=Path.home().joinpath('Desktop'))

if app_folder.joinpath('update.exe').exists():
    make_shortcut(src=app_folder.joinpath('update.exe'),
                  dst=Path.home().joinpath('Desktop'),
                  shortcut_name='update ktima')


log.success(f'\n{appname} was successfully updated to version {version}')
sleep(5)
