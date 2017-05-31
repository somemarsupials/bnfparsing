# -*- coding: utf-8 -*-

""" This package contains a series of tools for creating BNF, or 
Backus-Naur, form parsers. These use a series of rules to parse an input
string into a series of tokens, using a recursive descent method.

Importing this package automatically includes the ParserBase class and
the Token class. The ParserBase class can be used to create BNF parsers.
This is done through the creation of rules. Whitespace handlers are also
included in this import.

This can be done:
    - using a grammar, a series of newline-delimited rules
    - creating rules from strings
    - using existing functions as rules

See the documentation in the ParserBase for more information. It is
common to subclass this class for each specific type of parser.

The parser breaks an input string into a series of nested Tokens. These
each represent strings or collect strings.
"""

from .parser import ParserBase, rule, rule_with_option
from .token import Token
from .whitespace import ignore, ignore_specific, require
