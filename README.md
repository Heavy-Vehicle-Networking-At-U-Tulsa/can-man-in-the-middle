# CAN-man-in-the-middle
or better yet, "can-in-the-middle" is system using the TU Truck Cape, a BeagleBone Black, socketCAN and Python3 to inspect and forward CAN network traffic. Particular interest is on J1939 used in heavy trucks.

## Setting up the Hardware
The hardware for this project is 100% open. You can purchase every part of the hardware and and hand assemble the pieces. The schematic for the Truck Cape is in the docs folder.

### Bill of Materials

### Build the TruckCape
A completed truck cape is shown below.

## Setting up the Operating System (ARM Linux)
The project is based on the following image:

http://debian.beagleboard.org/images/bone-debian-9.4-iot-armhf-2018-06-17-4gb.img.xz

Follow the instructions at http://beagleboard.org/static/beaglebone/latest/README.htm

Here are a couple modifications to the instructions:

We assume you are using Windows 7 or Windows 10:
To install this system on the BeagleBone eMMC do the following: 
  1. Decompress the image using 7-zip: https://www.7-zip.org/download.html
  2. Write the image file to an SD card using Win32 Imager: https://sourceforge.net/projects/win32diskimager/files/latest/download
  3. Insert the micro SD card an boot the system while holding the SD button. A USB cable can power the BBB for this.
  4. Log into the system by using Putty to ssh into 192.168.7.2. The user is `debian` and the password is `temppwd`
  4. At the command prompt, type  `sudo nano /boot/uEnv.txt`. You may have to enter the password again.
  5. Uncomment an existing line so it says: `cmdline=init=/opt/scripts/tools/eMMC/init-eMMC-flasher-v3.sh` 
  6. reboot: `sudo shutdown -r now`
  7. The LEDs will flash back and forth then light up solid when finished (10 minutes or so).
  8. Remove the SD card and press the reset button or cycle power.
  9. Login again and finish creating the environment.

user: debian

password: temppwd

It may be helpful to connect to the Internet through Ethernet. Once the Ethernet is plugged in, you can check an IP address through the USB connection using `ifconfig`. Look for the IP address for eth0

BBone Black Wireless has not been tested yet.

### Setting up CAN 

Login to the beaglbone and make the following changes:

Steps to get both CAN channels working:
  1. `git clone https://github.com/RobertCNelson/dtb-rebuilder` 
  2. `cd dtb-rebuilder`
  3. `nano src/arm/am335x-boneblack-custom.dts`
    Uncommment the following lines (Remove the //) and save.
``` 
#include "am335x-peripheral-can0.dtsi"
#include "am335x-bone-pinmux-can0.dtsi"

#include "am335x-peripheral-can1.dtsi"
#include "am335x-bone-pinmux-can1.dtsi"
```
  4. `./dtc-overlay.sh`
  4. `make`
  5. `sudo make install`
  6. `cd /boot`
  7. `sudo nano uEnv.txt`

Edit the uEnv.txt file:
```
sudo nano /boot/uEnv.txt
```
Add the line 
```
dtb=am335x-boneblack-custom.dtb
``` 
near the top of the file.

Change the following block by uncommenting some lines shown below:
```
###Disable auto loading of virtual capes (emmc/video/wireless/adc)
#disable_uboot_overlay_emmc=1
disable_uboot_overlay_video=1
disable_uboot_overlay_audio=1
#disable_uboot_overlay_wireless=1
disable_uboot_overlay_adc=1
```

#### Autostart can0 and can1
To bring up both CAN interfaces at boot change `/etc/network/interfaces` with the following commands

```
sudo nano /etc/network/interfaces
```
Add these lines at the end of the file.
```
allow-hotplug can0
iface can0 can static
    bitrate 250000
    restart-ms 250
 
allow-hotplug can1
iface can1 can static
    bitrate 250000
    restart-ms 250
```

#### Changing CAN bitrates

```
sudo ip link set can1 down
sudo ip link set can1 type can bitrate 500000 restart-ms 200
sudo ip link set can1 up
```

#### Check CAN Statistics
```
ip -details -statistics link show can1
```

### Exceptions for the Forensic Link Adapter
If running on an FLA, turn the dual CAN switch on and make the change available on boot by adding the following script to `/etc/rc.local`

```
sudo nano /etc/rc.local
```
Enter the following lines:
```
#!/bin/sh -e
echo "70" > /sys/class/gpio/export
echo "out" > /sys/class/gpio/gpio70/direction
echo "1" > /sys/class/gpio/gpio70/value
exit 0
```
Save with Control-X, Y, Enter. Then make it executable:
```
sudo chmod 755 /etc/rc.local
sudo shutdown -r now
```

## Testing with an SSS2
Plug in the CAN-in-the-middle to the SSS2 and turn on the keyswitch of the SSS2 (press the knob for 2 seconds).
Log into the beaglbone and run `candump any` to see a stream of CAN traffic. Both green and red leds should be on.

Try `cangen can0` to see the green led ficker. Try `cangen can1` to see the red led flicker. 

### Using CAN Utils as a bridge
`candump -s 2 -B can0 can1&`
`candump -s 2 -B can1 can0&`
will bridge the two networks.
`top -c`
shows
```
top - 12:36:49 up 11 min,  1 user,  load average: 0.09, 0.17, 0.13 Tasks:  77 total,   1 running,  76 sleeping,   0 stopped,   0 zombie
%Cpu(s):  5.4 us, 13.1 sy,  0.0 ni, 76.2 id,  0.0 wa,  0.0 hi,  5.4 si,  0.0 st
KiB Mem:    508524 total,    64504 used,   444020 free,     6712 buffers
KiB Swap:        0 total,        0 used,        0 free.    25868 cached Mem

  PID USER      PR  NI    VIRT    RES    SHR S %CPU %MEM     TIME+ COMMAND
 1159 ubuntu    20   0    1164    344    288 S  8.9  0.1   0:04.78 candump -s 2 -B can1 can0
 1156 ubuntu    20   0    1164    344    288 S  7.0  0.1   0:10.79 candump -s 2 -B can0 can1
 ```

## Writing Programs

The image comes with Python 3.5

Install python-can
```
pip3 install python-can
```

Make something cool in Python!

### Remote Sublime

To edit files using Sublime in on the Beaglebone, there is a package in Sublime Text 3 called RemoteSubl. https://github.com/randy3k/RemoteSubl

http://blog.keyrus.co.uk/editing_files_on_a_remote_server_using_sublime.html


