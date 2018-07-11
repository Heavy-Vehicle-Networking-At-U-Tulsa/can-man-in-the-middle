#!/bin/env python3
import socket
import struct
import os

canformat = '<IB3x8s'

#From https://github.com/torvalds/linux/blob/master/include/uapi/linux/can.h
#special address description flags for the CAN_ID
CAN_EFF_FLAG = 0x80000000 #EFF/SFF is set in the MSB
CAN_RTR_FLAG = 0x40000000 #remote transmission request
CAN_ERR_FLAG = 0x20000000 #error message frame

#valid bits in CAN ID for frame formats
CAN_SFF_MASK = 0x000007FF # /* standard frame format (SFF) */
CAN_EFF_MASK = 0x1FFFFFFF # /* extended frame format (EFF) */
CAN_ERR_MASK = 0x1FFFFFFF # /* omit EFF, RTR, ERR flags */

# 
# Controller Area Network Identifier structure
# 
# bit 0-28 : CAN identifier (11/29 bit)
# bit 29   : error message frame flag (0 = data frame, 1 = error message)
# bit 30   : remote transmission request flag (1 = rtr frame)
# bit 31   : frame format flag (0 = standard 11 bit, 1 = extended 29 bit)
# 

# 
# Controller Area Network Error Message Frame Mask structure
# 
# bit 0-28 : error class mask (see include/linux/can/error.h)
# bit 29-31    : set to zero
# 


# 
# struct can_frame - basic CAN frame structure
# @can_id:  CAN ID of the frame and CAN_*_FLAG flags, see canid_t definition
# @can_dlc: frame payload length in byte (0 .. 8) aka data length code
          # N.B. the DLC field from ISO 11898-1 Chapter 8.4.2.3 has a 1:1
          # mapping of the 'data length code' to the real payload length
# @__pad:   padding
# @__res0:  reserved / padding
# @__res1:  reserved / padding
# @data:    CAN frame payload (up to 8 byte)
# 

# /* particular protocols of the protocol family PF_CAN */
# CAN_RAW     1 /* RAW sockets */
# CAN_BCM     2 /* Broadcast Manager */
# CAN_TP16    3 /* VAG Transport Protocol v1.6 */
# CAN_TP20    4 /* VAG Transport Protocol v2.0 */
# CAN_MCNET   5 /* Bosch MCNet */
# CAN_ISOTP   6 /* ISO 15765-2 Transport Protocol */
# CAN_NPROTO  7


