bnfparsing
==========

A simple BNF parser generator for Python.

Creating parsers
----------------

It's recommended that you subclass the ``bnfparsing.ParserBase`` class
whenever you create a new parser. This makes clear the purpose of the
parser.

Using a grammar
~~~~~~~~~~~~~~~

Create a new parser using string-based grammar.

.. code:: python

    IF_STMT = """
    if_stmt     := "if " test
    test        := name cmp name
    cmp         := "==" | "!=" | ">" | "<"
    name        := alpha name | alpha
    """

    class IfStmtParser(bnfparsing.ParserBase):

        def __init__(self):
        
            super().__init__(ignore_whitespace=True)
            self.grammar(IF_STMT)
            
    p = IfStmtParser()
    p.parse('if x==y')   

Creating individual rules, from strings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Subclass the ParserBase class to create a new parser. You can create
rules with a simple BNF (Backus-Naur Form) syntax. The first argument is
the name of the rule, the second is the body of the rule.

Rules can call other rules or capture literals, in double or single
quotes. Recursion is permitted. Use the ``ignore_whitespace`` parameter
to instruct the parser to skip over any whitespace between tokens.

.. code:: python

    class IfStmtParser(bnfparsing.ParserBase):

        def __init__(self):
            
            super().__init__()
            
            # add rules!
            self.new_rule('if_stmt', ' "if " test ')
            self.new_rule('test', 'name cmp name')
            self.new_rule('cmp', ' "==" | "!=" | ">" | "<" ')
            self.new_rule('name', 'alpha name | alpha')
            
    p = IfStmtParser()
    p.parse('if x==y')

You can also add rules by defining customised rules when subclassing, or
later on. Customised rules must accept an input string as an argument.
If successful, the custom rule must return a tuple containing the token
it's created and any unconsumed characters from the input string. If it
fails, it must return ``None`` and the original input string.

Using functions as rules
~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    class CaseParser(bnfparsing.ParserBase):

        # create rules as part of the class definition 
        # using the rule decorator
        
        @bnfparsing.rule
        def upper(self, string):
            """ Captures any upper-case letter. """
            char = string[0]
            if char.isupper():
                return Token('upper', char), string[1:]
            else:
                return None, string


    # or create them later on...
    def lowercase(string):
        """ Captures any lower-case letter. """
        char = string[0] 
        if char.islower():
            return Token('lower', char), string[1:]
        else:
            return None, string
           

    p = CaseParser()

    # ... as long as you add them as follows
    p.rule_from_function('lower', lowercase)

    p.parse('a')
    p.parse('A')

This can be useful when you don't want 26 options in a row, e.g.
``"A" | "B" | "C"``.

Also see ``bnfparsing.common``. This module contains some useful
functions that can be dropped in as rules. Most parsers will need one or
two of the common functions, which include:

-  ``alpha``, ``lower`` and ``upper``
-  ``digit``
-  Sequence versions of the above, e.g. ``alpha_run``. These capture
   sequences of alpha characters.
-  ``whitespace``

Whitespace handling
~~~~~~~~~~~~~~~~~~~

When creating a parser, use the ``ws_handler`` option to specify a means
by which the parse should handle whitespace between tokens. A whitespace
handler is a function that is called on the input string before each
literal token is parsed.

``bnfparsing.whitespace`` defines three handlers for use.

-  ``ignore`` removes all whitespace between tokens and requires none.
-  ``ignore_specific`` removes all of the given types of whitespace
   prior to parsing, much like the in-built ``str.lstrip``.
-  ``require`` raises a ``DelimiterError`` if a specific whitespace
   phrase *is not found* between tokens. Use the ``ignore`` option to
   optionally remove other whitespace that is surplus to that required

``ignore`` can be passed directly as a whitespace handler, whereas the
other two must be passed with arguments, e.g. ``require(' ')``.

You are free to define your own handler - it must accept an input string
and return a string. You can also specify whether custom rules should
use whitespace handling with the ``rule_with_option`` decorator.

Outputs
-------

As seen, you can run the parser on an input string using the ``parse``
method. This raises an error if the given string does not fit the rule
set or if there are any tokens remaining - unless you call ``parse``
with the optional ``allow_partial`` argument.

Otherwise, the parser will consume the string and return an instance of
``bnfparsing.Token``. This the top-most node of the syntax tree; any
child nodes represent the components of each node.

Use the ``value`` method to generate the content of each node. For the
nodes at the base of the tree this will return the value in the node.
For all others, ``value`` recursively combines the values of the tokens
beneath it.

.. code:: python

    # using the example above...
    root = p.parse('if x==y')

    assert(root.value() == 'if x==y')

    for t in root.iter_under():
        print(t.token_type, ':',  t.value())

Leading to...

::

    >>> 'literal : if'
    >>> 'test: x == y'

Tokens also come equipped with a range of methods for searching or
iterating over the tokens below them. These include:

-  ``child``: returns the nth child
-  ``series``: returns a lowest level tokens in a list.
-  ``level``: recursively returns a list of the nth-deepest tokens
-  ``find``: returns all tokens of a given token type
-  ``flatten``: returns a new token with the same value, but collapsing
   the repeatedly recursive tokens generated by recursive rules.

There are options for ensuring that some tokens are not broken down any
further by ``series``, including

See documentation for more information. Some of these methods come with
an ``as_str`` option, returning lists of strings instead of lists of
tokens.

Further work
------------

-  Expanded set of common functions?
-  EBNF syntax, without relying on recursion?S
