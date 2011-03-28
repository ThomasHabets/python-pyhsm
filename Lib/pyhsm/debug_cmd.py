"""
implementations of debugging commands to execute on a YubiHSM

"""
# Copyright (c) 2011, Yubico AB
# All rights reserved.

import struct
import defines

__all__ = [
    # constants
    # functions
    # classes
    'YHSM_Cmd_Monitor_Exit',
]

from cmd import YHSM_Cmd

class YHSM_Cmd_Monitor_Exit(YHSM_Cmd):
    """
    Send magics to stick in debug mode, and get it to exit to configuration mode again.
    """
    def __init__(self, stick, payload=''):
        #define YHSM_MONITOR_EXIT        0x7f    // Exit to monitor (no response sent)
        #define YHSM_MONITOR_EXIT_MAGIC  0xbaadbeef
        #typedef struct {
        #  uint32_t magic;                     // Magic number for trigger
        #  uint32_t magicInv;                  // 1st complement of magic
        #} YHSM_MONITOR_EXIT_REQ;

        packed = struct.pack('<II', 0xbaadbeef, 0xffffffff - 0xbaadbeef)
        YHSM_Cmd.__init__(self, stick, defines.YHSM_MONITOR_EXIT, packed)
        self.response_length = 0

    def parse_result(self, data):
        return data == ''