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

from setuptools import setup, find_packages

setup(
    name='RegiceMemtool',
    packages=['memtool'],
    author='Alexandre Bailon',
    author_email='abailon@baylibre.com',
    description='A tool to manipulate SoC or MCU registers for development and debugging purpose.',
    url='https://github.com/BayLibre/regicecmd', 
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 1 - Planning",
        "License :: MIT",
        "Natural Language :: English",
        "Operating System :: GNU/Linux",
        "Programming Language :: Python :: 3.6",
    ],
    install_requires=['LibRegice'],
    dependency_links=[
        'git+https://github.com/BayLibre/libregice.git#egg=LibRegice',
    ],
)

setup(
    name='RegiceMemtoolTest',
    packages=['memtooltest'],
    author='Alexandre Bailon',
    author_email='abailon@baylibre.com',
    description='Test for RegiceMemtool.',
    url='https://github.com/BayLibre/regicecmd',
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 1 - Planning",
        "License :: MIT",
        "Natural Language :: English",
        "Operating System :: GNU/Linux",
        "Programming Language :: Python :: 3.6",
    ],
    install_requires=['RegiceTest', 'RegiceMemtool'],
    dependency_links=[
        'git+https://github.com/BayLibre/regicecmd.git#egg=RegiceMemtool',
        'git+https://github.com/BayLibre/regice-test.git#egg=RegiceTest',
    ],
    entry_points={
        'regice': [
                'run_tests = memtooltest.test:run_tests',
        ]
    },
)
