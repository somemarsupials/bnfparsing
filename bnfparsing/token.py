# -*- coding: utf-8 -*-

""" Defines a class that represents a token in a syntax tree. Contains
one class, Token.
"""


class Token:

    def __init__(self, token_type=None, text=''):
        """ Create a new token. Tokens can be initialised with any of a
        type and a text value.
        """
        self.token_type = token_type
        self.text = text
        self.children = []
        self.parent = None

    def add(self, child):
        """ Add a child token to this token. Child-parent relations
        indicate the components of a token: e.g. the token 'foo' is made
        up of 'bar' and 'baz'. This is represented by adding these
        tokens as children. The 'value' method will add the text in
        both of these children to represent a 'foo' token.
        
        Non-literal tokens should not have a text parameter but instead 
        rely on the 'value' method to assemble a representative string.

        Returns nothing.
        """
        # prevent the creation of literals with children
        if self.text:
            raise RuntimeError('adding children to a literal')
        self.children.append(child)
        child.parent = self

    def value(self, with_whitespace=False):
        """ For a literal (i.e. a token with self.text) return the
        token's text. Otherwise, recursively return the text values of 
        child tokens. Returns a string.
        """
        if self.children and self.text:
            raise RuntimeError('token with text and children')
        elif self.children:
            base = ' ' if with_whitespace else ''
            return base.join(c.value() for c in self.children)
        return self.text

    def iter_under(self):
        """ Iterate over the children beneath the token. """
        return iter(self.children)

    def __eq__(self, other):
        """ Compare the value of the token to a string or token. """
        if isinstance(other, Token):
            return self.value() == other.value()
        return self.value() == other

    def __len__(self):
        """ Return the length of the token value. """
        return len(self.value())

    def __iter__(self):
        """ Iterate over characters in self. """
        return iter(self.value())

    def __repr__(self):
        return 'Token {}: "{}"'.format(self.token_type, self.value())

    def __bool__(self):
        """ False for empty tokens, i.e. not token_type or text. """
        return bool(self.token_type or self.text)

    def __nonzero__(self):
        """ False for empty tokens, i.e. not token_type or text. """
        return bool(self.token_type or self.text)
