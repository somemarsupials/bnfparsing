# -*- coding: utf-8 -*-

# a character that never occurs in regular strings
NULL = chr(0)


def head(string):
    """ Split a string into the first and following characters. If
    the string is empty or no string is passed, return None and the
    rest of the string.
    """
    return (string[0], string[1:]) if string else (None, string)


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
    # replace escaped double quotes
    replaced = string.replace('\\"', NULL)
    groups = replaced.split('"')
    tokens = []
    # if the number of groups is even then there is an issue
    if len(groups) % 2 == 0:
        raise ValueError('unfinished literal %s' % string)
    # keep track of whether in a literal
    # this alternates between items in the groups list
    in_literal = False
    for g in groups:
        # restore quotes
        g = g.replace(NULL, '"')
        # split groups outside of literals
        if not in_literal and g and not g.isspace():
            tokens.extend(g.strip().split())
        # preserve groups in literals
        elif in_literal:
            tokens.append('"{}"'.format(g))
        # alternate
        in_literal = not(in_literal)
    return tokens

