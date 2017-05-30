# -*- coding: utf-8 -*-

import unittest
from bnfparsing.parser import ParserBase
from bnfparsing.common import digit_run
from bnfparsing.whitespace import ignore
from bnfparsing.treeview import TreeView
from bnfparsing.exceptions import *


GRAMMAR = """
programme   := if_stmt "then" expression
if_stmt     := "if" digit_run cmp digit_run
cmp         := "!=" | "=="| ">" | "<"
expression  := sum_plus expression | sum
sum_plus    := digit_run operation
operation   := "+" | "-" | "/" | "*"
sum         := digit_run operation digit_run
"""

class SampleParser(ParserBase):

    def __init__(self):
        """ A simple parser for a section of a programme. """
        super(SampleParser, self).__init__(ws_handler=ignore)
        # add common rules
        self.from_function(digit_run, ws_handling=True)
        # add grammar
        self.grammar(GRAMMAR)


class TestTreeview(unittest.TestCase):

    def setUp(self):
        """ Add a parser to the test case. """
        self.parser = SampleParser()

    def test_make_treeview(self):
        """ Generate a TreeView. """
        self.parser.parse('if 23 > 45 then 4 + 5 + 6', main='programme')

    def tearDown(self):
        """ Remove the parser. """
        del self.parser

