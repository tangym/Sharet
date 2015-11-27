# -- encoding: utf-8 --
# author: tym
# date: 2015-11-25

import hashlib
import random
import json
import os
import sys
import getopt
import time

from tinydb import TinyDB, Query


with open('Sharet.conf') as f:
    config = json.load(f)
    
if 'external_config' in config:
    if os.path.isfile(config['external_config']):
        with open(config['external_config']) as f:
            external_config = json.load(f)
            for key in external_config:
                config[key] = external_config[key]

try:
    opts, args = getopt.getopt(sys.argv[1:], "s:", ["share=",])
except getopt.GetoptError as err:
    print(err)
    print('Error: no such option')
    sys.exit(1)
    
for o, a in opts:
        if o in ('-s', '--output'):
            config['share_dir'] = a
        else:
            assert False, "unhandled option"

config['upload_dir'] = os.path.join(config['share_dir'], 'temp')

if not os.path.exists(config['upload_dir']):
    os.mkdir(config['upload_dir'])
elif not os.path.isdir(config['upload_dir']):
    print('Error: cannot create upload directory')
    sys.exit(1)
if not os.path.exists(config['share_dir']):
    os.mkdir(config['share_dir'])
elif not os.path.isdir(config['share_dir']):
    print('Error: cannot create share directory')
    sys.exit(1)



db = TinyDB(config['database'], indent=1)
File = Query()

def md5(fpath):
    hash = hashlib.md5()
    with open(fpath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
    return hash.digest()


def byte_to_hex(byte_code):
    return ''.join('{:02x}'.format(x) for x in byte_code).upper()


def route(byte_code, length=4):
    length = 1 if length < 1 else int(length)
    length = len(byte_code) * 8 if length > len(byte_code) * 8 else length

    step = len(byte_code) * 8 // length
    shift = random.randint(0, len(byte_code) * 8)

    def get_bits(bias):
        bias = bias % (len(byte_code) * 8)
        index =  (bias // 8)
        bias -= index * 8
        bits = 0

        bits += (byte_code[index] & (0xf8 >> bias))
        # use 5 digits
        next_bias = 5 - (8 - bias)
        if next_bias > 0:
            bits = bits << next_bias
            bits += (byte_code[(index + 1) % len(byte_code)] >> (8 - next_bias))
        return bits

    shorten_bytes = [get_bits(i * step + shift) for i in range(length)]

    def bytes_to_string(shorten_bytes):
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_'
        shorten_chars = ''

        for byte in shorten_bytes:
            index = byte & 0x1f
            shorten_chars += chars[index]
        return shorten_chars

    return bytes_to_string(shorten_bytes)


# scan share directory.
flist = filter(lambda file: os.path.isfile(os.path.join(config['share_dir'], 
                                                        file)), 
               os.listdir(config['share_dir']))
files = {byte_to_hex(md5((os.path.join(config['share_dir'], fname)))): fname 
         for fname in flist if fname != os.path.basename(config['database'])}

# remove records of which the file does not exist in share directory
for file in db.all():
    if file['md5'] in files:
        db.update({'name': files[file['md5']]}, File.md5==file['md5'])
    else:
        db.remove(File.md5==file['md5'])

# move files in share directory to upload directory if not recorded
for file in files:
    if not db.contains(File.md5==file):
        os.rename(os.path.join(config['share_dir'], files[file]),
                  os.path.join(config['upload_dir'], files[file]))

# record files in upload directory and move to share direcory
def upload(fname=None):
    if fname:
        if os.path.isfile(os.path.join(config['upload_dir'], fname)):
            file = {}
            fmd5 = md5(os.path.join(config['upload_dir'], fname))
            file['md5'] = byte_to_hex(fmd5)
            
            if db.contains(File.md5==file['md5']):
                os.remove(os.path.join(config['upload_dir'], fname))
                return db.get(File.md5==file['md5'])['route']
            
            file['name'] = '%s-%s' % (file['md5'][:config['prefix_length']], fname)
            file['route'] = route(fmd5)
            file['upload_time'] = time.strftime('%Y-%m-%d %H:%M:%S', 
                                                time.localtime(time.time()))

            retry = 0
            while db.contains(File.route==file['route']) and retry < 5:
                file['route'] = route(fmd5)
                retry += 1
            if not db.contains(File.route==file['route']):
                db.insert(file)
                os.rename(os.path.join(config['upload_dir'], fname),
                          os.path.join(config['share_dir'], file['name']))
                return file['route']
            else:
                print('Error: route conflict')
                sys.exit(1)
        else: 
            print('Error: upload file does not exist')
            sys.exit(1)
    else:
        routes = []
        flist = os.listdir(config['upload_dir'])
        for fname in flist:
            froute = upload(fname)
            print(fname, froute)
            routes += [froute]
        return routes

upload()


def download(route):
    file = db.get(File.route==route)
    # print(route, file)
    if file:
        db.update({'download_time': time.strftime('%Y-%m-%d %H:%M:%S', 
                                                  time.localtime(time.time()))}, 
                  File.route==route)
        return file['name']
    else:
        return None
