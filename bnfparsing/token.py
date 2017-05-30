# -*- coding: utf-8 -*-

""" Defines a class that represents a token in a syntax tree. Contains
one class, Token. In many ways, tokens behave like strings.
"""


class Token:

    def __init__(self, token_type=None, text=''):
        """ Create a new token. Tokens can be initialised with any of a
        type and a text value. Tokens can have child tokens beneath
        them; the "value" of a token is either the text in the token or
        aggregated text of the tokens below it.

        The token behaves like a string in most respects, for example 
        with regards to length, iteration and comparison.
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

    def remove(self, token):
        """ Remove a child from the token. The token's id is used as the
        basis of comparison instead of the __eq__ method - this avoids
        removing the wrong token in a case where two tokens represent
        the same string. Returns nothing. """
        match = id(token)
        for child in self.children:
            if id(child) == match:
                self.children.remove(child)
        child.parent = None

    def has_under(self):
        """ True if the token has any children. """
        return len(self.children) > 0

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
        return 'Token %s (%s)' % (self.token_type, self.value())

    def __bool__(self):
        """ False for empty tokens, i.e. not token_type or text. """
        return bool(self.token_type or self.text)

    def __nonzero__(self):
        """ False for empty tokens, i.e. not token_type or text. """
        return bool(self.token_type or self.text)
