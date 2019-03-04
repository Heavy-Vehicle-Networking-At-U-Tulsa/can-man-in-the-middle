# Hardware revisions that work with the MITM
There are multiple hardware versions that can work with the man-in-the-middle programming. There are two main differences in the hardware that are delineated by where the network switching takes place. The MITM can be either on the normal CAN bus as a single node or it can be physically separating two different busses. If the MITM is inserted into an existing bus and separates it into two different CAN busses, then the terminating resistors need to be installed. In the first iteration of this, an external hardware box was built to make the connections and add terminating resitors. In subsequent builds, this switching was done using relays. 

## Truck Cape with an External Man-in-the-Middle
The circuit board for a small network splitter is in the folder labeled Hardware Version 2. This includes Altium designer files and a schematic. The connection to this board is done with a DSUB-15 connector. The network switching is done by reqiring the outside connectors.

## MITM v3
This board was designed to be a utility for inserting a man-in-the-middle in any heavy vehicle newtork using a deutsch 9-pin carrying 2 CAN channels and a J1708 channel. The relays on this board are setup to insert the CAN channels on the BeagleBone Black in either of the can channels from the vehicle. The details for the hardware and the errata are contained in the Hardware Version 3 directory.

## MITM v4
The directory labeled Hardware Version 4 includes the source documents for the MITM v4 that includes the fixes needed to make Rev3 MITM functional. This hardware has not been built yet (as of 4 March 2019).