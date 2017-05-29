# -*- encoding: utf-8 -*-

from functools import wraps
from .exceptions import DelimiterException

""" This module contains decorators used to handle the whitespace
between tokens, when parsing.
"""


def make_handler(handling_method, doc_line=None):
    """ Create a decorator that handles whitespace between tokens using
    a whitespace-handling function. The handler should accept a string
    as input and remove as much whitespace as required, returning the
    processed string. Returns a function. 
    """
    # create a decorator that pre-processes the string before it's
    # handed to the parsing function
    def wrapper(function):
        
        @wraps(function)
        def new_function(string, debug=False):

            # modify the docstring if an amendment given
            addition = ('\nAmended to handle whitespace using '
                'method "%s".' % handling_method.__name__
            )
            new_function.__doc__ += addition

            return function(handling_method(string), debug)

        return new_function 

    # return new function
    return wrapper


def ignore(string):
    """ A whitespace handler that ignores the whitespace between tokens. 
    This means that it doesn't matter if there is whitespace or not - 
    any whitespace is stripped from the input string before the next 
    token is parsed.
    """
    return string.lstrip()    


def ignore_specific(whitespace, ignore=False):
    """ A whitespace handler that ignores certain whitespace between 
    tokens. This means that it doesn't matter if there is whitespace or 
    not - the chosen whitespace is stripped from the input string before 
    the next token is parsed.
    """
    def handler(string):
        return string.lstrip(whitespace)

    return handler


def require(whitespace, ignore=False):
    """ A factory for whitespace handlers that require a given 
    whitespace 'phrase' between tokens. If the required whitespace is 
    not present an exception is raised. Use the 'ignore' parameter to 
    ignore any additional whitespace above that which is required.

    This function generates a handler function for make_handler. 
    Returns a function.
    """
    n = len(whitespace)

    def handler(string):
        if string[:n] != whitespace:
            raise DelimiterException
        return string[n:].lstrip() if ignore else string[n:]

    return handler


# create some potentially useful handlers
one_space = require(' ')
one_space_or_more = require(' ', ignore=True)
ignore_spaces = ignore_specific(' ')
