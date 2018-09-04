#!/usr/bin/env python
# -*- coding: utf-8 -*-

# MIT License
#
# Copyright (c) 2018 BayLibre
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
import unittest

from libregice import Regice, RegiceClientTest
from memtool.memtool import MemtoolPrompt
from regicecommon.helpers import load_svd

class TestRegicePrompt(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        svd = load_svd('test.svd')
        self.regice = Regice(RegiceClientTest(), svd)
        self.memory = self.regice.client.memory
        self.cmd = MemtoolPrompt(self.regice)
        self.cmd.test = True

    def setUp(self):
        self.regice.client.memory_restore()

    def test_quit(self):
        exit, data = self.cmd.onecmd("quit")
        self.assertTrue(exit)

    def test_peripheral(self):
        with self.assertRaises(SyntaxWarning):
            self.cmd.onecmd("peripheral")

    def test_peripheral_read(self):
        expected = self.memory[0x00001234]
        exit, value = self.cmd.onecmd("peripheral TEST1 read TESTA")
        self.assertEqual(value, expected)

        expected = {'A1': 0, 'A2': 1, 'A3': 3}
        exit, value = self.cmd.onecmd("peripheral TEST1 read -v TESTA")
        self.assertEqual(value, expected)

        expected = 3
        exit, value = self.cmd.onecmd("peripheral TEST1 read TESTA.A3")
        self.assertEqual(value, expected)

        with self.assertRaises(SyntaxWarning):
            self.cmd.onecmd("peripheral TEST1 read")

        with self.assertRaises(SyntaxWarning):
            self.cmd.onecmd("peripheral TEST1 read TESTC")

        with self.assertRaises(SyntaxWarning):
            self.cmd.onecmd("peripheral TEST1 read TESTA.A4")

    def test_peripheral_write(self):
        expected = 9
        exit, value = self.cmd.onecmd("peripheral TEST1 write TESTA " + str(expected))
        self.assertEqual(value, expected)

        expected = 3
        exit, value = self.cmd.onecmd("peripheral TEST1 write TESTA.A3 " + str(expected))
        self.assertEqual(value, expected)

        with self.assertRaises(SyntaxWarning):
            self.cmd.onecmd("peripheral TEST1 write")

        with self.assertRaises(SyntaxWarning):
            self.cmd.onecmd("peripheral TEST1 write TESTA")

        with self.assertRaises(SyntaxWarning):
            self.cmd.onecmd("peripheral TEST1 write TESTC 0")

        with self.assertRaises(SyntaxWarning):
            self.cmd.onecmd("peripheral TEST1 write TESTA.A4 0")

    def test_peripheral_dump(self):
        expected = {'TESTA' : self.memory[0x00001234]}
        exit, value = self.cmd.onecmd("peripheral TEST1 dump TESTA")
        self.assertEqual(value, expected)

        expected = {
            'TESTA' : self.memory[0x00001234],
            'TESTB' : self.memory[0x00001238],
        }
        exit, value = self.cmd.onecmd("peripheral TEST1 dump TESTA TESTB")
        self.assertEqual(value, expected)

        exti, value = self.cmd.onecmd("peripheral TEST1 dump")
        self.assertEqual(value, expected)

        expected = {
            'TESTA': {'A1': 0, 'A2': 1, 'A3': 3},
            'TESTB': {'B1': 1, 'B2': 0, 'B3': 0},
        }
        exit, value = self.cmd.onecmd("peripheral TEST1 dump -v")
        self.assertEqual(value, expected)

        expected = {
            'TESTA': {'A1': 0, 'A2': 1, 'A3': 3},
        }
        exit, value = self.cmd.onecmd("peripheral TEST1 dump -v TESTA")
        self.assertEqual(value, expected)

        with self.assertRaises(SyntaxWarning):
            self.cmd.onecmd("peripheral TEST1 dump TESTC")

    def test_peripheral_baseAddress(self):
        exit, value = self.cmd.onecmd("peripheral TEST1 baseAddress")
        self.assertEqual(value, 0x00001234)

        with self.assertRaises(SyntaxWarning):
            self.cmd.onecmd("peripheral TEST4 baseAddress")

    def test_peripherals_list(self):
        expected = ['TEST1', 'TEST2']
        exit, peripherals_list = self.cmd.onecmd("peripherals list")
        self.assertEqual(list(peripherals_list), expected)

        with self.assertRaises(SyntaxWarning):
            self.cmd.onecmd("peripherals")

def run_tests(module):
    return unittest.main(module=module, exit=False).result

if __name__ == '__main__':
    unittest.main()
