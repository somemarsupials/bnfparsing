# -*- coding: utf-8 -*-

import unittest
from bnfparsing.token import Token
from bnfparsing.parser import ParserBase, rule_with_option
from bnfparsing.common import digit_run
from bnfparsing.whitespace import ignore, ignore_specific, require
from bnfparsing.exceptions import *

GRAMMAR = """
programme   := if_stmt "then" sum 
if_stmt     := "if" digit_run cmp digit_run
cmp         := "!=" | "=="| ">" | "<"
operation   := "+" | "-" | "/" | "*"
sum         := digit_run operation digit_run
"""


class TestWhitespace(unittest.TestCase):

    def test_ignore(self):
        """ Test the 'ignore' whitespace handling technique. """
        # set up parser with new grammar and the digit_run function
        p = ParserBase(ws_handler=ignore)
        p.from_function(digit_run, ws_handling=True)
        p.grammar(GRAMMAR, main='programme')
        # trial various combinations of whitespace
        # single spacing
        p.parse('if 34 > 33 then 44 + 3')  
        # no spacing
        p.parse('if34>33then44+3')  
        # random spacing, including a tab
        p.parse('if34 >  33 then   44+\t3') 
    
    def test_ignore_specific(self):
        """ Test the 'ignore_specific' whitespace handling 
        technique. 
        """
        # set up parser with new grammar and the digit_run function
        p = ParserBase(ws_handler=ignore_specific(' '))
        p.from_function(digit_run, ws_handling=True)
        p.grammar(GRAMMAR, main='programme')
        # trial various combinations of whitespace
        # single spacing
        p.parse('if 34 > 33 then 44 + 3')  
        # no spacing
        p.parse('if34>33then44+3')  
        # random spacing, including a tab - should fail
        with self.assertRaises(NotFoundError, msg='should ignore tab'):
            p.parse('if34 >  33 then   44+\t3') 

    def test_require(self):
        """ Test the 'require' whitespace handling technique. """
        # set up parser with new grammar and the digit_run function
        p = ParserBase(ws_handler=require(' '))
        p.from_function(digit_run, ws_handling=True)
        p.grammar(GRAMMAR, main='programme')
        # trial various combinations of whitespace
        # single spacing - should work
        p.parse('if 34 > 33 then 44 + 3')  
        # double spacing - should fail
        with self.assertRaises(NotFoundError):
            p.parse('if  34  >  33  then  44  +  3')  
        # no spacing - should fail
        with self.assertRaises(DelimiterError):
            p.parse('if34>33then44+3')  

    def test_require_with_ignore(self):
        """ Test the 'require' whitespace handling technique, using
        the 'ignore' option. """
        # set up parser with new grammar and the digit_run function
        p = ParserBase(ws_handler=require(' ', ignore=True))
        p.from_function(digit_run, ws_handling=True)
        p.grammar(GRAMMAR, main='programme')
        # trial various combinations of whitespace
        # single spacing - should work
        p.parse('if 34 > 33 then 44 + 3') 
        # double spacing - should now work
        p.parse('if  34  >  33  then  44  +  3')  
        # no spacing - should fail
        with self.assertRaises(DelimiterError):
            p.parse('if34>33then44+3')  

    def test_rule_decorator_without_ws(self):
        """ Test rules created using the rule decorator and the 'ignore
        whitespace' option. 
        """
        s1 = '_if'
        s2 = 'then'

        class Subclass(ParserBase):
            
            @rule_with_option(ws_handling=False)
            def _if(self, string):
                if string[:len(s1)] == s1:
                    return Token(s1, s1), string[len(s1):]
                return None, string

            @rule_with_option(ws_handling=False)
            def then(self, string):
                if string[:len(s2)] == s2:
                    return Token(s2, s2), string[len(s2):]
                return None, string

        p = Subclass()
        p.new_rule('both', '_if then', main=True)
        # should work
        p.parse_token('_ifthen')
        # check that spaces aren't ignored when they shouldn't be
        with self.assertRaises(NotFoundError, msg='ignored spaces'):
            p.parse_token('_if then')
        # check that spaces still aren't ignored with a handler
        p.set_ws_handler(ignore)
        with self.assertRaises(NotFoundError, 
                msg='ignored spaces with handler'):
            p.parse_token('_if then')

