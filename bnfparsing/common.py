# -*- coding: utf-8 -*-

""" This module contains a series of common functions that you may
want to use to build a parser.
"""

from .parser import head
from .token import Token

# This module contains commonly-used expressions, for utility
# purposes. Add these to parser classes.

def lower(string):
    """ Capture any lower-case character. """
    char, other = head(string)
    if char and char.islower():
        return Token(token_type='lower', text=char), other 
    return None, string


def upper(string):
    """ Capture any upper-case character. """
    char, other = head(string)
    if char and char.isupper():
        return Token(token_type='alpha', text=char), other 
    return None, string


def alpha(string):
    """ Capture any alphabetic character. """
    char, other = head(string)
    if char and char.isalpha():
        return Token(token_type='alpha', text=char), other 
    return None, string


def digit(string):
    """ Capture any digit. """
    char, other = head(string)
    if char and char.isdigit():
        return Token(token_type='digit', text=char), other
    return None, string


def whitespace(string):
    """ Capture runs of whitespace. """
    nonspace = string.lstrip()
    if len(nonspace) != len(string):
        return Token('whitespace', string[:len(nonspace)+1]), nonspace
    return None, string
