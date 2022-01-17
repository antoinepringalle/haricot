#!/bin/bash

cd /tmp || exit
wget --progress=dot:mega -O rpi3-hotspot.zip "https://github.com/poppy-project/rpi3-hotspot/archive/master.zip"
unzip -q rpi3-hotspot.zip
mv rpi3-hotspot-* rpi3-hotspot
cd rpi3-hotspot || exit
./install.sh
cd /tmp || exit
rm -f rpi3-hotspot.zip
rm -rf rpi3-hotspot

# reads the hotspot credentials from the file config.txt
# and saves the values hotspot_ssid and hotspot_password
# in the variables ssid and password

cd /home/pi/haricots || exit
function read_hotspot_credentials() {
  ssid=$(grep "ssid=" "./config.txt" | cut -d "=" -f 2)
  password=$(grep "password=" "./config.txt" | cut -d "=" -f 2)
}

read_hotspot_credentials
echo "ssid: $ssid"
echo "password: $password"

tee /boot/hotspot.txt <<EOF
ssid=$ssid
passphrase=$password
EOF
