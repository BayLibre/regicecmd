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

from cmd import Cmd
from libregice import SVDNotLoaded

# pylint: disable=no-self-use
class MemtoolPromptBase(Cmd):
    """
        A simple class to handle Memtool commands

        This class is derived from Cmd and overrides onecmd and postcmd
        to handle exceptions and test.
    """
    test = False
    def onecmd(self, str):
        """
            Interpret the command

            This is an overriden method that handle exceptions, to not
            stop the script even in the case of error.
            Exception handling could disabled for testing (to check if
            exception have been raised).

            :param str: The string to parse
            :return: A tuple, where the first value is a boolean set to True
                     to exit cmdloop, and the second is data returned by the
                     function called by one cmd.
        """
        if self.test:
            return super().onecmd(str)

        try:
            return super().onecmd(str)
        except SVDNotLoaded:
            print("Please run load_svd <svd_file> before to execute this command")
        except SyntaxWarning as ex:
            print(ex)
        return False, None

    def postcmd(self, stop, _data):
        """
            postcmd method updated to work with the overriden onecmd() method

            :param stop: Set to True if cmdloop() must stop
            :param data: data returned by onecmd() method
            :return: True if cmdloop() must stop
        """
        if stop is None:
            return False
        return stop[0]

class MemtoolPeripheralPrompt(MemtoolPromptBase):
    """
        A class to handle peripheral commands
    """
    def __init__(self, memtool_prompt, peripheral):
        super(MemtoolPeripheralPrompt, self).__init__()
        self.regice = memtool_prompt.regice
        self.test = memtool_prompt.test
        self.peripheral = peripheral

    def get_args(self, line):
        """
            Extract arguments from a string

            This takes a string, split it, and returns the list.
            :param arg: the string tat contains argument
            :return: a list of arguments
        """
        args = line.split(' ')
        if not args:
            return []
        out = []
        for arg in args:
            if not arg:
                continue
            out.append(arg)
        return out

    def test_first_arg(self, args, arg):
        """
            This tests the value of the first argument in list

            This tests if the first argument in the list is equal to arg.
            If so, this return True and remove it from the argument list.

            :param args: A list of argument
            :param arg: The value that must be tested with the first argument
            :return: A tuple, with the first value set to True if the arg match
                     with the first argument of the list, otherwise False.
                     The second value is the list of arguments, minus the first
                     one if arg and matched with it.
        """
        if not args:
            return False, []
        if args[0] == arg:
            return True, args[1:]
        return False, args

    def test_and_get_register(self, arg):
        """
            Test if a register exists, and if so, returns its name

            :param arg: The register name, or the register name '.' the name of field
            :return: The register if it exists, otherwise raise an exception
        """
        register = arg.split('.')[0]
        if not self.regice.register_exist(self.peripheral, register):
            raise SyntaxWarning("Invalid register name")
        return register

    def test_and_get_field(self, arg):
        """
            Test if there is a field name defined, and return it

            :param arg: The name of register '.' the name field
            :return: The name of field, if it has been defined or None
        """
        args = arg.split('.')
        register = args[0]
        if len(args) == 2:
            field = args[1]
            if not self.regice.field_exist(self.peripheral, register, field):
                raise SyntaxWarning("Invalid field name")
            return args[1]
        return None

    def do_return(self, _arg):
        """
            Return from MemtoolPeripheralPrompt to MemtoolPrompt

            There are multiple prompt layers. This provides a way to exit
            the current prompt to come back to parent prompt.

            :param arg: Unused
            :return: (True, None) to stop cmdlooop()
        """
        return True, None

    def do_read(self, arg):
        """
            Read the content of a register or the value of one of its field

            The commnd is read [-v] <register[.field]>, with:
            - register: the name of register
            - field: the name of field to ger
            If '-v' argument is set, then read will display all register's fields

            :param arg: read command arguments
            :return: False, and the value read from register
        """
        args = self.get_args(arg)
        verbose, args = self.test_first_arg(args, "-v")
        if not args:
            raise SyntaxWarning("Expected format is 'read [-v] <register[.field]>'")
        register = self.test_and_get_register(args[0])
        size = self.regice.get_size(self.peripheral, register)
        read_format = "0>{}x".format(size)
        if not verbose:
            field = self.test_and_get_field(args[0])
            if not field:
                value = self.regice.read(self.peripheral, register)
                print("{} = 0x{}".format(register, format(value, read_format)))
            else:
                value = self.regice.read_fields(self.peripheral, register)[field]
                print("{} = 0x{}".format(args[0], format(value, read_format)))
        else:
            value = fields = self.regice.read_fields(self.peripheral, register)
            print(register + ":")
            for field in fields:
                print(" {} = {}".format(field, fields[field]))
        return False, value

    def do_write(self, arg):
        """
            Write a value to a register or one of its fiels

            The command is write <register[.field]> <value> with:
            - register: the name of register to write
            - field: the name of the field to set
            - value: the value to write

            :param arg: write command arguments
            :return: False, and the value read back from register
        """
        args = self.get_args(arg)
        if len(args) < 2 or not args[0] or not args[1]:
            raise SyntaxWarning("Expected format is 'write <register[.field]> <value>'")
        register = self.test_and_get_register(args[0])
        field = self.test_and_get_field(args[0])
        if not field:
            self.regice.write(self.peripheral, register, int(args[1]))
        else:
            fields = self.regice.read_fields(self.peripheral, register)
            fields[field] = args[1]
            self.regice.write_fields(self.peripheral, register, fields)

        return self.do_read(args[0])

    def do_baseAddress(self, _arg):
        """
            Get the base address of peripheral

            :param arg: Unused
            :return: False, and the base address of peripheral
        """
        address = self.regice.get_base_address(self.peripheral)
        print("0x" + format(address, "0>8x"))
        return False, address

    def do_dump(self, arg):
        """
            Read the value of some or all peripheral's register

            The command is dump [-v] [register [register [...]]], with:
            - register: the name of register
            If '-v' argument is set, then it will display all registers's fields.
            If there is no register in argument list, then display all registers.

            :param arg: dump command arguments
            :return: False, and the value read from register

        """
        values = {}
        args = self.get_args(arg)
        verbose, args = self.test_first_arg(args, "-v")
        if not args:
            registers_name = []
        else:
            registers_name = args
        for register in registers_name:
            if not self.regice.register_exist(self.peripheral, register):
                raise SyntaxWarning("Invalid register name " + register)
        registers = self.regice.get_register_list(self.peripheral, registers_name)
        for register in registers:
            if not verbose:
                _exit, values[register] = self.do_read(register)
            else:
                _exit, values[register] = self.do_read("-v " + register)
        return False, values

