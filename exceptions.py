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
