#!/usr/bin/env python3

import datetime
import json
import zmq
import csv
import os

context = zmq.Context()
socket = context.socket(zmq.SUB)
binding = 'tcp://*:5555'
socket.bind(binding)
print(datetime.datetime.now(), 'ZMQ listening at:', binding)
socket.setsockopt_string(zmq.SUBSCRIBE, '')

# Get homedir
from pathlib import Path

homedir = str(Path.home()) + os.path.sep
print(datetime.datetime.now(), 'Dumping data to:', homedir)

while True:
    string = socket.recv_string()
    print(string)
    try:
        data = json.loads(string)
        # {"timestamp":1543675375.78301,"channel":2,"freq":136.875,"icao":4221787,"toaddr":2499139,"mode":"2","label":"_d","block_id":"5","ack":"E","tail":"G-GATL","flight":"BA030T","msgno":"S57A"}
        # {"timestamp":1543675377.651469,"channel":3,"freq":136.975,"icao":4921892,"toaddr":1087690,"mode":"2","label":"H2","block_id":"5","ack":"!","tail":"HB-JXK","flight":"DS51QH","msgno":"M69E","text":"33297M517308091G    "}
        flat = {
            'timestamp': float(str(data['vdl2']['t']['sec']) + '.' + str(data['vdl2']['t']['usec'])),
            'channel': 0,
            'freq': float(data['vdl2']['freq']) / 1000000,
            'icao': int(data['vdl2']['avlc']['src']['addr'], 16),
            'toaddr': int(data['vdl2']['avlc']['dst']['addr'], 16)
        }

        if 'acars' in data['vdl2']['avlc']:
            if len(data['vdl2']['avlc']['acars']['msg_text']) < 1:
                continue
            if data['vdl2']['avlc']['acars']['err'] == 'true' or data['vdl2']['avlc']['acars']['crc_ok'] == 'false':
                print('ACARS data error')
                continue
            flat['mode'] = int(data['vdl2']['avlc']['acars']['mode'])
            flat['label'] = data['vdl2']['avlc']['acars']['label']
            flat['block_id'] = data['vdl2']['avlc']['acars']['blk_id']
            flat['ack'] = data['vdl2']['avlc']['acars']['ack']
            flat['tail'] = data['vdl2']['avlc']['acars']['reg']
            flat['flight'] = data['vdl2']['avlc']['acars']['flight']
            flat['msgno'] = data['vdl2']['avlc']['acars']['msg_num']
            flat['text'] = data['vdl2']['avlc']['acars']['msg_text']

        print(json.dumps(flat, indent=2))
    except ValueError as err:
        print("Conversion error:", err)
    except KeyError as err:
        print("Conversion error:", err)

    # Dump all non-empty ACARS messages to CSV
    if 'acars' in data['vdl2']['avlc']:
        filename = homedir + datetime.datetime.now().strftime("%Y-%m-%d_%H") + '_messages.json'
        with open(filename, 'a', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow([data['vdl2']['t']['sec'], data['vdl2']['avlc']['acars']['flight'], data['vdl2']['avlc']['acars']['msg_text']])

    # Look for interesting things in ACARS

    import re

    if 'acars' in data['vdl2']['avlc']:

        # regex = r'.'
        # if bool(re.search(regex, data['vdl2']['avlc']['acars']['msg_text'])):
        #     print('Possible flight plan!')
        #     print(data['vdl2']['avlc']['acars']['msg_text'])
        # filename = homedir + datetime.datetime.now().strftime("%Y-%m-%d_%H") + '_messages.txt'
        # with open(filename, 'a', encoding='utf-8') as f:
        #     f.write(data['vdl2']['avlc']['acars']['msg_text'] + "\n")

        regex = r'.AT1.'
        # FANS - AT1 – CPDLC – aircraft controller directions or response from pilot (can be input or output)
        if bool(re.search(regex, data['vdl2']['avlc']['acars']['msg_text'])):
            print('AT1 message')
            filename = homedir + datetime.datetime.now().strftime("%Y-%m-%d_%H") + 'at1.txt'
            with open(filename, 'a', encoding='utf-8') as f:
                f.write(data['vdl2']['avlc']['acars']['msg_text'] + "\n")

        regex = r'.ADS.'
        # ADS - ADS-C position report
        if bool(re.search(regex, data['vdl2']['avlc']['acars']['msg_text'])):
            print('ADS message')
            filename = homedir + datetime.datetime.now().strftime("%Y-%m-%d_%H") + 'ads.txt'
            with open(filename, 'a', encoding='utf-8') as f:
                f.write(data['vdl2']['avlc']['acars']['msg_text'] + "\n")

        # Dump interesting ACARS labels
        # https://www.universal-radio.com/catalog/decoders/acarsweb.pdf
        regex = r'00 | 7A | A7 | B7 | C\d | M\d | Q.'
        if bool(re.search(regex, data['vdl2']['avlc']['acars']['label'])):
            print(data['vdl2']['avlc']['acars']['msg_text'])
            filename = homedir + datetime.datetime.now().strftime("%Y-%m-%d_%H") + '_labels.json'
            with open(filename, 'a', encoding='utf-8') as f:
                f.write(string + "\n")

        regex = r'[S,N] \d\d\.\d\d [W,E] \d\d\d\.\d\d | FPO\/\d\d | [N,S]\d\d\d\d.\d,[W,E]\d\d\d\d\d.\d | POSN\d'
        if bool(re.search(regex, data['vdl2']['avlc']['acars']['msg_text'])):
            print('Coordinates found')
            print(data['vdl2']['avlc']['acars']['msg_text'])
            filename = homedir + datetime.datetime.now().strftime("%Y-%m-%d_%H") + '_coordinates.json'
            with open(filename, 'a', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow([data['vdl2']['t']['sec'], data['vdl2']['avlc']['acars']['flight'], data['vdl2']['avlc']['acars']['msg_text']])
            # Save flightnumber, coordinates and altitude
            filename = homedir + datetime.datetime.now().strftime("%Y-%m-%d_%H") + '_ac_positions.json'
            with open(filename, 'a', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                lat = data['vdl2']['avlc']['acars']['msg_text']
                # writer.writerow([data['vdl2']['avlc']['acars']['flight'], lat, lon, alt])
