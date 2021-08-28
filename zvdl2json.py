#!/usr/bin/env python3

import csv
import datetime
import json
import os
import traceback
from pathlib import Path
from sty import fg

import zmq

__version__ = "0.1.0"
verbose = False
watch_regex = 'ACCIDENT|COCKPIT|COMPUTER|CABIN|CAPT|COLLISION|CAUTION|DISPATCH|DIVERT|DIVERSION|DIV|DRUG|EMERGENCY|FAILED|FIRE|GUESS|HELP|IPHONE|IPAD|IFE|INCIDENT|INFORM|KNOW|KEEPING|LASER|LOOK|MASK|MARSHALL|MEDICAL|OXYGEN|ODD|PILOT|PAX|PLZ|PLEASE|POLICE|PHONE|RIDE|RELEASE|REPORTED|RETRACTING|ROUTING|RESET|RETURN|SHIP|SMOKE|SHIP|SICK|SUGGEST|THREAT|THE|TAPS|TRAFFIC|USB|VOMIT|WHAT|WHY|WINDOW|WEATHER|WRN|WOULD|FAULT'

os.system("")

def bell():
    if os.name == 'nt':
        import winsound
        winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)


def main():
    print('zvdl2json', __version__)
    context = zmq.Context()
    s = context.socket(zmq.SUB)
    binding = 'tcp://*:5555'
    s.bind(binding)
    print(datetime.datetime.now(), 'ZMQ listening at:', binding)
    s.setsockopt_string(zmq.SUBSCRIBE, '')

    # Get workdir
    workdir = Path.home() / 'zvdl2json'
    Path(workdir).mkdir(parents=True, exist_ok=True)
    print(datetime.datetime.now(), 'Dumping data to:', workdir)

    while True:
        data = s.recv_json()
        if verbose:
            print(json.dumps(data, indent=4))

        # Save everything
        filename = datetime.datetime.utcnow().strftime("%Y-%m-%d") + '_all.json'
        with open(workdir / filename, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data) + "\n")

        # Now we'll remap ZMQ input from dumpvdl2 to vdlm2dec compatible JSON, example:
        # {"timestamp":1630081049.174413,"station_id":"EV-KPTK0-VDL2","channel":0,"freq":136.650,"icao":10871946,"toaddr":1127706,"is_response":0,"is_onground":0,"mode":"2","label":"H1","block_id":"3","ack":"!","tail":"N479WN","flight":"WN6197","msgno":"D09A","text":"#DFB76401\r\n02E27KMSPKBWI\r\nN42395W08427716173898M054263024G000X210030PSZ\r\n"}
        try:
            flat = {
                'timestamp': float(str(data['vdl2']['t']['sec']) + '.' + str(data['vdl2']['t']['usec'])),
                'channel': 1,
                'freq': float(data['vdl2']['freq']) / 1000000,
                'icao': int(data['vdl2']['avlc']['src']['addr'], 16),
                'toaddr': int(data['vdl2']['avlc']['dst']['addr'], 16),
                'is_onground': int((data['vdl2']['avlc']['src']['status'] != 'Airborne')),
                # 'is_response': (data['vdl2']['avlc']['src']['addr']['rsec'] > 1)
            }

            if 'text' in data['vdl2']:
                flat['text'] = data['vdl2']['text']

            if 'acars' in data['vdl2']['avlc']:
                if len(data['vdl2']['avlc']['acars']['msg_text']) < 1:
                    continue
                if data['vdl2']['avlc']['acars']['err'] == 'true' or data['vdl2']['avlc']['acars']['crc_ok'] == 'false':
                    print('ACARS data error')
                    continue
                flat['mode'] = str(data['vdl2']['avlc']['acars']['mode'])
                flat['label'] = data['vdl2']['avlc']['acars']['label']
                flat['block_id'] = data['vdl2']['avlc']['acars']['blk_id']
                flat['ack'] = data['vdl2']['avlc']['acars']['ack']
                flat['tail'] = data['vdl2']['avlc']['acars']['reg']
                flat['flight'] = data['vdl2']['avlc']['acars']['flight']
                flat['msgno'] = data['vdl2']['avlc']['acars']['msg_num']
                flat['text'] = data['vdl2']['avlc']['acars']['msg_text']
            if len(data['vdl2']['station']) > 4:
                flat['station_id'] = data['vdl2']['station']

            # if verbose:
            #     print(json.dumps(flat, indent=2, sort_keys=True))

            # Send this via UDP to airframes.io
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
                sock.sendto(bytes(json.dumps(flat, sort_keys=True), "utf-8"), ('feed.acars.io', 5555))
            except OSError:
                print('Error sending over UDP')

        except ValueError:
            print("Conversion error")
            traceback.print_exc()
        except KeyError:
            print("Conversion error")
            traceback.print_exc()

        # Dump all non-empty ACARS messages to CSV
        if 'acars' in data['vdl2']['avlc']:
            msgtime = datetime.datetime.utcfromtimestamp(data['vdl2']['t']['sec']).isoformat() + 'Z'
            print(msgtime, data['vdl2']['avlc']['acars']['reg'].replace('.', ''), "===>\n", data['vdl2']['avlc']['acars']['msg_text'])
            filename = datetime.datetime.utcnow().strftime("%Y-%m-%d") + '_messages.csv'
            with open(workdir / filename, 'a', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([data['vdl2']['t']['sec'], data['vdl2']['avlc']['acars']['reg'].replace('.', ''), data['vdl2']['avlc']['acars']['msg_text']])

        # Dump all non-empty non-ACARS messages to CSV
        if 'text' in data['vdl2']:
            print(data['vdl2']['reg'], "===>\n", data['vdl2']['text'])
            filename = datetime.datetime.utcnow().strftime("%Y-%m-%d") + '_messages.csv'
            with open(workdir / filename, 'a', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([data['vdl2']['t']['sec'], data['vdl2']['flight'], data['vdl2']['text']])
            # Word watchist
            if bool(re.search(watch_regex, data['vdl2']['text'])):
                print('Interesting information found')
                bell()
                print(fg.yellow + data['vdl2']['text'] + fg.rs)
                filename = datetime.datetime.utcnow().strftime("%Y-%m-%d") + '_interesting.json'
                with open(workdir / filename, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(data) + "\n")

        # Look for interesting things in ACARS

        import re

        if 'acars' in data['vdl2']['avlc']:

            # ADS-C

            try:
                if 'arinc622' in data['vdl2']['avlc']['acars']:
                    if data['vdl2']['avlc']['acars']['arinc622']['msg_type'] == 'adsc_msg':
                        print('ADS-C message detected, saving position')
                        # Reassemble time
                        t = datetime.datetime.utcfromtimestamp(data['vdl2']['t']['sec'])
                        mins = int(int(data['vdl2']['avlc']['acars']['arinc622']['adsc']['tags'][1]['basic_report']['ts_sec']) / 60)
                        ts = t.replace(minute=mins).isoformat() + 'Z'  # ISO time in UTC (Zulu)
                        tail = data['vdl2']['avlc']['acars']['reg'].replace('.', '')
                        lat = data['vdl2']['avlc']['acars']['arinc622']['adsc']['tags'][1]['basic_report']['lat']
                        lon = data['vdl2']['avlc']['acars']['arinc622']['adsc']['tags'][1]['basic_report']['lon']
                        alt = data['vdl2']['avlc']['acars']['arinc622']['adsc']['tags'][1]['basic_report']['alt']
                        filename = datetime.datetime.utcnow().strftime("%Y-%m-%d") + '_positions.csv'
                        with open(workdir / filename, 'a', encoding='utf-8', newline='') as f:
                            writer = csv.writer(f)
                            writer.writerow([ts, tail, lat, lon, alt])

            except KeyError:
                print("ADS-C decode error")
                traceback.print_exc()

            # VDL position

            # try:
            #     if 'xid' in data['vdl2']['avlc']:
            #         if 'ac_location' in data['vdl2']['avlc']['xid']['vdl_params']:
            #             print(colored("VLD position", 'yellow'))
            #             lat = data['vdl2']['avlc']['xid']['vdl_params']['ac_position']['lat']
            #
            #
            #             filename = workdir + datetime.datetime.utcnow().strftime("%Y-%m-%d") + '_adsc.csv'
            #             with open(workdir / filename, 'a', encoding='utf-8') as f:
            #                 writer = csv.writer(f)
            #                 writer.writerow([ts, tail, lat, lon, alt])
            #
            # except KeyError as err:
            #     print("VLD position decode error")
            #     traceback.print_exc()

            # regex = r'.AT1.'
            # # FANS - AT1 – CPDLC – aircraft controller directions or response from pilot (can be input or output)
            # if bool(re.search(regex, data['vdl2']['avlc']['acars']['msg_text'])):
            #     print('AT1 message')
            #     filename = datetime.datetime.utcnow().strftime("%Y-%m-%d") + 'at1.txt'
            #     with open(workdir / filename, 'a', encoding='utf-8') as f:
            #         f.write(data['vdl2']['avlc']['acars']['msg_text'] + "\n")

            # regex = r'.ADS.'
            # # ADS - ADS-C position report
            # if bool(re.search(regex, data['vdl2']['avlc']['acars']['msg_text'])):
            #     print('ADS message')
            #     filename = workdir + datetime.datetime.utcnow().strftime("%Y-%m-%d") + 'ads.txt'
            #     with open(filename, 'a', encoding='utf-8') as f:
            #         f.write(data['vdl2']['avlc']['acars']['msg_text'] + "\n")

            # Dump interesting ACARS labels
            # https://www.universal-radio.com/catalog/decoders/acarsweb.pdf
            regex = r'00|7A|A7|B7|C\d|M\d|Q.'
            if bool(re.search(regex, data['vdl2']['avlc']['acars']['label'])):
                print(data['vdl2']['avlc']['acars']['msg_text'])
                filename = datetime.datetime.utcnow().strftime("%Y-%m-%d") + '_interesting.json'
                with open(workdir / filename, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(data) + "\n")

            # Coordinates search
            regex = r'[S,N] \d\d\.\d{3,4} [W,E] \d\d\d\.\d\d|FPO\/\d\d|[N,S]\d\d\d\d.\d,[W,E]\d\d\d\d\d.\d|POS[N,S]'
            if bool(re.search(regex, data['vdl2']['avlc']['acars']['msg_text'])):
                print('Coordinates found in message')
                # print(data['vdl2']['avlc']['acars']['msg_text'])
                filename = datetime.datetime.utcnow().strftime("%Y-%m-%d") + '_position_messages.json'
                with open(workdir / filename, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(data) + "\n")

            # Word watchist
            if bool(re.search(watch_regex, data['vdl2']['avlc']['acars']['msg_text'])):
                print('Interesting information found')
                bell()
                print(style.YELLOW + data['vdl2']['avlc']['acars']['msg_text'])
                filename = datetime.datetime.utcnow().strftime("%Y-%m-%d") + '_interesting.json'
                with open(workdir / filename, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(data) + "\n")

                # Parse position and save to file
                # filename = datetime.datetime.utcnow().strftime("%Y-%m-%d") + '_other_positions.json'
                # with open(workdir / filename, 'a', encoding='utf-8') as f:
                #     writer = csv.writer(f)
                #     lat = data['vdl2']['avlc']['acars']['msg_text']
                #     writer.writerow([data['vdl2']['avlc']['acars']['reg'], lat, lon, alt])


if __name__ == "__main__":
    main()
