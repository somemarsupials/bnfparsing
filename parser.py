# -*- coding: utf-8 -*-

from bnfparsing import ParserBase, Token, rule
from bnfparsing.common import alpha, digit
from bnfparsing.utils import head

# list of valid escape characters
ESCAPES = r'WwDdSsnt()[]?*+|'

# list of valid printable characters
IMPERMISSIBLE = '?*+|[]{}-'


# the grammar specification for regular expressions
REGEX_GRAMMAR = r"""
regex       := or_phrase regex | phrase
or_phrase   := "\|" phrase
phrase      := item phrase | item
item        := atom modifier | atom
modifier    := "+" | "*" | "?"
atom        := char | group | set
group       := "(" regex ")"
set         := "[" setitems "]"
setitems    := setitem setitems | setitem
setitem     := range | char | escape
range       := alpha "-" alpha | digit "-" digit
escape      := "\\" escapechar
char        := any | misc_char
any         := "."
"""

class RegexParser(ParserBase):

    def __init__(self):

        # initialise parent class
        super(RegexParser, self).__init__()
        
        # install rules
        for rule in (alpha, digit):
            self.from_function(rule)

        # install grammar
        self.grammar(REGEX_GRAMMAR, main='regex')

    @rule
    def escapechar(self, string):
        """ Identify escapable characters. """
        char, other = head(string)
        if char and char in ESCAPES:
            return Token('escapechar', char), other
        return None, string

    @rule
    def misc_char(self, string):
        """ Identify miscellaneous characters that are permitted in
        regular expressions. Permissible characters are negatively 
        defined - they are acceptable if not in the IMPERMISSIBLE list.
        """
        char, other = head(string)
        if char and char not in IMPERMISSIBLE:
            return Token('char', char), other
        return None, string


if __name__ == '__main__':
    p = RegexParser()
    root = p.parse('[A-Z1-2A-Z]')
    print(root)
    for i in range(5):
        print([t.tags for t in root.flatten().level(i)])
