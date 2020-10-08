import random
import pysmt
from pysmt.shortcuts import Symbol, LE, GE, Int, GT, LT, And, Equals, Plus, Solver, is_sat, Or, Not, Minus, Ite, Implies, is_unsat, get_model, Times
from pysmt.typing import INT, STRING, BOOL, REAL
from sklearn import svm
import matplotlib.pyplot as plt
import numpy as np


SETTINGS = {
    'POINTS': {
        'GENERATE': 40,
        'X': {
            'START': -32,
            'END': 32
        },
        'Y': {
            'START': -32,
            'END': 32
        }
    }
}


def is_invariant_correct(invariant):
    X = Symbol('x', INT)
    Y = Symbol('y', INT)

    # test (4)
    pre = LT(X, Y)
    formula = And(pre, Not(invariant))
    print(formula.serialize())
    if is_sat(formula):
        return False

    # test (5)
    cond = LT(X, Y)
    X_new = Ite(LT(X, Int(0)), Plus(X, Int(7)), Plus(X, Int(10)))
    Y_new = Ite(LT(Y, Int(0)), Minus(Y, Int(10)), Plus(Y, Int(3)))
    invariant_new = invariant.substitute({X: X_new, Y: Y_new})
    formula = And(Implies(And(cond, invariant), invariant_new), Not(invariant))
    print(formula.serialize())
    if is_sat(Not(formula)):
        return False

    # test (6)
    post = GE(X, Y)
    formula = And(invariant, Not(cond), Not(post))
    print(formula.serialize())
    if is_sat(formula):
        return False

    return True


# correct_invariant = LE(Symbol('x', INT), Plus(Symbol('y', INT), Int(16)))
# incorrect_invariant = LE(Symbol('x', INT), Plus(Symbol('y', INT), Int(19)))
# print(is_invariant_correct(incorrect_invariant))


def check_invariant(x, y, invariant):
    X = Symbol('x', INT)
    Y = Symbol('y', INT)
    assert x < y

    # precondition
    start = LT(X, Y)

    # check invariant holds before the loop
    formula = Implies(start, invariant)
    assert is_unsat(Not(formula))

    # check (4)
    # assert is_unsat(And(start, Not(invariant)))
    print(x, y)
    print(evaluate_point(x, y))
    while x < y:
        # while loop condition
        start = LT(X, Y)

        # check invariant holds at the beginning of the loop
        formula = Implies(
            start,
            invariant.substitute({Symbol('x', INT): X, Symbol('y', INT): Y})
        )
        assert is_unsat(Not(formula))

        # while loop body
        if x < 0:
            x += 7
        else:
            x += 10
        if y < 0:
            y -= 10
        else:
            y += 3
        X = Ite(LT(X, Int(0)), Plus(X, Int(7)), Plus(X, Int(10)))
        Y = Ite(LT(Y, Int(0)), Minus(Y, Int(10)), Plus(Y, Int(3)))

        # check invariant holds at the end of the loop
        formula = Implies(
            start,
            invariant.substitute({Symbol('x', INT): X, Symbol('y', INT): Y})
        )
        assert is_unsat(Not(formula))

        # check (5)
        # assert is_unsat(
        #     And(
        #         And(
        #             invariant.substitute(
        #                 {Symbol('x', INT): X, Symbol('y', INT): Y}),
        #             start
        #         ),
        #         Not(invariant)
        #     )
        # )

    # check invariant holds after the loop
    post = And(LE(Y, X), LE(X, Plus(Y, Int(16))))
    formula = Implies(And(post, start), invariant.substitute(
        {Symbol('x', INT): X, Symbol('y', INT): Y}))
    assert is_unsat(Not(formula))

    # check (6)
    start = LT(Symbol('x', INT), Symbol('y', INT))
    post = And(
        LE(Symbol('y', INT), Symbol('x', INT)),
        LE(Symbol('x', INT), Plus(Symbol('y', INT), Int(16)))
    )
    formula = And(invariant, Not(start), Not(post))
    assert is_unsat(formula)


def evaluate_point(x, y):
    points = [(x, y)]

    pre_violated = False
    if not (x < y):
        pre_violated = True

    while x < y:

        if x < 0:
            x += 7
        else:
            x += 10
        if y < 0:
            y -= 10
        else:
            y += 3

        points.append((x, y))

    if not (y <= x and x <= y + 16):
        if pre_violated:
            return ('NEGATIVE', points)
        return ('CE', points)
    if pre_violated:
        # return ('NEGATIVE', points)
        return ('NP', points)
    return ('POSITIVE', points)


