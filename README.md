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
### Python and CAN
Python 3  is installed at version 3.5 on this image. To test this
```
debian@beaglebone:~$ python3
Python 3.5.3 (default, Jan 19 2017, 14:11:04)
[GCC 6.3.0 20170118] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>>
```
Python comes with sockets and socketCAN is available by default.
You can also install python-can as an interface:
```
python3 -m pip install python-can
```
Building the dependency of `wrapt` failed to build, but the pip command completed.
 
#### Example Program
The following is a basic Python3 program to forward can messages from one socket to another.
```
#!/bin/env python
import socket
import struct

canformat = '<IB3x8s'

class CanBridge():
    def __init__(self, interface_from, interface_to):
        self.interface_from = interface_from
        self.interface_to = interface_to
        self.canSocket_to = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        self.canSocket_from = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        try: 
            self.canSocket_to.bind((self.interface_to,))
            self.canSocket_from.bind((self.interface_from,))
        except OSError: 
            print("Could not bind to interfaces")
        #put the sockets in blocking mode.
        self.canSocket_to.settimeout(None)
        self.canSocket_from.settimeout(None)

    def run(self):
        while True:
            raw_bytes = self.canSocket_from.recv(512)
            try:
                self.canSocket_to.send(raw_bytes)
            except OSError: #Buffer overflow usually from lack of connection.
                pass

            rawID,DLC,candata = struct.unpack(canformat,raw_bytes)
            canID = rawID & 0x1FFFFFFF
            candata_string = " ".join(["{:02X}".format(b) for b in candata])
            print("{:08X} {}".format(canID, candata_string))

if __name__ == '__main__':
    bridge = CanBridge('can1','can0')
    bridge.run()
```
Another simple program using the `python-can` library:
```
#!/bin/env python3
import can

bus = can.interface.Bus(bustype='socketcan', channel='can1', bitrate=250000)
try:
    while True:
        message = bus.recv()
        candata_string = " ".join(["{:02X}".format(b) for b in message.data])
        print("{:08X} {}".format(message.arbitration_id, candata_string))
except KeyboardInterrupt:
    bus.shutdown()
    print("Finished.")
```
There is an noticalble delay when starting this program. The output is as follows when connected to a brake controller and a Smart Sensor Simulator 2:
```
18FEBF0B 00 00 7D 7D 7D 7D FF FF
0CFE6E0B 00 00 00 00 00 00 00 00
0CFE6E0B 00 00 00 00 00 00 00 00
0CFE6E0B 00 00 00 00 00 00 00 00
18FEF10B FF 00 00 FF FF FF FF FF
0CFE6E0B 00 00 00 00 00 00 00 00
18F00131 00 00 00 00 00 00 00 00
18F0010B 00 00 00 00 00 00 00 00
18FEF117 00 00 00 00 00 00 00 00
18FEF128 00 00 00 00 00 00 00 00
18FEF121 00 00 00 00 00 00 00 00
18FEF131 00 00 00 00 00 00 00 00
18E00017 00 00 00 00 00 00 00 00
^CFinished.
```


## Testing with an SSS2
Plug in the CAN-in-the-middle to the SSS2 and turn on the keyswitch of the SSS2 (press the knob for 2 seconds).
Log into the beaglbone and run `candump any` to see a stream of CAN traffic. Both green and red leds should be on.

Try `cangen can0` to see the green led ficker. Try `cangen can1` to see the red led flicker. 

### Using CAN Utils as a bridge
`candump -s 2 -B can0 can1&`
`candump -s 2 -B can1 can0&`
will bridge the two networks.

Can-utils is installed in `/usr/bin`
```
$ which candump
/usr/bin/candump
```

To make this into a service that runs on boot, do the following:


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


