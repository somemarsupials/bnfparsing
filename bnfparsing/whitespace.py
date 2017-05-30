# -*- encoding: utf-8 -*-

from functools import wraps
from .utils import NULL
from .exceptions import DelimiterError

""" This module contains decorators used to handle the whitespace
between tokens, when parsing.
"""


def make_handler(handling_method):
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
            
            token, unused = function(handling_method(string), debug)
            if token:
                return token, unused
            return None, string
        
        return new_function 

    # return new function
    return wrapper


def ignore(string):
    """ A whitespace handler that ignores the whitespace between tokens. 
    This means that it doesn't matter if there is whitespace or not - 
    any whitespace is stripped from the input string before the next 
    token is parsed.
    """
    if string and string[0] == NULL:
        string = string[1:]
    return string.lstrip()    


def ignore_specific(whitespace):
    """ A whitespace handler that ignores certain whitespace between 
    tokens. This means that it doesn't matter if there is whitespace or 
    not - the chosen whitespace is stripped from the input string before 
    the next token is parsed.
    """
    def handler(string):
        if string and string[0] == NULL:
            string = string[1:]
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
        if string and string[0] == NULL:
            return string[1:]
        elif string[:n] != whitespace:
            raise DelimiterError('"%s..." not delimited' % string[:50])
        return string[n:].lstrip() if ignore else string[n:]
    
    return handler