def test_invariant(invariant):
    x = random.randint(-100, 100)
    y = x + random.randint(1, 20)
    try:
        check_invariant(x, y, invariant)
    except:
        return (False, (x, y))
    return (True, )


def verify():
    SP = {}
    SP['UNKNOWN'] = [
        (random.randint(SETTINGS['POINTS']['X']['START'], SETTINGS['POINTS']['X']['END']), random.randint(
            SETTINGS['POINTS']['Y']['START'], SETTINGS['POINTS']['Y']['END']))
        for _ in range(0, SETTINGS['POINTS']['GENERATE'])
    ]
    # SP['UNKNOWN'] += [(1, 2), (10, 1), (100, 0)]
    SP['CE'], SP['NEGATIVE'], SP['NP'], SP['POSITIVE'] = ([], [], [], [])
    while True:
        for point in SP['UNKNOWN']:
            evaluation = evaluate_point(*point)
            SP[evaluation[0]] += evaluation[1]
        SP['UNKNOWN'] = []
        invariant = activeLearn(SP)
        if invariant[0]:
            proved = test_invariant(invariant[1])
            if proved[0]:
                return invariant[1]
            else:
                SP['UNKNOWN'] = invariant[2]
        else:
            return 'DISPROVED'


def activeLearn(SP):
    if len(SP['CE']) != 0:
        return (False,)
    x = SP['POSITIVE'] + SP['NEGATIVE']
    y = len(SP['POSITIVE']) * [1] + len(SP['NEGATIVE']) * [0]
    x = np.array(x)
    clf = svm.SVC(kernel='linear', C=1000)
    clf.fit(x, y)
    print(len(x))
    # print(SP)
    # print(x)
    # print(y)

    # plt.scatter(x[:, 0], x[:, 1], c=y, s=30)
    # # plot the` decision function
    # ax = plt.gca()
    # xlim = ax.get_xlim()
    # ylim = ax.get_ylim()
    # # create grid to evaluate model
    # xx = np.linspace(xlim[0], xlim[1], 30)
    # yy = np.linspace(ylim[0], ylim[1], 30)
    # YY, XX = np.meshgrid(yy, xx)
    # xy = np.vstack([XX.ravel(), YY.ravel()]).T
    # Z = clf.decision_function(xy).reshape(XX.shape)
    # # plot decision boundary and margins
    # ax.contour(XX, YY, Z, colors='k', levels=[-1, 0, 1], alpha=0.5,
    #            linestyles=['--', '-', '--'])
    # # plot support vectors
    # ax.scatter(clf.support_vectors_[:, 0], clf.support_vectors_[:, 1], s=100,
    #            linewidth=1, facecolors='none', edgecolors='k')
    # plt.show()

    W = clf.coef_[0]
    I = clf.intercept_
    # print('intercept', clf.intercept_)
    a = -W[0] / W[1]
    b = I[0] / W[1]
    # print(a, b)
    a = int(round(a))
    b = int(round(b))
    def line(x): return a*x - b
    if clf.predict([(1, line(1) - 1)]) == 0:
        invariant = LE(Minus(Times(Int(a), Symbol('x', INT)),
                             Int(b)), Symbol('y', INT))
    else:
        invariant = GE(Minus(Times(Int(a), Symbol('x', INT)),
                             Int(b)), Symbol('y', INT))
    print(invariant)
    points = []
    for _ in range(0, 10):
        x = random.randint(SETTINGS['POINTS']['X']
                           ['START'], SETTINGS['POINTS']['Y']['END'])
        y = line(x) + random.randint(-20, 20)
        points.append((x, y))
    return (True, invariant, points)


# print(verify())


###
# Testing invariants
###

# inputs
# X = Symbol('x', INT)
# Y = Symbol('y', INT)

# function to test invariant
# def test_invariant(invariant):
#     x = random.randint(-100, 100)
#     y = x + random.randint(1, 20)
#     print('\nTesting invariant: {}. Values: x={} and y={}'.format(invariant, x, y))
#     func(x, y, X, Y, invariant=invariant)

# this invariant seems to be correct
correct_invariant = LE(Symbol('x', INT), Plus(Symbol('y', INT), Int(16)))
# check_invariant(1, 10, correct_invariant)

# this invariant fails after some tries
incorrect_invariant = LE(Symbol('x', INT), Plus(Symbol('y', INT), Int(19)))

# test invariant
# test_invariant(incorrect_invariant)
# print(is_invariant_correct(incorrect_invariant))
