# -*- coding: utf-8 -*-

import unittest

# package
from bnfparsing.token import Token
from bnfparsing.common import upper, lower, alpha, digit, whitespace


class TestCommon(unittest.TestCase):

    def test_alpha(self):
        """ Test the alpha method """
        match = (Token('alpha', 'a'), '')
        self.assertEqual(alpha('a'), match) 
        match = (None, '1')
        self.assertEqual(alpha('1'), match)

    def test_lower(self):
        """ Test the lower method """
        match = (Token('lower', 'a'), 'b')
        self.assertEqual(lower('ab'), match)
        match = (None, '1')
        self.assertEqual(lower('1'), match)

    def test_upper(self):
        """ Test the upper method """
        match = (Token('upper', 'A'), '')
        self.assertEqual(upper('A'), match)
        match = (None, '1')
        self.assertEqual(upper('1'), match)

    def test_digit(self):
        """ Test the digit method. """
        match = (Token('digit', '1'), '')
        self.assertEqual(digit('1'), match)
        match = (None, 'a')
        self.assertEqual(digit('a'), match)

    def test_whitespace(self):
        """ Test the whitespace method. """
        match = (Token('whitespace', '\t '), 'b')
        self.assertEqual(whitespace('\t b'), match)
        match = (None, '1')
        self.assertEqual(whitespace('1'), match)
