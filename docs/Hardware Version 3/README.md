# Truck Cape Revision 3 MITM Hardware
This readme describes how to build the Man-in-the-middle.

## Errata
In hardware version 3 MITM, there are a few issues to address:
  1. The relays need to be mounted on the bottom of the board to get the correct polarity of voltage across the coil. This has been fixed in MITM rev 4.
  2. The pin going to P8_41 needs to be clipped off the header or removed. This is for switch 3. A jumper wire needs to be routed from pin3 of U2 to P8_37, which is GPIO78.
  3. The LED1 net was not connected. Add a jumper wire from P8_38 (GPIO79) to U2 Pin 7. 