# CAN-man-in-the-middle
or better yet, "can-in-the-middle" is system using the TU Truck Cape, a BeagleBone Black, socketCAN and Python3 to inspect and forward CAN network traffic. Particular interest is on J1939 used in heavy trucks. Contributions to this repository are a result of the funded research on heavy vehicle cybersecurity and digital forensics at the University of Tulsa. 

## Setting up the Hardware
The hardware for this project is 100% open. You can purchase every part of the hardware and hand assemble the pieces. The schematic for the Truck Cape or the CAN Man-in-the-middle is shown in the docs folder. There are multiple hardware versions for different form factors and switching functions. All versions use the BeagleBone Black and have 2 CAN channels and 2 J1708 channels. For more details, see the ![docs](docs) folder.

## Accessing the BeagleBone Black

### USB
A mini usb connection has an RNDIS connection for treating the connection like a network. The IP address for the USB connection is 192.168.7.2. However, in Windows 10, the driver for this connection is not install correctly by default. To set up the driver for this, please see this ![guide](http://www.synercontechnologies.com/wp-content/uploads/2018/05/Fixing-RNDIS-Error-on-Windows-10..pdf).

### Ethernet
The BeagleBone Black is setup by default to have a DHCP client to get an IP address. Therefore, a DHCP server is needed for the device to get an IP address.

### Shell Access
SSH is a prefered method to access the operating system. For Windows users, PuTTy is available.

### File Transfer
WinSCP can handle file transfers over a secure connection from a Windows machine.

### Remote Sublime

To edit files using Sublime in on the Beaglebone, there is a package in Sublime Text 3 called RemoteSubl. https://github.com/randy3k/RemoteSubl

http://blog.keyrus.co.uk/editing_files_on_a_remote_server_using_sublime.html

## Setting up the Operating System (ARM Linux)
The project is based on the following image:

http://debian.beagleboard.org/images/bone-debian-9.5-iot-armhf-2018-10-07-4gb.img.xz

Follow the instructions at http://beagleboard.org/static/beaglebone/latest/README.htm

Here are a couple modifications to the instructions:

We assume you are using Windows 7 or Windows 10:
To install this system on the BeagleBone eMMC do the following: 
  1. Decompress the image using 7-zip: https://www.7-zip.org/download.html
  2. Write the image file to an SD card using Win32 Imager: https://sourceforge.net/projects/win32diskimager/files/latest/download
  3. Insert the micro SD card into the BeagleBone Black.
  3. Boot the system while holding down the SD boot button. A USB cable can power the BBB for this. 
  4. Log into the system by using Putty to ssh into 192.168.7.2 (with USB). The user is `debian` and the password is `temppwd`
  4. At the command prompt, type  `sudo nano /boot/uEnv.txt`. You may have to enter the password again.
  5. Uncomment the last existing line so it says: `cmdline=init=/opt/scripts/tools/eMMC/init-eMMC-flasher-v3.sh` 
  6. reboot: `sudo shutdown -r now`
  7. The system will reboot and after a minuite or so, the LEDs will flash back and forth then light up solid when finished (10 minutes or so).
  8. Remove the SD card and press the reset button or cycle power.
  9. Login again and finish creating the environment.

user: debian

password: temppwd

It may be helpful to connect to the Internet through Ethernet. Once the Ethernet is plugged in, you can check an IP address through the USB connection using `ifconfig`. Look for the IP address for eth0.

BBone Black Wireless has not been tested yet.

## Creating the environment.

The baseline is the 4.14.71 Linux Kernel. Verify you have the correct operating system installed. Try the following commands and compare the output.

```
debian@beaglebone:~$ uname -a
Linux beaglebone 4.14.71-ti-r80 #1 SMP PREEMPT Fri Oct 5 23:50:11 UTC 2018 armv7l GNU/Linux
```

```
debian@beaglebone:~$ cat /etc/os-release
PRETTY_NAME="Debian GNU/Linux 9 (stretch)"
NAME="Debian GNU/Linux"
VERSION_ID="9"
VERSION="9 (stretch)"
ID=debian
HOME_URL="https://www.debian.org/"
SUPPORT_URL="https://www.debian.org/support"
BUG_REPORT_URL="https://bugs.debian.org/"
```

```
debian@beaglebone:~$ cat /etc/debian_version
9.5
```

```
debian@beaglebone:~$ cat /etc/dogtag
BeagleBoard.org Debian Image 2018-10-07
```

### Controlling Relays
In the hardware revisions with relays (versions 3 and 4), the configuration of the relay switches enables the MITM to be moved between different networks. 

All relays and LEDs require the 5V0 to be present, which comes from the 12V source. This means if the device is powered with just the USB, the relays won't work.

From the command line:

#### Switch 1
`config-pin P8_39 0`  disconnects J1939 from either side (man-in-the-middle mode).

`config-pin P8_39 1`  connects J1939 (Pins C and D) on the A side to J1939 on the B side (passthrough mode).

#### Switch 2
`config-pin P8_40 0`  connects CAN2 (Pins H and J) on the A side to CAN2 on the B side (passthrough mode).

`config-pin P8_40 1`  disconnects CAN2 from either side (man-in-the-middle mode).

#### Switch 3
`config-pin P8_37 0`  connects the `can1` socket to J1939 (Pins C and D) on the A side.

`config-pin P8_37 1`  connects the `can1` socket to CAN2 (Pins H and J) on the A side.

#### Switch 4
`config-pin P8_42 0` connects J1708 (Pins F and G) on the A side to J1708 (Pins F and G) on the B side.

`config-pin P8_42 1` disconnects J1708 from either side (requires software bridge).

#### Switch 5

`config-pin P8_45 0` connects J1939 (Pins C and D) on the B side to `can0`.

`config-pin P8_45 1` connects CAN2 (Pins H and J) on the B side to `can0`.

#### Switch 6

`config-pin P8_46 0` connects terminating resistors.

`config-pin P8_46 1` connects both beaglebone CAN channels together.


#### LED
`config-pin P8_38 0`  Turns off the board mounted LED.

`config-pin P8_38 1`  Turns on the board mounted LED.

#### Using Python
The `os.system` command enables execution of these commands.

```
debian@beaglebone:~$ python3
Python 3.5.3 (default, Jan 19 2017, 14:11:04)
[GCC 6.3.0 20170118] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import os
>>> os.system("config_pin P8_38 1")
```

Or, you can use Adafruit's Python Package:

`sudo apt-get install build-essential python-dev python-pip3 -y`

`sudo pip3 install Adafruit_BBIO`

Example of turning on the LED:
```
debian@beaglebone:~$ python3
Python 3.5.3 (default, Sep 27 2018, 17:25:39)
[GCC 6.3.0 20170516] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import Adafruit_BBIO.GPIO as GPIO
>>> GPIO.setup("P8_38",GPIO.OUT)
>>> GPIO.output("P8_38",GPIO.HIGH)
```

### Enabling Relays and CAN on Boot

`sudo nano /boot/uEnv.txt`

Change the following block by uncommenting some lines shown below:

```
###Disable auto loading of virtual capes (emmc/video/wireless/adc)
#disable_uboot_overlay_emmc=1
disable_uboot_overlay_video=1
disable_uboot_overlay_audio=1
#disable_uboot_overlay_wireless=1
disable_uboot_overlay_adc=1
```
Exit and save the file.

Restart `sudo shutdown -r now`

We need to load the GPIO settings into the system to use them.

`sudo nano /etc/rc.local`

Copy the rc.local file contents into this editor. The rc.local file runs on boot. It uses the `config-pin` command to set the pins to the appropriate function (like GPIO or CAN)

`sudo chmod 755 rc.local`

Restart the system. `sudo shutdown -r now`.

`sudo sh rc.local` should produce a series of relay clicks and leave the LED on.


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
Python 3.5 is installed at this version of Linux. To test this
```
debian@beaglebone:~$ python3
Python 3.5.3 (default, Jan 19 2017, 14:11:04)
[GCC 6.3.0 20170118] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>>
```
Python comes with sockets and socketCAN, which is available by default.
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
There is a noticeable delay when starting this program. The output is as follows when connected to a brake controller and a Smart Sensor Simulator 2:
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
Plug in the CAN-in-the-middle to the Smart Sensor Simulator 2 and turn on the keyswitch of the SSS2 (press the knob for 2 seconds).
Log into the BeagleBone and run `candump any` to see a stream of CAN traffic. Both green and red leds on the SSS2should be on.

Try `cangen can0` to see the green led ficker. Try `cangen can1` to see the red led flicker. 

### Using CAN Utils as a bridge

`candump -s 2 -B can0 can1&`

`candump -s 2 -B can1 can0&`

will bridge the two networks.

To make this into a service that runs on boot add these two lines to the `/etc/rc.local` file. 

can-utils is installed in `/usr/bin`
```
$ which candump
/usr/bin/candump
```

### Remote Access
Interfacing with CAN over Ethernet has been done in this project.

https://github.com/Heavy-Vehicle-Networking-At-U-Tulsa/TruckCapeProjects/tree/master/SocketCAN

In this project, CAN data is efficiently transferred over TCP for remote interaction.