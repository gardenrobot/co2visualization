#!/bin/sh

# change this to your co2 device. Find with `lsusb`.
search_string='Holtek Semiconductor, Inc. USB-zyTemp'


dev_path=$(lsusb | grep "$search_string" | sed 's/Bus \([0-9]\+\) Device \([0-9]\+\).*/\/dev\/bus\/usb\/\1\/\2/')
echo Changing device to $dev_path
sed -i "s,DEVICE=.*,DEVICE=${dev_path}," .env
