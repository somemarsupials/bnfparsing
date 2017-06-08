#!/usr/bin/env python

import os
from setuptools import setup

setup(

    # package information
    name='bnfparsing',
    packages=['bnfparsing'],
    test_suite='tests',
    version='0.1.3',
    description='A BNF parser generator for Python',
    long_description=open('README.rst').read(),

    # author information
    author='Theo Breuer-Weil',
    author_email='theobreuerweil@gmail.com',

    # other information
    url='https://www.github.com/somemarspials/bnfparsing',
    license='GPL-3.0',
    keywords=['parsing', 'bnf']
    
    )

