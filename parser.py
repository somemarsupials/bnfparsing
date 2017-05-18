# -*- coding: utf-8 -*-

# compatibility
from __future__ import print_function

# package
from .token import Token
from .exceptions import *


# The intended usage for this module is that the ParserBase class is
# subclassed and populated with BNF-style rules.

# ParserBase uses a simple BNF-like syntax to build rules that can be
# used to parse regular expressions (or anything). Rules are supplied
# as strings and are converted into functions. 

# Rules are given as space-delimited words, including the use of the or 
# ("|") operator. Double quotes are used to delimit literals. Literals
# expressions will match the exact phrase contained between the double
# quotes. Non-literal words are treated as existing rules, which are
# retrieved from the parser's dictionary of existing rules.

# Example: rule_from_string('greeting', 'hello "world" | hi')

# In this case, the rule will match either the results of the  function 
# 'hello' and the literal 'world', or the results of the function 'hi'. 
# Recursion is permitted.

# The general form of rule-functions is that they accept a string and
# return a token (or None) and what remains of the string (or the whole
# string). This is used in place of an IO-based system.

# Users can create rules through the use of the 'rule_from_string' 
# function or through custom functions, using the function 
# 'rule_from_function'. Customised functions must follow the pattern 
# described in the previous paragraph. If customised functions are
# defined as part of a subclass of ParserBase, use the 'rule' decorator
# to include these functions in the parser's rule dictionary.

# Custom functions can be used in place of long or complicated rules;
# for example, the pre-defined 'alpha' function is easier to write and 
# more efficient than a rule with 52 'or' expressions, for 26 letters
# and 2 cases.
        
# attribute name used to indicate parsing rules
RULE_ATTR = 'is_rule'

# a character that never occurs in regular strings
NULL = chr(0)


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
    class definition, as it hasn't been created. This seems like a more
    elegant solution than using the names of the functions.
    """
    setattr(function, RULE_ATTR, True)
    return function


def is_quote(c):
    """ Returns true for single or double quotes. """
    return c in "'\""


def is_literal(c):
    """ Returns true for strings surrounded by double quotes. """
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
    return ''.join(reversed(output)).split(NULL)


class ParserBase(object):

    def __init__(self):
        """ Set up the parser. Create an empty dictionary to contain
        rules. Function definitions that are prefaced with an underscore
        are intended to be special-case rules (e.g. empty, alpha). These
        are added to the rule dictionary immediately, with the 
        underscore removed from the name. 
        """
        self.rules = {}
        for item in dir(self):
            function = getattr(self, item)
            # check for functions marked as rules
            if hasattr(function, RULE_ATTR):
                # append any rules that are found
                self.rules[item] = function
        self.main = None

    def parse(self, string, main=None):
        """ Create a syntax tree by parsing a string. The input string 
        is expected to correspond to the function that is marked as the
        main function. An exception is raised if any characters in the 
        string are not consumed.
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
        token, remaining = main_function(string)
        # if tokens are found but the string has not been 
        # consumed entirely
        if token and remaining:
            raise IncompleteParseError(
                'characters "%s" remaining' % remaining
            )
        # if the string does not match
        elif token is None:
            raise NotFoundError('%s not valid' % string)
        return token

    def rule_from_function(self, function, name=None):
        """ Install a rule from an existing function. This should be
        used in cases where customised functionality is required. For
        example, this is useful for capturing empty tokens. It's also
        easier to use str.isalpha than write an conditional with 52
        branches.
        """
        # get the function name if not supplied
        if not name:
            name = function.__name__
        self.rules[name] = function

    def rule_from_string(self, name, rule, main=False):
        """ Generate and register a rule function from a string-based 
        rule. A rule is a series of space-delineated literals or names 
        of other rules. Rules can use the "or" operator ("|"). Literals
        should be surrounded by quotation marks (" or '). 
        """
        # replace escaped 'or' characters with NULL
        rule = rule.replace("\\|", chr(0))
        # split 'or' expressions and then split groups
        groups = [group.split() for group in rule.split('|')]
        options = len(groups) > 1
        # if there is an 'or'...
        if options:
            group_funcs = []
            # make each group
            for g in groups:
                group_funcs.append(self.make_group(g, name))
            # and then set up an 'or' function
            func = self.make_choice(group_funcs)
        else:
            # otherwise make the group into a single function
            func = self.make_group(groups[0], name)
        if main:
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
                characters that have been consumed.
                """
                master = Token(token_type=name)
                original = str(string)
                for item in group:
                    if is_literal(item):
                        token, string = self.literal(item[1:-1], string)
                        if token:
                            master.add(token)
                        else:
                            return None, original
                    else:
                        function = self.rules[item]
                        token, string = function(string)
                        if token:
                            master.add(token)
                        else:
                            return None, original

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
                if is_literal(item):
                    token, string = self.literal(item[1:-1], string)
                else:
                    function = self.rules[item]
                    token, string = function(string)
                if token:
                    token.name = name
                return token, string

        # return the function that was created
        return group_func

    def make_choice(self, choices):
        """ Create a function that handles a series or 'or' clauses.
        For example, " a | b | c". The function calls each rule or
        literal in turn and returns the first that is successful, or
        None. In any case, the input string is also returned, less any
        characters that were consumed.
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
                    return token, string
            return None, string

        # return the function that was created
        return choice_func

    def literal(self, phrase, string):
        """ Look for a string literal at the beginning of an input
        string. If found, return a token and the remainder of the
        string. Otherwise, return None and the original string.
        """
        if string.startswith(phrase):
            string = string[len(phrase):]
            return Token('literal', phrase), string
        return None, string
    
    @rule
    def alpha(self, string):
        char, other = head(string)
        if char and char.isalpha():
            return Token(token_type='alpha', text=char), other 
        return None, string

    @rule
    def digit(self, string):
        char, other = head(string)
        if char and char.isdigit():
            return Token(token_type='digit', text=char), other
        return None, string

    @rule
    def whitespace(self, string):
        nonspace = string.lstrip()
        if nonspace != string:
            n = len(nonspace)
            return string[:n], string[n:]
        return None, string


class ReParser(ParserBase):

    def __init__(self):

        # initialise class
        super(ReParser, self).__init__()

        # specification of regular expression
        self.rule_from_string('char', 'alpha | digit | "_"')
        self.rule_from_string('word', 'char word | char ', main=True)

if __name__ == '__main__':
    p = ReParser()
    print(p.parse('hello'))
