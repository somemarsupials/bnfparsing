# -*- coding: utf-8 -*-

# built-in
from functools import wraps

# package
from .token import Token
from .exceptions import *

__all__ = ['ParserBase', 'rule']
        
# attribute name used to indicate parsing rules
RULE_ATTR = 'is_rule'

# a character that never occurs in regular strings
NULL = chr(0)

# for grammars
SEP = ':='
DELIMITER = '\n'


def head(string):
    """ Split a string into the first and following characters. If
    the string is empty or no string is passed, return None and the
    rest of the string.
    """
    return (string[0], string[1:]) if string else (None, string)


def rule(function):
    """ This decorator is used to mark bound methods as 'rules'.
    This approach is used because function definitions within class
    definitions cannot be appended to ParserBase.rules at the time of
    class definition, as it hasn't been created. This seems better than
    enforcing a naming convention.
    """
    setattr(function, RULE_ATTR, True)
    return function


def is_quote(c):
    """ Verify a string as a quotation mark. True for single or double 
    quotes. Designed to work with strings of length 1. """
    return c in "'\""


def is_literal(c):
    """ Verify a string as a literal. True for strings surrounded by 
    double quotes. 
    """
    return c[0] == '"' and c[-1] == '"' and len(c) > 1


def split_tokens(string):
    """ Convert a series of space-delimited token names and literals
    into a list of strings. The built-in str.split() is inadequate for
    this task because it cannot distinguish spaces within literals.

    The loop replaces spaces with the NULL character and places 
    finalised in the output list, in reverse. This is then split on the 
    NULL character to get separated token names.
    """
    # list to contain finalised characters, in reverse
    output = []
    # convert input string to list
    stream = list(string)
    # used to track literals
    quote_type = None
    while stream:
        c = stream.pop()
        # for quotes...
        if is_quote(c):
            # if an ending quote matches the starting quote...
            if c == quote_type:
                # mark the literal as closed
                quote_type = None
                # add a separator
                # note that characters must be combined in reverse
                c = NULL + c
            elif not quote_type:
                # else mark literal as open
                quote_type = c
                # and add a preceding separator
                c += NULL
        # only double quotes can be escaped
        elif c == '\\':
            # get the next character
            c = stream.pop()
            # if it's not a matching quote, append the escape 
            # and the character
            if not c == quote_type and is_quote(c):
                c += '\\'
        output.append(c)
    # if quote_type is not null, there is an unmatched quotation mark
    if quote_type:
        raise SyntaxError('unfinished literal')
    tokens = ''.join(reversed(output)).split(NULL)
    tokens = [t for t in tokens if not t.isspace() and t]
    return tokens

def stripify(function):
    """ Convert a function designed to parse a token from a string to 
    one that first removes whitespace from the string and then parses
    the token.
    """
    
    @wraps(function)
    def with_strip(string):
        return function(string.lstrip())
    
    # amend and add documentation
    with_strip.__doc__ = '{}\nRemoves whitespace before parsing' \
        'tokens.'.format(function.__doc__)

    return with_strip


