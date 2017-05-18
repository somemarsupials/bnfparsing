# bnfparsing
A simple BNF parser generator for Python.

## Usage

Subclass the ParserBase class to create a new parser. You can create rules with
a simple BNF (Backus-Naur Form) syntax. The first argument is the name of the
rule, the second is the body of the rule.

Rules can call other rules or capture literals, in double or single quotes.
Recursion is permitted.

```Python
class WordParser(bnfparsing.ParserBase):

    def __init__(self):
        
        # add arguments for Python 2.x
        super().__init__()
        
        # add rules!
        self.rule_from_string('if_stmt', ' "if" test ', main=True)
        self.rule_from_string('test', 'name cmp name')
        self.rule_from_string('cmp', ' "==" | "!=" | ">" | "<" ')
        self.rule_from_string('name', 'alpha name | alpha')
        
p = WordParser()
p.parse('if x == y')
```

You can also add rules by defining customised rules when subclassing, or later on. 
Customised rules must accept an input string as an argument. If successful, the
custom rule must return a tuple containing the token it's created and any unconsumed 
characters from the input string. If it fails, it must return None and the original 
input string.

```Python
from bnfparsing import ParserBase, Token

class CaseParser(ParserBase):

    # create rules as part of the class definition (using the rule decorator)
    @rule
    def upper(self, string):
        """ Captures any upper-case letter. """
        if string[0].isupper():
            return Token(token_type='upper', text=string[0]), string[1:]
        else:
            return None, string


# or create them later on...
def lowercase(string):
    """ Captures any lower-case letter. """ 
    if string[0].islower():
        return Token(token_type='lower', text=string[0]), string[1:]
    else:
        return None, string
       

p = CaseParser()

# ... as long as you add them as follows
p.rule_from_function('lower', lowercase)

p.parse('a')
p.parse('A')
```

This can be useful when you don't want 26 options in a row, 
e.g. "A" | "B" | "C" ...
