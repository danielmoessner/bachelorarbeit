import ast
import astpretty

def code_1(x, y):
    assert x < y
    while x < y:
        if x < 0:
            x = x + 7
        else:
            x = x + 10
        if y < 0:
            y = y - 10
        else:
            y = y + 3
    assert y <= x and x <= y + 16
    return (x, y)


code_1 = """
assert x < y
while x < y:
    if x < 0:
        x = x + 7
    else:
        x = x + 10
    if y < 0:
        y = y - 10
    else:
        y = y + 3
assert y <= x and x <= y + 16
"""

# print(code_1(2, 3))
# print(ast.dump(ast.parse('x = 10 + y * 5')))
# print(ast.dump(ast.parse(code_1)))
astpretty.pprint(ast.parse(code_1))