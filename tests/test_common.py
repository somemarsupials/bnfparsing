# -*- coding: utf-8 -*-

import unittest

# package
from bnfparsing.token import Token
from bnfparsing.parser import ParserBase
from bnfparsing.exceptions import *
import bnfparsing.common

# to identify functions in the common module
is_func = lambda s: s.islower() and not s.startswith('__')

# list of rules in the common module
RULES = [rule for rule in dir(bnfparsing.common) if is_func(rule)]


class CommonParser(ParserBase):

    def __init__(self):
        """ A parser that comes equipped with common rules. """
        # intialise
        super(CommonParser, self).__init__()        
        # add common rules
        for rule in RULES:
            function = getattr(bnfparsing.common, rule)
            self.from_function(function)


class TestCommon(unittest.TestCase):

    def setUp(self):
        """ Create a parser. """
        self.parser = CommonParser()
 
    def parse(self, *args, **kwargs):
        """ Shortcut to access parse method. """
        return self.parser.parse(*args, **kwargs)

    def single_test(self, name, string, fail=None):
        """ A test routine for functions that capture a single
        character.
        """
        # try parsing a single token from a stream
        token = self.parse(string, main=name, allow_partial=True)
        # add a custom 'repeat' to the parser
        # this is of the form e.g. "alpha repeat | alpha"
        new_name = 'manual_run_%s' % name
        filler = (name, new_name, name)
        self.parser.new_rule(new_name, '%s %s | %s' % filler)
        # trial the rule
        token = self.parse(string, main=new_name)
        # if a failure is given, use the newly built run
        if fail:
            with self.assertRaises(NotFoundError):

                self.parse(fail, main=new_name)

    def run_test(self, name, string, fail=None):
        """ A test routine for functions that capture a run. """
        # try parsing the run
        token = self.parser.parse(string, main=name)
        # parse the fail case if given
        if fail: 
            with self.assertRaises(NotFoundError):
                self.parser.parse(fail, main=name)

    def test_alpha(self):
        """ Test the alpha method. """
        self.single_test('alpha', 'aBa', '1Ga')

    def test_lower(self):
        """ Test the lower method. """
        self.single_test('lower', 'aba', 'GGa')

    def test_upper(self):
        """ Test the upper method. """
        self.single_test('upper', 'ABA', 'aGa')

    def test_digit(self):
        """ Test the digit method. """
        self.single_test('digit', '123', 'a3a')
   
    def test_alpha_run(self):
        """ Test the alpha_run method. """
        self.run_test('alpha_run', 'GHj', '435')

    def test_lower_run(self):
        """ Test the lower_run method. """
        self.run_test('lower_run', 'ghj', 'Abc')

    def test_upper_run(self):
        """ Test the upper_run method. """
        self.run_test('upper_run', 'RYH', 'aaa')

    def test_digit_run(self):
        """ Test the digit_run method. """
        self.run_test('digit_run', '123', 'a35')

    def test_whitespace(self):
        """ Test the whitespace method. """
        self.run_test('whitespace', '  \t', '435')

    def tearDown(self):
        """ Remove functions and attributes specific to these test. """
        del self.parser
