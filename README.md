# zvdl2json

This daemon will attempt to receive ZMQ input from [dumpvdl2](https://github.com/szpajder/dumpvdl2/) and do some manipulations.
Right now it attempts to output [vdlm2dec](https://github.com/TLeconte/vdlm2dec) compatible JSON for feeding to [airframes.io](https://airframes.io) and dump some interesting information to CSV files.

## Install

```shell
cd /usr/src
git clone --depth=1 https://github.com/varnav/zvdl2json.git
cd zvdl2json
mkdir /opt/zvdl2json
cp zvdl2json.py /opt/zvdl2json
cp zvdl2json.service /etc/systemd/system/zvdl2json.service
systemctl daemon-reload
```

## Run 

```shell
systemctl start zvdl2json && systemctl status zvdl2json
```

## How to run dumpvdl

Change station ID to your own:

`JD` - your initials  
`KJFK` - nearest airport

```shell
dumpvdl2 --rtlsdr 0 --gain 35 --station-id JD-KJFK-VDL2 --msg-filter all,-avlc_s,-acars_nodata,-gsif,-x25_control,-idrp_keepalive,-esis --output decoded:json:zmq:mode=client,endpoint=tcp://192.168.50.204:5555 136725000 136975000 136875000
```

## Installation of dumpvdl2

```shell
cd /usr/src
git clone --depth=1 https://github.com/szpajder/dumpvdl2.git
cd dumpvdl2
mkdir build
cd build
cmake ../
make
make install
cd ..
cp etc/dumpvdl2.service /etc/systemd/system/
cp etc/dumpvdl2 /etc/default/
systemctl daemon-reload
```

Now edit parameters:

```shell
nano /etc/default/
```

See example on top for options

## See also

https://github.com/mylk/acars-server