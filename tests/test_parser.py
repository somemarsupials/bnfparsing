# -*- coding: utf-8 -*-

import unittest

from bnfparsing.parser import ParserBase
from bnfparsing.token import Token
from bnfparsing.exceptions import *

STANDARD = ('hello', 'hello', 'hell', 'helloo')

GRAMMAR = r"""
main := access "www." domain "." locale
access := "https://" | "http://"
domain := letter domain | letter
letter := "a" | "b" | "c"
locale := "com" | "co.uk" | "fr"
"""

GRAMMAR_WS = r"""
main := hello world hello punctuations
hello := "hello" | "hi"
world := "Earth" | "planet"
punctuations := punctuation punctuations | punctuation
punctuation := "?" | "!" | "."
"""

class TestParser(unittest.TestCase):

    def check(self, p, string, match, fail=None, extra=None):
        """ Trial a parser with an input string. Check that it matches
        the match argument, fails on the fail argument and correctly
        reports an IncompleteParseError on the extra argument.
        """
        token = p.parse(string)
        # check that the parse works
        self.assertTrue(token == match, 
            msg='parse failed for literal'
            )
        # check that the parse doesn't work when it shouldn't
        if fail:
            with self.assertRaises(NotFoundError, 
                    msg='matched literal where none exists'):
                p.parse(fail)
        # verify incomplete parse check
        if extra:
            with self.assertRaises(IncompleteParseError, 
                    msg='consumed more characters than expected'):
                p.parse(extra)

    def test_rule_addition(self):
        """ Check that rules can be added to the rule dictionary. """
        p = ParserBase()
        p.new_rule('hello', '"hello"')
        # check that the p has the new rule
        self.assertEqual(list(p.rules.keys()), ['hello'])

    def test_literal(self):
        """ Test a custom rule that involves a literal. """
        p = ParserBase()
        p.new_rule('hello', '"hello"', main=True)
        self.check(p, *STANDARD)

    def test_rule_reference(self):
        """ Test a custom rule that references another rule. """
        p = ParserBase()
        p.new_rule('literal', '"hello"')
        p.new_rule('reference', 'literal')
        self.check(p, *STANDARD)

    def test_bad_rule_reference(self):
        """ Refer to a rule that doesn't exist. """
        p = ParserBase()
        p.new_rule('bad', 'notarule')
        with self.assertRaises(KeyError, 
                msg='non-existent rule did not raise error'):
            p.parse('any text')

    def test_rule_sequence(self):
        """ Test a rule that contains a sequence of tokens. """
        p = ParserBase()
        p.new_rule('hello', '"hel" "lo"')
        self.check(p, *STANDARD)

    def test_long_sequence(self):
        """ Test a longer sequence, using literals and rules. """
        p = ParserBase()
        p.new_rule('ls', '"l"')
        p.new_rule('long', '"h" "e" ls ls "o"', main=True)
        self.check(p, *STANDARD)

    def test_branching(self):
        """ Test a simple 'or' example. """
        p = ParserBase()
        p.new_rule('branch', '"null" | "hello"')
        self.check(p, *STANDARD)

    def test_branching_complex(self):
        """ A more complicated branching example. """
        p = ParserBase()
        p.new_rule('end', '"llo"')
        p.new_rule('branch', '"hellp" | "he" end', main=True)
        self.check(p, *STANDARD)

    def test_recursion(self):
        """ Test the use of recursion to achieve repetition. """
        p = ParserBase()
        p.new_rule('repeat', '"hello" repeat | "hello"')
        # standard check on a single 'hello'
        self.check(p, *STANDARD)
        # check for repeated 'hello's
        check = 'hello' * 10
        self.check(p, check, check)

    def test_empty_string(self):
        """ Check that the parser understands empty strings. """
        p = ParserBase()
        p.new_rule('empty', '""')
        p.new_rule('hello', '"hello"')
        p.new_rule('combined', 'hello empty', main=True)
        # do the standard check
        self.check(p, *STANDARD)
        # check the empty case by itself
        p.main = 'empty'
        self.check(p, "", "")

    def test_whitespace(self):
        phrase = 'hello world'
        p = ParserBase(ignore_whitespace=True)
        p.new_rule('test', '"hello" "world"')
        token = p.parse(phrase)
        self.assertEqual(token.value(with_whitespace=True),
            phrase, msg='whitespace not ignored'
            )

    def test_grammar(self):
        """ Use the grammar method, also providing an opportunity to
        check a more complex multi-rule example.
        """
        p = ParserBase()
        p.grammar(GRAMMAR)
        # these should all succeed
        p.parse('https://www.abcabc.com')
        p.parse('https://www.bcaabc.co.uk')
        p.parse('http://www.a.fr')
        # these should all fail
        with self.assertRaises(NotFoundError):
            p.parse('www.abc.com')
        with self.assertRaises(NotFoundError):
            p.parse('https:/www.abcabc.com')
        with self.assertRaises(NotFoundError):
            p.parse('https://www.abcd.co.uk')
        with self.assertRaises(NotFoundError):
            p.parse('http://www..com')
        with self.assertRaises(IncompleteParseError):
            p.parse('https://www.a.fra')

    def test_grammar_with_whitespace(self):
        """ Check a different grammar, this time using whitespace-
        ignorant parsing.
        """
        p = ParserBase(ignore_whitespace=True)
        p.grammar(GRAMMAR_WS)
        # these should succeed
        p.parse('hello Earth hi?')
        p.parse('hi planet hello ?!?')
        p.parse('hello Earthhello ?? ??')
        # these should fail
        with self.assertRaises(NotFoundError):
            p.parse('hello planet hi')

    def test_pipe_escaping(self):
        """ Try using an escaped pipe in a rule. """
        p = ParserBase()
        p.new_rule(r'escaped', '"pipe: " "\|"')
        p.parse('pipe: |')

    def test_quote_escaping(self):
        """ Try using an escaped double-quote in a rule. """
        p = ParserBase()
        p.new_rule('quote', r'"\""')
        p.parse('"')

    def test_rule_from_function(self):
        """ Check the operation of custom rules. """

        def parse_hello(string):
            """ A rule that grabs the literal 'hello'. """
            w = STANDARD[0]
            if string.startswith(w):
                return w, string[len(w):]
            return None, string

        p = ParserBase()
        p.from_function(parse_hello, main=True)
        self.check(p, *STANDARD)
