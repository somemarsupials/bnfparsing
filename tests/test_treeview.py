# -*- coding: utf-8 -*-

import unittest
from bnfparsing.parser import ParserBase
from bnfparsing.common import digit
from bnfparsing.whitespace import ignore_spaces
from bnfparsing.treeview import TreeView
from bnfparsing.exceptions import *


GRAMMAR = """
programme   := if_stmt "then" expression
if_stmt     := "if" number cmp number
cmp         := "!=" | "=="| ">" | "<"
number      := digit number | digit
expression  := sum_plus expression | sum
sum_plus    := operation number
operation   := "+" | "-" | "/" | "*"
sum         := number operation number
"""

class SampleParser(ParserBase):

    def __init__(self):
        """ A simple parser for a section of a programme. """
        super(SampleParser, self).__init__(ws_handler=ignore_spaces)
        # add common rules
        self.from_function(digit)
        # add grammar
        self.grammar(GRAMMAR)


class TestTreeview(unittest.TestCase):

    def setUp(self):
        """ Add a parser to the test case. """
        self.parser = SampleParser()

    def test_make_treeview(self):
        """ Generate a TreeView. """
        self.parser.parse('if 23 > 45 then 4 + 5 + 6', 
            debug=True, main='programme'
            )

    def tearDown(self):
        """ Remove the parser. """
        del self.parser

