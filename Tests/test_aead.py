# Copyright (c) 2011, Yubico AB
# All rights reserved.

import sys
import unittest
import pyhsm

import test_common

class TestAEAD(test_common.YHSM_TestCase):

    def setUp(self):
        test_common.YHSM_TestCase.setUp(self)
        self.nonce = "4d4d4d4d4d4d".decode('hex')
        self.key = "A" * 16
        self.uid = '\x4d\x01\x4d\x02\x4d\x03'
        self.secret = pyhsm.aead_cmd.YHSM_YubiKeySecret(self.key, self.uid)

    def test_aead_cmd_class(self):
        """ Test YHSM_AEAD_Cmd class. """
        this = pyhsm.aead_cmd.YHSM_AEAD_Cmd(None, None)
        # test repr method
        self.assertEquals(str, type(str(this)))
        this.executed = True
        self.assertEquals(str, type(str(this)))

    def test_generate_aead_simple(self):
        """ Test generate_aead_simple. """
        # Enabled flags 00000002 = YSM_AEAD_GENERATE
        # HSM> < keyload - Load key data now using flags 00000002. Press ESC to quit
        # 00000002 - stored ok
        key_handle = 2
        aead = self.hsm.generate_aead_simple(self.nonce, key_handle, self.secret)

        self.assertEqual(aead.nonce, self.nonce)
        self.assertEqual(aead.key_handle, key_handle)

        # test repr method
        self.assertEquals(str, type(str(aead)))

    def test_generate_aead_simple_validates(self):
        """ Test decrypt_cmp of generate_aead_simple result. """
        # To successfully decrypt the AEAD we have to generate and decrypt
        # with the same key handle. Key handle 0x2000 has all flags set.
        kh_gen = 0x2000
        kh_val = 0x2000

        aead = self.hsm.generate_aead_simple(self.nonce, kh_gen, self.secret)

        # test that the YubiHSM validates the generated AEAD
        # and confirms it contains our secret
        self.assertTrue(self.hsm.validate_aead(self.nonce, kh_val, \
                                                   aead, cleartext = self.secret.pack()))

    def test_generate_aead_random(self):
        """ Test decrypt_cmp of generate_aead_random result. """
        # Enabled flags 00000008 = YSM_RANDOM_AEAD_GENERATE
        # 00000004 - stored ok
        key_handle = 4

        # Test a number of different sizes
        for num_bytes in (1, \
                              pyhsm.defines.KEY_SIZE + pyhsm.defines.UID_SIZE, \
                              pyhsm.defines.YSM_AEAD_MAX_SIZE - pyhsm.defines.YSM_AEAD_MAC_SIZE):
            aead = self.hsm.generate_aead_random(self.nonce, key_handle, num_bytes)
            self.assertEqual(num_bytes + pyhsm.defines.YSM_AEAD_MAC_SIZE, len(aead.data))

        # test num_bytes we expect to fail
        for num_bytes in (0, \
                              pyhsm.defines.YSM_AEAD_MAX_SIZE - pyhsm.defines.YSM_AEAD_MAC_SIZE + 1, \
                              255):
            try:
                res = self.hsm.generate_aead_random(self.nonce, key_handle, num_bytes)
                self.fail("Expected YSM_INVALID_PARAMETER, got %s" % (res))
            except pyhsm.exception.YHSM_CommandFailed, e:
                self.assertEquals(e.status, pyhsm.defines.YSM_INVALID_PARAMETER)

    def test_who_can_generate_random(self):
        """ Test what key handles can generate a random AEAD. """
        # Enabled flags 00000008 = YSM_RANDOM_AEAD_GENERATE
        # 00000004 - stored ok
        this = lambda kh: self.hsm.generate_aead_random(self.nonce, kh, 10)
        self.who_can(this, expected = [0x04])

    def test_who_can_generate_simple(self):
        """ Test what key handles can generate a simple AEAD. """
        # Enabled flags 00000002 = YSM_AEAD_GENERATE
        # 00000002 - stored ok
        this = lambda kh: self.hsm.generate_aead_simple(self.nonce, kh, self.secret)
        self.who_can(this, expected = [0x02])

    def test_who_can_validate(self):
        """ Test what key handles can validate an AEAD. """
        # Enabled flags 00000002 = YSM_AEAD_GENERATE
        # 00000002 - stored ok
        gen_kh = 2
        # Enabled flags 00000010 = YSM_AEAD_DECRYPT_CMP
        # 00000005 - stored ok
        aead = self.hsm.generate_aead_simple(self.nonce, gen_kh, self.secret)

        this = lambda kh: self.hsm.validate_aead(self.nonce, kh, \
                                                     aead, cleartext = self.secret.pack())
        self.who_can(this, expected = [0x05])
