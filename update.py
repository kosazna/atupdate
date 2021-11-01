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

my_parser = argparse.ArgumentParser()

my_parser.add_argument('--appname', action='store', type=str, default='')
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


log.warning("\nThis might take some time. Do not close the console")
log.highlight("Reading and extracting update package\n")

with zipfile.ZipFile(update_package, mode='r') as zf:
    zf.extractall(updatefolder, pwd=bytes(password, 'utf-8'))

sleep(1)

if updatefolder.joinpath('arcgis').exists():
    for p in updatefolder.joinpath('arcgis').iterdir():
        if p.stem == '!Toolboxes':
            copy_file(src=p,
                      dst="C:/Program Files (x86)/ArcGIS/Desktop10.1/Tools",
                      save_name='KT-Tools')
        else:
            copy_file(src=p,
                      dst="C:/Python27/ArcGIS10.1/Lib/site-packages/ktima")

if updatefolder.joinpath('ktima').exists():
    copy_file(src=updatefolder.joinpath('ktima'),
              dst=Path.home(),
              save_name=f'.{appname}')

log.success(f'\n{appname} was successfully updated to version {version}')
sleep(5)
