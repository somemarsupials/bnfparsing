# -*- coding: utf-8 -*-

""" Defines a series of custom exceptions for the parser class. All
exceptions derive from ParserBaseException.
"""

class ParserBaseException(Exception):
    pass

class BadRuleError(ParserBaseException):
    pass

class BadEntryError(ParserBaseException):
    pass

class IncompleteParseError(ParserBaseException):
    pass

class NotFoundError(ParserBaseException):
    pass

class DelimiterException(ParserBaseException):
    pass
