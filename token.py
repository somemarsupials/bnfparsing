from functools import wraps


class NotFoundError(Exception):
    pass


class Token:

    def __init__(self, token_type=None, text='', parent=None):
        self.token_type = token_type
        self.text = text
        self.children = []
        self.parent = parent

    def add(self, child):
        self.children.append(child)

    def value(self):
        if self.children:
            return ''.join(c.value() for c in self.children)
        return self.text

    def __len__(self):
        return len(self.value())

    def __iter__(self):
        return iter(self.children)

    def __repr__(self):
        return 'Token {}: {}'.format(self.token_type, self.value())

    def __bool__(self):
        return True
