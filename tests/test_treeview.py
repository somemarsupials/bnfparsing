# -*- coding: utf-8 -*-

import unittest
from bnfparsing.parser import ParserBase
from bnfparsing.common import digit_run
from bnfparsing.whitespace import ignore
from bnfparsing.treeview import TreeView
from bnfparsing.exceptions import *

SIMPLE_GRAMMAR = """
sentence    := object verb object end
end         := "." | "?" | "!"
object      := "Jane" | "Tom" | "Rajesh"
verb        := "liked" | "killed" | "voted for"
"""

GRAMMAR = """
programme   := if_stmt "then" expression
if_stmt     := "if" digit_run cmp digit_run
cmp         := "!=" | "=="| ">" | "<"
expression  := sum_plus expression | sum
sum_plus    := digit_run operation
operation   := "+" | "-" | "/" | "*"
sum         := digit_run operation digit_run
"""


class SampleSimpleParser(ParserBase):

    def __init__(self):
        """ A simple parser for a sentence. """
        super(SampleSimpleParser, self).__init__(ws_handler=ignore)
        # add grammar
        self.grammar(SIMPLE_GRAMMAR, main='sentence')


class SampleParser(ParserBase):

    def __init__(self):
        """ A simple parser for a section of a programme. """
        super(SampleParser, self).__init__(ws_handler=ignore)
        # add common rules
        self.from_function(digit_run, ws_handling=True)
        # add grammar
        self.grammar(GRAMMAR, main='programme')


# sample sentences to be parsed
SIMPLE = 'Jane liked Rajesh .'
SAMPLE = 'if 23 > 45 then 4 + 5 + 6'


class TestTreeview(unittest.TestCase):

    def setUp(self):
        """ Add parsers to the test case. """
        self.simple = SampleSimpleParser()
        self.parser = SampleParser()

    def test_make_treeview(self):
        """ Generate a TreeView. """
        self.parser.parse(SAMPLE)

    def test_tokens(self):
        tv = self.simple.parse(SIMPLE)
        compare = [s.strip() for s in SIMPLE.split()]
        tokens = [t.value() for t in tv.tokens()]
        # test normal tokens method
        self.assertEqual(tokens, compare,
            msg='tokens not generated as expected'
            )
        # test with 'as_str' parameter
        self.assertEqual(tv.tokens(as_str=True), compare,
            msg='tokens not generated as strings as expected'
            )

    def test_find(self):
        """ Test the find method of the TreeView. """
        tv = self.parser.parse(SAMPLE)
        found = tv.find('digit_run', as_str=True)
        numbers = [n for n in SAMPLE.split() if n.isdigit()]

        self.assertEqual(found, numbers, msg='find method failed')

    def test_iter(self):
        """ Test iterating over children as TreeViews. """
        tv = self.parser.parse(SAMPLE)
        for child in tv.iter_treeview():
            self.assertEqual(type(child), TreeView, 
                msg='children are not TreeViews'
                )

    def test_level(self):
        """ Test the level method. """
        tv = self.parser.parse(SAMPLE)
        self.assertEqual(tv.level(0), [tv.root], msg='level 0 failed')
        print(tv.level(2))

    def test_flatten(self):
        """ Test the flatten method. """
        tv = self.parser.parse(SAMPLE)
        tv.flatten()

def tearDown(self):
        """ Remove the parser. """
        del self.parser

