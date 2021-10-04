#!/usr/bin/env python3

import datetime
import json
import zmq

__version__ = "0.2.0"
verbose = False


def main():
    print('zvdl2json', __version__)
    context = zmq.Context()
    s = context.socket(zmq.SUB)
    binding = 'tcp://*:5555'
    s.bind(binding)
    print(datetime.datetime.now(), 'ZMQ listening at:', binding)
    s.setsockopt_string(zmq.SUBSCRIBE, '')

    while True:
        data = s.recv_json()
        if verbose:
            print(json.dumps(data, indent=4))

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

            # Send this via UDP to feed.acars.io
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


if __name__ == "__main__":
    main()
