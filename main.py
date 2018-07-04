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

from argparse import ArgumentParser
from libregice import Regice, RegiceClientTest, RegiceOpenOCD
from regicecmd import RegicePrompt

def main(argv):
    parser = ArgumentParser()
    parser.add_argument(
        "--svd",
        help="SVD file that contains registers definition"
    )

    parser.add_argument(
        "--openocd", action='store_true',
        help="Use openocd to connect to target"
    )

    parser.add_argument(
        "--test", action='store_true',
        help="Use a mock as target"
    )

    args = parser.parse_args(argv)
    if args.openocd:
        client = RegiceOpenOCD()
    if args.test:
        client = RegiceClientTest()

    regice = Regice(client)

    if args.svd:
        regice.load_svd(args.svd)

    prompt = RegicePrompt(regice)
    prompt.prompt = 'RegICe> '
    prompt.cmdloop()

if __name__ == "__main__":
    main(sys.argv[1:])
