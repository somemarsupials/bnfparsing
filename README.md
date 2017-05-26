# bnfparsing
A simple BNF parser generator for Python.

## Creating parsers

It's recommended that you subclass the `bnfparsing.ParserBase` class whenever you create a new parser. This makes clear the purpose of the parser.

### Using a grammar

Create a new parser using string-based grammar.

```Python
IF_STMT = """
if_stmt 	:= "if" test
test 		:= name cmp name
cmp 		:= "==" | "!=" | ">" | "<"
name		:= alpha name | alpha
"""

class IfStmtParser(bnfparsing.ParserBase):

	def __init__(self):
		super().__init__(ignore_whitespace=True)
		self.grammar(IF_STMT)
		
p = IfStmtParser()
p.parse('if x == y')   
```

### Using string-based rule creation

Subclass the ParserBase class to create a new parser. You can create rules with a simple BNF (Backus-Naur Form) syntax. The first argument is the name of the rule, the second is the body of the rule.

Rules can call other rules or capture literals, in double or single quotes. Recursion is permitted. Use the `ignore_whitespace` parameter to instruct the parser to skip over any whitespace between tokens.

```Python
class IfStmtParser(bnfparsing.ParserBase):

    def __init__(self):
        
        super().__init__(ignore_whitespace=True)
        
        # add rules!
        self.new_rule('if_stmt', ' "if" test ')
        self.new_rule('test', 'name cmp name')
        self.new_rule('cmp', ' "==" | "!=" | ">" | "<" ')
        self.new_rule('name', 'alpha name | alpha')
        
p = IfStmtParser()
p.parse('if x == y')
```

You can also add rules by defining customised rules when subclassing, or later on. 
Customised rules must accept an input string as an argument. If successful, the
custom rule must return a tuple containing the token it's created and any unconsumed 
characters from the input string. If it fails, it must return `None` and the original 
input string.

### Using functions as rules

```Python
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
```

This can be useful when you don't want 26 options in a row, 
e.g. `"A" | "B" | "C"`. 

Also see `bnfparsing.common`. This module contains some useful functions that can be dropped in as rules. Most parsers will need one or two of the common functions, which include:

+ `alpha`, `lower` and `upper`
+ `digit`
+ `whitespace`

## Outputs

As seen, you can run the parser on an input string using the `parse` method. This raises an error if the given string does not fit the rule set or if there are any tokens remaining - unless you call `parse` with the optional `allow_partial` argument.

Otherwise, the parser will consume the string and return an instance of `bnfparsing.Token`. This the top-most node of the syntax tree; any child nodes represent the components of each node.

Use the `value` method to generate the content of each node. For the nodes at the base of the tree this will return the value in the node. For all others, `value` recursively combines the values of the tokens beneath it.

```Python
# using the example above...
root = p.parse('if x == y')

assert(root.value() == 'if x == y')

for t in root.iter_under():
	print(t.token_type, ':',  t.value())
```
Leading to...

```
>>> 'literal : if'
>>> 'test: x == y'
```

## Further work

+ Expanded set of common functions?
+ Improved whitespace handling; for example, an option that forces the parser to find whitespace between each token, rather than ignore it? 
+ Improved tools for parsing token trees?