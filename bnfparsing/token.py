# -*- coding: utf-8 -*-

__all__ = ['Token']

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
        """ Add a child token to this token. Child-parent relations are
        used to illustrate the recursivity of BNF rules. Non-literal
        tokens should not have a text parameter but instead rely on the
        'value' method to assemble a representative string. """
        # prevent the creation of literals with children
        if self.text:
            raise RuntimeError('adding children to a literal')
        self.children.append(child)
        child.parent = self

    def value(self):
        """ For a literal (i.e. a token with self.text) return the text.
        Else recursively return the text values of child tokens.
        """
        if self.children:
            return ''.join(c.value() for c in self.children)
        return self.text

    def iter_under(self):
        """ Iterate over the children beneath the token. """
        return iter(self.children)

    def jump(self):
        """ Go to the parent token. """
        return self.parent

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