class CanBridge():
    def __init__(self, interface_from, interface_to,bitrate_to=250000,bitrate_from=250000):
        #set CAN bit rates. Must have super user privilages.
        os.system('ip link set {} down'.format(interface_from))
        os.system('ip link set {} type can bitrate {}'.format(interface_from, bitrate_from))
        os.system('ip link set {} up'.format(interface_from))
        os.system('ip link set {} down'.format(interface_to))
        os.system('ip link set {} type can bitrate {}'.format(interface_to, bitrate_to))
        os.system('ip link set {} up'.format(interface_to))

        self.canSocket_to = socket.socket(socket.PF_CAN, 
                                          socket.SOCK_RAW, 
                                          socket.CAN_RAW)
        self.canSocket_from = socket.socket(socket.PF_CAN, 
                                            socket.SOCK_RAW, 
                                            socket.CAN_RAW)
        # Following the RAW Socket Options at
        # https://github.com/torvalds/linux/blob/master/Documentation/networking/can.rst
        # Set receive filters
        # filter passes when <received_can_id> & mask == can_id & mask
        # by setting the mask to zero, all messages pass. 
        can_id = 0
        can_mask = 0
        # Alternatively, to filter out J1939 Cruise Control/Vehicle Speed messages
        # can_id = 0x00FEF100
        # can_mask = 0x00FFFF00 #Just looks at the PGN of 0xFEF1 = 65265
        can_filter = struct.pack('LL',can_id,can_mask)
        
        self.canSocket_to.setsockopt(socket.SOL_CAN_RAW, 
                                     socket.CAN_RAW_FILTER,
                                     can_filter)
        ret_val = self.canSocket_to.getsockopt(socket.SOL_CAN_RAW, socket.CAN_RAW_FILTER)
        print("Socket Option for CAN_RAW_FILTER is set to {}".format(ret_val))
        self.canSocket_from.setsockopt(socket.SOL_CAN_RAW, 
                                     socket.CAN_RAW_FILTER,
                                     can_filter)
        ret_val = self.canSocket_from.getsockopt(socket.SOL_CAN_RAW, socket.CAN_RAW_FILTER)
        print("Socket Option for CAN_RAW_FILTER is set to {}".format(ret_val))
        
        # Set the system to receive every possible error
        can_error_filter = struct.pack('L',CAN_ERR_MASK)
        # Alternatively, we can set specific errors where the errors are enumerated
        # in the defines of /linux/can/error.h
        # can_error_filter = CAN_ERR_TX_TIMEOUT | CAN_ERR_BUSOFF
        self.canSocket_to.setsockopt(socket.SOL_CAN_RAW, 
                                     socket.CAN_RAW_ERR_FILTER,
                                     can_error_filter)
        ret_val = self.canSocket_to.getsockopt(socket.SOL_CAN_RAW, socket.CAN_RAW_ERR_FILTER)
        print("Socket Option for CAN_RAW_ERR_FILTER is set to {}".format(ret_val))
        
        self.canSocket_from.setsockopt(socket.SOL_CAN_RAW, 
                                     socket.CAN_RAW_ERR_FILTER,
                                     can_error_filter)
        ret_val = self.canSocket_from.getsockopt(socket.SOL_CAN_RAW, socket.CAN_RAW_ERR_FILTER)
        print("Socket Option for CAN_RAW_ERR_FILTER is set to {}".format(ret_val))
        
        self.interface_from = interface_from
        self.interface_to = interface_to
        try: 
            self.canSocket_to.bind((interface_to,))
            self.canSocket_from.bind((interface_from,))
        except OSError: 
            print("Could not bind to SocketCAN interfaces")
        #put the sockets in blocking mode.
        self.canSocket_to.settimeout(None)
        self.canSocket_from.settimeout(None)

    def run(self, display=False):
        while True:
            raw_bytes = self.canSocket_from.recv(128)
            try:
                self.canSocket_to.send(raw_bytes)

            except OSError: #Buffer overflow usually from lack of connection.
                if display:
                    print("error writing can.")
                else:
                    pass
            raw_bytes_from = self.canSocket_to.recv(128)
            rawID,DLC,candata = struct.unpack(canformat,raw_bytes_from)
            canID = rawID & 0x1FFFFFFF
            if (rawID & CAN_ERR_FLAG) == CAN_ERR_FLAG:
                print("Found Error Frame.")
                print("RawID: {:08X}, data: {}".format(rawID,candata))

                if canID == 1:
                    print("TX timeout")
                elif canID == 2:
                    print ("Lost arbitration")
                elif canID == 4:
                    print("Controller problems")
                elif canID == 8:
                    print("Protocol violations")
                elif canID == 16:
                    print("Transceiver status") 
                elif canID == 32:
                    print("No Acknkowlegement on transmission")
                elif canID == 64:
                    print("Bus off")
                elif canID == 128:
                    print("{:03X}: Bus error. {}".format(canID,candata))
                elif canID == 0x100:
                    print("Controller restarted")
            elif rawID & CAN_RTR_FLAG == CAN_RTR_FLAG:
                print("Received RTR frame.")
            else:
                #Normal data frame
                if display:   
                    canID = rawID & 0x1FFFFFFF
                    candata_string = " ".join(["{:02X}".format(b) for b in candata])
                    print("{:08X} {}".format(canID, candata_string))

if __name__ == '__main__':
    bridge = CanBridge('can0','can1',bitrate_from=250000,bitrate_to=250000)
    bridge.run()
