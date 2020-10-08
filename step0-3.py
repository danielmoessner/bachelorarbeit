import random
import pysmt
from pysmt.shortcuts import Symbol, LE, GE, Int, GT, LT, And, Equals, Plus, Solver, is_sat, Or, Not, Minus, Ite, Implies, is_unsat, get_model
from pysmt.typing import INT, STRING, BOOL, REAL


def func(x, y, X, Y, invariant):
    assert x < y
    start = LT(X, Y)
    start2 = start
    X2 = X
    Y2 = Y
    if is_unsat(Not(Implies(start, invariant))):
        print("(4) established, i.e.,  invariant holds at loop start")
    while x < y:
        formula = Implies(start, invariant)
        assert is_unsat(Not(formula))
        if x < 0:
            x += 7
            # X_new = Plus(X, Int(7))
        else:
            x += 10
            # X_new = Plus(X, Int(10))
        if y < 0:
            y -= 10
            # Y_new = Minus(Y, Int(10))
        else:
            y += 3
            # Y_new = Plus(Y, Int(3))
        X_new = Ite(LT(X, Int(0)), Plus(X, Int(7)), Plus(X, Int(10)))
        Y_new = Ite(LT(Y, Int(0)), Minus(Y, Int(10)), Plus(Y, Int(3)))
        invariant2 = invariant.substitute({X: X_new, Y: Y_new})

        formula = Implies(And(invariant, start), invariant2)  # (5)
        print(formula.serialize())
        #start = start.substitute({X: X_new, Y: Y_new})
        #X2 = X2.substitute({X: X_new})
        #Y2 = Y2.substitute({Y: Y_new})
        assert is_unsat(Not(formula))
        if is_unsat(Not(formula)):
            print("(5) holds (is a tautology) => invariant reestablished")
    post = And(LE(Y, X), LE(X, Plus(Y+Int(16))))  # (y <= x <= y + 16)
    formula = And(invariant, Not(start), Not(post))  # (6)
    # print(formula.serialize())
    # print(get_model(Not(formula)))
    assert is_unsat(formula)
    if is_unsat(formula):
        print("(6) is unsat as expected")


def test_invariant(invariant):
    x = random.randint(-100, 100)
    y = x + random.randint(1, 100)
    print('\nTesting invariant: {}. Values: x={} and y={}'.format(invariant, x, y))
    func(x, y, X, Y, invariant=invariant)


###
# Testing invariants
###

# inputs
X = Symbol('x', INT)
Y = Symbol('y', INT)

# this invariant seems to be correct
correct_invariant = LE(X, Plus(Y, Int(16)))

# this invariant fails after some tries
incorrect_invariant = LE(X, Plus(Y, Int(15)))

# test invariant
test_invariant(correct_invariant)


###
# Testing other stuff
###

# B = Symbol('b', BOOL)

# formula = And(LE(Plus(Y, Int(3)), Plus(X, Int(10))), LE(X, Y))
# print(formula)
# print('SAT', is_sat(formula))
# print('UNSAT', is_unsat(formula))

# formula = Not(And(LE(Plus(Y, Int(3)), Plus(X, Int(10))), LE(X, Y)))
# print(formula)
# print('SAT', is_sat(formula))
# print('UNSAT', is_unsat(formula))

# formula = Implies(LE(X, Y), LE(X, Plus(Y, Int(16))))
# formula = Not(formula)
# print(formula)
# print(is_unsat(formula))