class MemtoolPrompt(MemtoolPromptBase):
    """
        A class to handle regice commands
    """
    def __init__(self, regice):
        super(MemtoolPrompt, self).__init__()
        self.regice = regice

    def do_peripherals(self, arg):
        """
            Execute peripherals commands

            Command is peripherals list, which lists all the peripherals.
            :param arg: peripherals command arguments
            :return: False, and the list of peripherals
        """
        if not arg or not arg == "list":
            raise SyntaxWarning("Expected format is 'peripherals list'")
        for peripheral in self.regice.get_peripheral_list():
            print(peripheral)
        return False, self.regice.get_peripheral_list()

    def do_peripheral(self, arg):
        """
            Execute a peripheral command

            Most of the time, we just need to debug one peripheral.
            This provides a set of commands that could be executed for
            a specific peripheral.
            The command is peripheral <peripheral_name> [subcommands [args, ...]].
            Executing this command without arguments start a prompt.

            :param arg: peripheral command arguments
            :return: False, and the data return by the subcommands
        """
        args = arg.split(' ', 1)
        if not self.regice.peripheral_exist(args[0]) or not args:
            raise SyntaxWarning("Invalid peripheral")

        cmd = MemtoolPeripheralPrompt(self, args[0])
        cmd.prompt = args[0] + ">"
        if len(args) == 1:
            cmd.cmdloop()
        else:
            return cmd.onecmd(args[1])
        return False, None

    def do_load_svd(self, arg):
        """
            Load or reload a svd file

            :param arg: svd_load command argument (e.g svd file to load)
            :return: False, None
        """
        self.regice.load_svd(arg)
        return False, None

    def do_quit(self, _arg):
        """
            Quit the application

            :return: (True, None) to stop cmdloop
        """
        print("Quitting.")
        return True, None
