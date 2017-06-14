# -*- coding: utf-8 -*-

# built-in
from functools import wraps

# package
from .utils import NULL, head, is_quote, is_literal, split_tokens
from .token import Token
from .exceptions import *

__all__ = ['ParserBase', 'rule']
        
# attribute name used to indicate parsing rules
RULE_ATTR = 'is_rule'
WS_ATTR = 'ws_handling'

# for grammars
SEP = ':='
DELIMITER = '\n'

# for debug
SUCCESS = 'success: "%s" leaving "%s"'
FAILED = 'failed: "%s" leaving "%s"'
CHARS = 50


def rule(function):
    """ This decorator is used to mark bound methods as 'rules'.
    This approach is used because function definitions within class
    definitions cannot be appended to ParserBase.rules at the time of
    class definition, as it hasn't been created. This seems better than
    enforcing a naming convention.
    """
    setattr(function, RULE_ATTR, True)
    return function
    

def rule_with_option(ws_handling=True):
    """ This decorator is used to mark bound methods as 'rules'.
    This approach is used because function definitions within class
    definitions cannot be appended to ParserBase.rules at the time of
    class definition, as it hasn't been created. This seems better than
    enforcing a naming convention.

    Use the optional ws_handling parameter to indicate whether the
    parser's whitespace handling should be applied to this rule.
    """

    def decorator(function):
        # apply normal decoration
        function = rule(function)
        # set specific attributes
        setattr(function, RULE_ATTR, ws_handling)
        return function

    return decorator


