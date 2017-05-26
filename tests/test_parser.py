
import unittest
from bnfparsing.parser import *

class TestParser(unittest.TestCase):

    def test_rule_addition(self):
        parser = ParserBase()
        parser.new_rule('hello', "hello")
        self.assertEqual(list(parser.rules.keys()), ['hello'])

    def test_literal(self):
        parser = ParserBase()
        parser.new_rule('hello', "hello")
        parser.parse('hell', main=True)
