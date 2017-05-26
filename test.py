def tokenise(string):
    string = string.replace('\\"', NULL)
    groups = string.split('"')
    tokens = []
    if len(groups) % 2 == 0:
        raise ValueError('unfinished literal')
    in_literal = False
    for g in groups:
        g = g.replace(NULL, '"')
        if not in_literal and g and not g.isspace():
            tokens.extend(g.split())
        elif in_literal:
            tokens.append(g)
        in_literal = not(in_literal)
    return tokens

print(tokenise('"pipe: " |'))
