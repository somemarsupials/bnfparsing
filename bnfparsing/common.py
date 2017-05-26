# -*- coding: utf-8 -*-

from .parser import head

# This module contains commonly-used expressions, for utility
# purposes. Add these to parser classes.

def alpha(self, string):
    """ Capture any alphabetic character. """
    char, other = head(string)
    if char and char.isalpha():
        return Token(token_type='alpha', text=char), other 
    return None, string


def digit(self, string):
    """ Capture any digit. """
    char, other = head(string)
    if char and char.isdigit():
        return Token(token_type='digit', text=char), other
    return None, string


def whitespace(self, string):
    """ Capture runs of whitespace. """
    nonspace = string.lstrip()
    if nonspace != string:
        n = len(nonspace)
        return string[:n], string[n:]
    return None, string

