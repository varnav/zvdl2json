# zvdl2json

This daemon will attempt to receive ZMQ input from [dumpvdl2](https://github.com/szpajder/dumpvdl2/) and do some manipulations.
Right now it attempts to output [vdlm2dec](https://github.com/TLeconte/vdlm2dec) compatible JSON for feeding to [airframes.io](https://airframes.io) and dump some interesting information to CSV files.

## Features

* Works on Windows & Linux, works on Raspberry Pi.
* Read and save [ADS-C](https://code7700.com/surveillance_ads-c.htm) positions to csv file
* Plot those positions on map
* Feed to airframes.io
* Attempt to find and save interesting messages

## Install

```shell
sudo -i
cd /usr/src
git clone https://github.com/varnav/zvdl2json.git
cd zvdl2json
pip3 install -r requirements.txt
mkdir /opt/zvdl2json
cp zvdl2json.py /opt/zvdl2json
chmod +x /opt/zvdl2json/zvdl2json.py
cp zvdl2json.service /etc/systemd/system/zvdl2json.service
systemctl daemon-reload
systemctl enable zvdl2json
```

## Run 

```shell
systemctl start zvdl2json && systemctl status zvdl2json
```

# Update

Run `update-zvdl2json.py`

## How to run dumpvdl

Change station ID to your own:

`JD` - your initials  
`KJFK` - nearest airport

```shell
dumpvdl2 --rtlsdr 0 --station-id JD-KJFK-VDL2 --msg-filter all,-avlc_s,-acars_nodata,-gsif,-x25_control,-idrp_keepalive,-esis --output decoded:json:zmq:mode=client,endpoint=tcp://127.0.0.1:5555 136650000 136700000 136800000 136975000
```

You may use serial of the SDR dongle instead of `0`. Use frequencies depending on region:

```
136.650 USA (ARINC)
136.700 USA (ARINC)
136.800 USA (SITA)
136.725 Europe (ARINC)
136.775 Europe (SITA)
136.825 Europe (ARINC)
136.875 Europe (SITA)
136.975 Worldwide (SITA & ARINC)
```

## Installation of dumpvdl2

```shell
apt update
apt install -y cmake rtl-sdr git cmake libusb-1.0-0-dev libtool librtlsdr-dev build-essential libglib2.0-dev pkg-config librtlsdr-dev libxml2-dev libzmq3-dev python3-zmq libsqlite3-dev sqlite3 
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
```

Now edit parameters:

```shell
nano /etc/default/dumpvdl2
systemctl daemon-reload
systemctl start dumpvdl2 && systemctl status dumpvdl2
```

See example on top for options

## Plot collected positions from CSV

```shell
./ads-c_plot.py ~/zvdl2json/2021-08-28_positions.csv
```

## Note on optimal antenna length

137 MHz means 1/4 antenna must be 521 mm long.

# TODO

* MongoDB or ElasticSearch instead of dumping to text/csv

## See also

https://github.com/mylk/acars-server

https://thebaldgeek.github.io/

https://www.pentestpartners.com/security-blog/introduction-to-acars/

http://www.hoka.it/oldweb/tech_info/systems/acarslabel.htm

https://thebaldgeek.github.io/vhf-vdl2.html

https://github.com/fredclausen/docker-acarshub

https://github.com/aerospaceresearch/CalibrateSDR

https://github.com/projecthorus/radiosonde_auto_rx/