class ParserBase(object):

    def __init__(self, ws_handler=None):
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

        Supply a decorator to the whitespace handler parameter in order
        to properly handle whitespace between tokens. See the whitespace
        module for more information on this. If no handler is passed,
        whitespace characters are treated as normal characters.
        """
        # to contain parser rules
        self.rules = {}
        self.no_handling = {}
        # store whitespace handling method
        self.ws_handler = ws_handler
        # register functions marked as rules
        for item in dir(self):
            function = getattr(self, item)
            if hasattr(function, RULE_ATTR):
                new_function = self.enable_debug(function)
                # store in rule dictionary
                self.rules[item] = new_function
                # register rules that don't need whitespace handling
                if hasattr(function, WS_ATTR) and \
                        getattr(function, WS_ATTR):
                    self.no_handling[item] = new_function
        self.main = None

    def set_ws_handler(self, handler):
        """ Change or set the function used for handling whitespace
        in between tokens.
        """
        self.ws_handler = handler

    def parse(self, string, main=None, debug=False, 
            allow_partial=False, no_aggregate=False):
        """ Create a syntax tree by parsing a string. Parses the input
        string using the role indicated by main, or otherwise self.main. 
        An exception is raised if any characters in the string are not 
        consumed, unless the allow_partial argument is True. If the
        no_aggregate option is given then this is applied to the new 
        token. Returns a Token.
        """
        # search for the specified function to start with
        if main and main in self.rules:
            main_function = self.rules[main]
        # otherwise use the class' main function
        elif self.main and self.main in self.rules:
            main_function = self.rules[self.main]
        # if main has been specified but does not exist 
        elif main or self.main:
            raise BadEntryError('entry point does not exist')
        # if the parser is called without any rules
        elif not self.rules:
            raise BadEntryError('no rules exist')
        # if main has not been specified
        else:
            raise BadEntryError('no entry point specified')
        # call the main function
        if debug:
            # debug message to indicate the entry point
            params = (main if main else self.main, string[:CHARS])
            print('\nCalling main function "%s" with "%s"' % params)
            del params
        # we use NULL as a 'start-of-string' marker
        if self.ws_handler:
            string = NULL + string
        token, unconsumed = main_function(string, debug)
        # if the input string has not been entirely consumed
        if token and unconsumed and not allow_partial:
            raise IncompleteParseError('"%s" remaining' % unconsumed)
        # if the main rule cannot successfully parse the input string
        elif token is None:
            raise NotFoundError('%s not valid' % string)
        # add list of tokens to be aggregated
        if no_aggregate:
            aggregate = []
        else:
            aggregate = list(self.no_handling.keys())
        return token

    def enable_debug(self, function, debug=False):
        """ A decorator-like function that accepts a user-defined 
        function and converts it into a function that accepts and uses
        a debug parameter. This is used in conjunction with the
        'from_function' method.
        """

        @wraps(function)
        def debug_enabled_function(string, debug=False):
            # call the function
            token, string = function(string)
            # print the appropriate debug message
            if token and debug:
                print(SUCCESS % (token, string[:CHARS]))
            elif debug:
                print(FAILED % (token, string[:CHARS]))
            return token, string

        return debug_enabled_function

    def from_function(self, function, name=None, ws_handling=True,
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
        # debug handling
        function = self.enable_debug(function)
        # whitespace handling
        if ws_handling:
            self.no_handling[name] = function
        # register rule
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
        rule = rule.replace('\|', NULL)
        # split 'or' expressions and then split groups
        groups = []
        for group in rule.split('|'):
            groups.append(split_tokens(group.replace(NULL, '|')))
        # get number of groups
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
            func = self.make_choice(group_funcs, name)
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

            def group_func(string, debug=False):
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
                        token, string = self.literal(
                            item[1:-1], string, debug
                            )
                    else:
                        # get the appropriate function
                        function = self.rules[item]
                        # whitespace handling
                        if item in self.no_handling and self.ws_handler:
                            string = self.ws_handler(string)
                        # generate a token
                        token, string = function(string, debug)
                    if token:
                        master.add(token)
                    else:
                        if debug: 
                            print(FAILED % (item, string[:CHARS]))
                        return None, original
                # return the master token and what remains of the string
                if debug: 
                    print(SUCCESS % (token, string[:CHARS]))
                return master, string
            
        else:

            # get the single item
            item = group[0]

            def group_func(string, debug=False):
                """ Match a literal or rule against an input string.
                If the call is successful, the resulting token is
                returned. Otherwise, the function returns None. I
                either case, the input string is also returned, less
                any characters that may have been consumed.
                """
                # remote quotation marks before searching
                if is_literal(item):
                    token, string = self.literal(
                        item[1:-1], string, debug
                        )
                else:
                    # get the appropriate function
                    function = self.rules[item]
                    # whitespace handling
                    if item in self.no_handling and self.ws_handler:
                        string = self.ws_handler(string)
                    # generate a token
                    token, string = function(string, debug)
                if token:
                    token.token_type = name
                # return the token and remains of the string
                if debug and token: 
                    print(SUCCESS % (token, string[:CHARS]))
                elif debug:
                    print(FAILED % (item, string[:CHARS]))
                return token, string

        # return the function that was created
        return group_func

    def make_choice(self, choices, name):
        """ Create a function that handles a series or 'or' clauses.
        For example, " a | b | c". The function calls each rule or
        literal in turn and returns the first that is successful, or
        None. In any case, the input string is also returned, less any
        characters that were consumed. Returns a Token.
        """

        def choice_func(string, debug=False):
            """ Call each rule or literal in turn. Create a master token
            and add as a child the token from the first successful call, 
            as well as the input string less consumed characters. If all 
            calls fail, return None and the original input.
            """
            for item in choices:
                token, string = item(string, debug)
                if token:
                    # apply a tag
                    token.tag(name)
                    # return a token if the function succeeds
                    return token, string
            # if none succeed, return nothing
            return None, string

        # return the function that was created
        # we don't need to worry about whitespace because each 
        # sub-function will remove whitespace prior to being called
        return choice_func

    def literal(self, phrase, string, debug=False):
        """ Look for a string literal at the beginning of an input
        string. If found, return a token and the remainder of the
        string. Otherwise, return None and the original string.
        """
        original = str(string)
        # handle whitespace if required
        if self.ws_handler:
            string = self.ws_handler(string)
        if string.startswith(phrase):
            # if found, remove the phrase from the string
            string = string[len(phrase):]
            # return a token containing the phrase
            return Token('literal', phrase), string
        return None, original

    def grammar(self, grammar, sep=SEP, delimiter=DELIMITER, main=None):
        """ Generate a series of rules from a grammar. Grammars should
        be given as a series of lines delineated by a newline, or
        whatever is passed as delimiter. Each line should contain a rule
        name and a definition separated by the ":=", or whatever
        is passed as the separator.

        Rules obey the same rules as the new_rule method of the parser.
        In short, give a space-delimited series of rule names or 
        literals, which must be surrounded by quote marks. See the
        new_rule function for more information.
        
        Use the main parameter to specify one function as the main for
        the parser, i.e. the first function called when parsing.
        """
        for rule in grammar.strip().split(delimiter):
            name, parts = rule.split(SEP)
            name = name.strip()
            if main and name == main:
                self.main = main
            self.new_rule(name, parts.strip())