'''
https://github.com/torvalds/linux/blob/master/include/uapi/linux/can/error.h
/*
 * linux/can/error.h
 *
 * Definitions of the CAN error frame to be filtered and passed to the user.
 *
 * Author: Oliver Hartkopp <oliver.hartkopp@volkswagen.de>
 * Copyright (c) 2002-2007 Volkswagen Group Electronic Research
 * All rights reserved.
 *
 */

#ifndef CAN_ERROR_H
#define CAN_ERROR_H

#define CAN_ERR_DLC 8 /* dlc for error frames */

/* error class (mask) in can_id */
#define CAN_ERR_TX_TIMEOUT   0x00000001U /* TX timeout (by netdevice driver) */
#define CAN_ERR_LOSTARB      0x00000002U /* lost arbitration    / data[0]    */
#define CAN_ERR_CRTL         0x00000004U /* controller problems / data[1]    */
#define CAN_ERR_PROT         0x00000008U /* protocol violations / data[2..3] */
#define CAN_ERR_TRX          0x00000010U /* transceiver status  / data[4]    */
#define CAN_ERR_ACK          0x00000020U /* received no ACK on transmission */
#define CAN_ERR_BUSOFF       0x00000040U /* bus off */
#define CAN_ERR_BUSERROR     0x00000080U /* bus error (may flood!) */
#define CAN_ERR_RESTARTED    0x00000100U /* controller restarted */

/* arbitration lost in bit ... / data[0] */
#define CAN_ERR_LOSTARB_UNSPEC   0x00 /* unspecified */
                      /* else bit number in bitstream */

/* error status of CAN-controller / data[1] */
#define CAN_ERR_CRTL_UNSPEC      0x00 /* unspecified */
#define CAN_ERR_CRTL_RX_OVERFLOW 0x01 /* RX buffer overflow */
#define CAN_ERR_CRTL_TX_OVERFLOW 0x02 /* TX buffer overflow */
#define CAN_ERR_CRTL_RX_WARNING  0x04 /* reached warning level for RX errors */
#define CAN_ERR_CRTL_TX_WARNING  0x08 /* reached warning level for TX errors */
#define CAN_ERR_CRTL_RX_PASSIVE  0x10 /* reached error passive status RX */
#define CAN_ERR_CRTL_TX_PASSIVE  0x20 /* reached error passive status TX */
                      /* (at least one error counter exceeds */
                      /* the protocol-defined level of 127)  */

/* error in CAN protocol (type) / data[2] */
#define CAN_ERR_PROT_UNSPEC      0x00 /* unspecified */
#define CAN_ERR_PROT_BIT         0x01 /* single bit error */
#define CAN_ERR_PROT_FORM        0x02 /* frame format error */
#define CAN_ERR_PROT_STUFF       0x04 /* bit stuffing error */
#define CAN_ERR_PROT_BIT0        0x08 /* unable to send dominant bit */
#define CAN_ERR_PROT_BIT1        0x10 /* unable to send recessive bit */
#define CAN_ERR_PROT_OVERLOAD    0x20 /* bus overload */
#define CAN_ERR_PROT_ACTIVE      0x40 /* active error announcement */
#define CAN_ERR_PROT_TX          0x80 /* error occurred on transmission */

/* error in CAN protocol (location) / data[3] */
#define CAN_ERR_PROT_LOC_UNSPEC  0x00 /* unspecified */
#define CAN_ERR_PROT_LOC_SOF     0x03 /* start of frame */
#define CAN_ERR_PROT_LOC_ID28_21 0x02 /* ID bits 28 - 21 (SFF: 10 - 3) */
#define CAN_ERR_PROT_LOC_ID20_18 0x06 /* ID bits 20 - 18 (SFF: 2 - 0 )*/
#define CAN_ERR_PROT_LOC_SRTR    0x04 /* substitute RTR (SFF: RTR) */
#define CAN_ERR_PROT_LOC_IDE     0x05 /* identifier extension */
#define CAN_ERR_PROT_LOC_ID17_13 0x07 /* ID bits 17-13 */
#define CAN_ERR_PROT_LOC_ID12_05 0x0F /* ID bits 12-5 */
#define CAN_ERR_PROT_LOC_ID04_00 0x0E /* ID bits 4-0 */
#define CAN_ERR_PROT_LOC_RTR     0x0C /* RTR */
#define CAN_ERR_PROT_LOC_RES1    0x0D /* reserved bit 1 */
#define CAN_ERR_PROT_LOC_RES0    0x09 /* reserved bit 0 */
#define CAN_ERR_PROT_LOC_DLC     0x0B /* data length code */
#define CAN_ERR_PROT_LOC_DATA    0x0A /* data section */
#define CAN_ERR_PROT_LOC_CRC_SEQ 0x08 /* CRC sequence */
#define CAN_ERR_PROT_LOC_CRC_DEL 0x18 /* CRC delimiter */
#define CAN_ERR_PROT_LOC_ACK     0x19 /* ACK slot */
#define CAN_ERR_PROT_LOC_ACK_DEL 0x1B /* ACK delimiter */
#define CAN_ERR_PROT_LOC_EOF     0x1A /* end of frame */
#define CAN_ERR_PROT_LOC_INTERM  0x12 /* intermission */

/* error status of CAN-transceiver / data[4] */
/*                                             CANH CANL */
#define CAN_ERR_TRX_UNSPEC             0x00 /* 0000 0000 */
#define CAN_ERR_TRX_CANH_NO_WIRE       0x04 /* 0000 0100 */
#define CAN_ERR_TRX_CANH_SHORT_TO_BAT  0x05 /* 0000 0101 */
#define CAN_ERR_TRX_CANH_SHORT_TO_VCC  0x06 /* 0000 0110 */
#define CAN_ERR_TRX_CANH_SHORT_TO_GND  0x07 /* 0000 0111 */
#define CAN_ERR_TRX_CANL_NO_WIRE       0x40 /* 0100 0000 */
#define CAN_ERR_TRX_CANL_SHORT_TO_BAT  0x50 /* 0101 0000 */
#define CAN_ERR_TRX_CANL_SHORT_TO_VCC  0x60 /* 0110 0000 */
#define CAN_ERR_TRX_CANL_SHORT_TO_GND  0x70 /* 0111 0000 */
#define CAN_ERR_TRX_CANL_SHORT_TO_CANH 0x80 /* 1000 0000 */

/* controller specific additional information / data[5..7] */

#endif /* CAN_ERROR_H */
'''