cat <<EOF >no-rtl.conf
blacklist dvb_usb_rtl28xxu
blacklist rtl2832
blacklist rtl2830
EOF
sudo mv no-rtl.conf /etc/modprobe.d/

sudo apt-get install git cmake libusb-1.0-0-dev build-essential

git clone git://git.osmocom.org/rtl-sdr.git
cd rtl-sdr
mkdir build
cd build
cmake ../ -DDETACH_KERNEL_DRIVER=ON -DINSTALL_UDEV_RULES=ON
make
make install
ldconfig
cd ~
cp /usr/src/rtl-sdr/rtl-sdr.rules /etc/udev/rules.d/
reboot