class ParserBase(object):

    def __init__(self, ignore_whitespace=False):
        """ This class serves as the basis of a BNF parser. It doesn't
        come populated with any rules. These can be created in one of
        three ways: use the 'new_rule' function, add in a custom rule
        when subclassing this class or adding custom rules to an
        instance post-creation.

        The intended usage is that this class is sub-classed to create
        a parser for a specific purpose. If custom rules are defined as
        part of the subclass, they must be flagged with the 'rule'
        decorator - see above.

        Use the 'parse' method to have the parser parse a string into
        a hierarchical series of tokens. The parse method calls
        whichever function is indicated by self.main, unless otherwise
        instructed.

        Use the ignore_whitespace argument to instruct the parser to
        ignore whitespace between tokens. This does not require 
        whitespace between tokens, only that whitespace is removed
        between each function call.
        """
        self.rules = {}
        for item in dir(self):
            function = getattr(self, item)
            # check for functions marked as rules
            if hasattr(function, RULE_ATTR):
                # append any rules that are found
                if ignore_whitespace:
                    self.rules[item] = stripify(function)
                else:
                    self.rules[item] = function
        self.ignore_ws = ignore_whitespace
        self.main = None

    def parse(self, string, main=None, allow_partial=False):
        """ Create a syntax tree by parsing a string. Parses the input
        string using the role indicated by main, or otherwise self.main. 
        An exception is raised if any characters in the string are not 
        consumed, unless the allow_partial argument is True. 
        Returns a Token.
        """
        # search for the specified function to start with
        if main and main in self.rules:
            main_function = self.rules[main]
        # otherwise use the class' main function
        elif self.main and self.main in self.rules:
            main_function = self.rules[self.main]
        elif self.main:
            # if main has been specified but does not exist 
            raise BadEntryError('entry point does not exist')
        else:
            # if main has not been specified
            raise BadEntryError('no entry point specified')
        # call the main function
        token, unconsumed = main_function(string)
        # if tokens are found but the string has not been 
        # consumed entirely
        if token and unconsumed and not allow_partial:
            raise IncompleteParseError(
                'characters "%s" remaining' % unconsumed
            )
        # if the string does not match
        elif token is None:
            raise NotFoundError('%s not valid' % string)
        return token

    def from_function(self, function, name=None, 
            main=False, force=False):
        """ Install a rule from an existing function. This should be
        used in cases where customised functionality is required. For
        example, it's easier to use str.isalpha than write an 
        conditional with 52 branches.

        This registers the rule in self.rules. Duplicate rules replace
        the existing rule and can only be installed if 'force' is True.
        Use the main parameter to indicate that this is the main rule
        for the parser.
        """
        # check duplication
        if name in self.rules and not force:
            raise ValueError(
                'cannot redefine rule without forcing; use force=True'
                )
        # get the function name if not supplied
        if not name:
            name = function.__name__
        # set to main if main is undefined
        if main or not self.main:
            self.main = name
        # whitespace handling
        if self.ignore_ws:
            self.rules[name] = stripify(function)
        else:
            self.rules[name] = function

    def new_rule(self, name, rule, main=False, force=False):
        """ Generate and register a rule function from a string-based 
        rule. A rule is a series of space-delineated literals or names 
        of other rules. Rules can use the "or" operator ("|"). Literals
        must be surrounded by quotation marks (" or '). To parse 'or'
        operators, use a backslash to escape the "|".

        If the 'main' parameter is true, this will be set as the main 
        rule for the parser. Use the 'force' parameter to overwrite
        existing rules.
        """
        # check duplication
        if name in self.rules and not force:
            raise ValueError(
                'cannot redefine rule without forcing; use force=True'
                )
        # replace escaped 'or' characters with NULL
        rule = rule.replace(r'\|', NULL)
        # split 'or' expressions and then split groups
        groups = [split_tokens(group) for group in rule.split('|')]
        print('\n', rule, groups)
        options = len(groups) > 1
        # if there is an 'or'...
        if options:
            group_funcs = []
            # make each group
            for group in groups:
                # put pipes back into place
                group = [item.replace(NULL, '|') for item in group]
                group_funcs.append(self.make_group(group, name))
            # and then set up an 'or' function
            func = self.make_choice(group_funcs)
        else:
            # put pipes back into places
            group = [item.replace(NULL, '|') for item in groups[0]]
            # otherwise make the group into a single function
            func = self.make_group(group, name)
        # set to main if instructed or if main is undefined
        if main or not self.main:
            self.main = name
        # append to the rule dictionary
        self.rules[name] = func 

    def make_group(self, group, name):
        """ Convert a group into a function. A group is a series of
        literals or existing rules. For each item in the group, the
        new function will either try to call the named function or
        check the input string for the specified literal. For groups 
        with multiple members, the tokens created are appended to a new
        token. Groups with one member simply return the output of the
        function that's called.
        """
        if len(group) > 1:

            def group_func(string):
                """ Match a series of literals or rules to an input
                string. Each literal or group is called in succession.
                If any call fails, no token is returned. Otherwise,
                each token is appended to a new token, which is 
                returned. The input string is also returned, less any
                characters that have been consumed. Returns a tuple of
                a Token, or None, and a string.
                """
                # create a master token under which new tokens sit
                master = Token(token_type=name)
                # copy the string, in case it needs to be returned
                original = str(string)
                for item in group:
                    if is_literal(item):
                        # remove quotation marks before searching
                        token, string = self.literal(item[1:-1], string)
                        if token:
                            master.add(token)
                        else:
                            return None, original
                    else:
                        # get the appropriate function
                        function = self.rules[item]
                        # generate a token
                        token, string = function(string)
                        if token:
                            master.add(token)
                        else:
                            return None, original
                
                # return the master token and what remains of the string
                return master, string
            
        else:

            # get the single item
            item = group[0]

            def group_func(string):
                """ Match a literal or rule against an input string.
                If the call is successful, the resulting token is
                returned. Otherwise, the function returns None. I
                either case, the input string is also returned, less
                any characters that may have been consumed.
                """
                # remote quotation marks before searching
                if is_literal(item):
                    token, string = self.literal(item[1:-1], string)
                else:
                    # get the appropriate function
                    function = self.rules[item]
                    # generate a token
                    token, string = function(string)
                if token:
                    token.name = name
                    # return the token and remains of the string
                return token, string

        # return the function that was created
        return stripify(group_func) if self.ignore_ws else group_func

    def make_choice(self, choices):
        """ Create a function that handles a series or 'or' clauses.
        For example, " a | b | c". The function calls each rule or
        literal in turn and returns the first that is successful, or
        None. In any case, the input string is also returned, less any
        characters that were consumed. Returns a Token.
        """

        def choice_func(string):
            """ Call each rule or literal in turn. Return the token
            from the first successful call, as well as the input string
            less consumed characters. If all calls fail, return None
            and the original input.
            """
            for item in choices:
                token, string = item(string)
                if token:
                    # return a token if the function succeeds
                    return token, string
            # if none succeed, return nothing
            return None, string

        # return the function that was created
        # we don't need to worry about whitespace because each 
        # sub-function will remove whitespace prior to being called
        return choice_func

    def literal(self, phrase, string):
        """ Look for a string literal at the beginning of an input
        string. If found, return a token and the remainder of the
        string. Otherwise, return None and the original string.
        """
        # handle whitespace if required
        if self.ignore_ws:
            string = string.lstrip()
        if string.startswith(phrase):
            # if found, remove the phrase from the string
            string = string[len(phrase):]
            # return a token containing the phrase
            return Token('literal', phrase), string
        # otherwise return nothing
        return None, string

    def grammar(self, grammar, sep=SEP, delimiter=DELIMITER):
        """ Generate a series of rules from a grammar. Grammars should
        be given as a series of lines delineated by a newline, or
        whatever is passed as delimiter. Each line should contain a rule
        name and a definition separated by the ":=", or whatever
        is passed as the separator.

        Rules obey the same rules as the new_rule method of the parser.
        In short, give a space-delimited series of rule names or 
        literals, which must be surrounded by quote marks. See the
        new_rule function for more information.
        """
        for rule in grammar.strip().split(delimiter):
            name, parts = rule.split(SEP)
            self.new_rule(name.strip(), parts.strip())
    
