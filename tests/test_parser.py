# -*- coding: utf-8 -*-

import unittest

from bnfparsing.parser import *
from bnfparsing.token import *
from bnfparsing.exceptions import *

class TestParser(unittest.TestCase):

    def test_rule_addition(self):
        parser = ParserBase()
        parser.new_rule('hello', '"hello"')
        self.assertEqual(list(parser.rules.keys()), ['hello'])

    def test_literal(self):
        parser = ParserBase()
        parser.new_rule('hello', '"hello"', main=True)
        token = parser.parse('hello')
        self.assertTrue(token == 'hello', 
            msg='parse failed for literal'
            )
        with self.assertRaises(NotFoundError, 
                msg='matched literal where none exists'):
            parser.parse('hell')
        with self.assertRaises(IncompleteParseError, 
                msg='consumed more characters than expected'):
            parser.parse('helloo')

    def test_rule_function(self):
        
        def parse_a(string):
            if string[0] == 'a':
                return 'a', string[1:]
            return None, string

        parser = ParserBase()
        parser.from_function(parse_a, name='a', main=True)
        token = parser.parse('a')
        self.assertTrue(token == 'a', msg='parse failed for function')
        with self.assertRaises(NotFoundError,
                msg='matched function where incorrect'):
            parser.parse('b')
        with self.assertRaises(IncompleteParseError,
                msg='consumed more characters than expected'):
            parser.parse('aa')
