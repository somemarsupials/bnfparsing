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
        return Token('lower', char), other 
    return None, string


def lower_run(string):
    """ Capture a run of lower-case characters. """
    for n, char in enumerate(string):
        if not char.islower():
            break
        n += 1
    if n > 0:
        return Token('lower_run', string[:n]), string[n:] 
    return None, string


def upper(string):
    """ Capture any upper-case character. """
    char, other = head(string)
    if char and char.isupper():
        return Token('upper', char), other 
    return None, string


def upper_run(string):
    """ Capture a run of upper-case characters. """
    for n, char in enumerate(string):
        if not char.isupper():
            break
        n += 1
    if n > 0:
        return Token('upper_run', string[:n]), string[n:] 
    return None, string


def alpha(string):
    """ Capture any alphabetic character. """
    char, other = head(string)
    if char and char.isalpha():
        return Token('alpha', char), other 
    return None, string


def alpha_run(string):
    """ Capture a run of alpha-case characters. """
    for n, char in enumerate(string):
        if not char.isalpha():
            break
        n += 1
    if n > 0:
        return Token('alpha_run', string[:n]), string[n:] 
    return None, string


def digit(string):
    """ Capture any digit. """
    char, other = head(string)
    if char and char.isdigit():
        return Token('digit', char), other
    return None, string


def digit_run(string):
    """ Capture a run of digit-case characters. """
    for n, char in enumerate(string):
        if not char.isdigit():
            break
        n += 1
    if n > 0:
        return Token('digit_run', string[:n]), string[n:] 
    return None, string


def whitespace(string):
    """ Capture runs of whitespace. """
    nonspace = string.lstrip()
    if len(nonspace) != len(string):
        return Token('whitespace', string[:len(nonspace)+1]), nonspace
    return None, string
