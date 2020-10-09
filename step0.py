import random
import pysmt
from pysmt.shortcuts import Symbol, LE, GE, Int, GT, LT, And, Equals, Plus, Solver, is_sat, Or, Not, Minus, Ite, Implies, is_unsat, get_model, Times
from pysmt.typing import INT, STRING, BOOL, REAL
from sklearn import svm
import matplotlib.pyplot as plt
import numpy as np


###
# Settings
###
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


###
# Helper functions
###
def get_var(name, index=None):
    if index is None:
        return Symbol(name, INT)
    return Symbol(name + str(index), INT)


def get_lowest_variables(variables):
    values = {}
    for variable in variables:
        name = variable[0].serialize()
        key = name[0]
        height = int(name[1:])
        value = int(variable[1].serialize())
        if key in values.keys() and values[key]['height'] < height:
            continue
        values[key] = {
            'value': value,
            'height': height
        }
    variables = {}
    for key, value in values.items():
        variables[key] = value['value']
    return variables


###
# Example programs from the paper
###
code_1 = {
    'pre': LT(get_var('x', 1), get_var('y', 1)),
    'cond': LT(get_var('x', 1), get_var('y', 1)),
    'body': And(
        Or(
            Equals(
                get_var('x', 2),
                Plus(get_var('x', 1), Int(7))
            ),
            Equals(
                get_var('x', 2),
                Plus(get_var('x', 1), Int(10))
            )
        ),
        Or(
            And(
                Equals(
                    get_var('y', 2),
                    Minus(get_var('y', 1), Int(10))
                ),
                Equals(
                    get_var('x', 2),
                    Plus(get_var('x', 1), Int(7))
                ),
            ),
            Equals(
                get_var('y', 2),
                Plus(get_var('y', 1), Int(3))
            ),
        )
    ),
    'post': And(
        LE(get_var('y', 2), get_var('x', 2)),
        LE(get_var('x', 2), Plus(get_var('y', 2), Int(16)))
    ),
    'map': {
        'x': {
            'pre': 1,
            'body': 2
        },
        'y': {
            'pre': 1,
            'body': 2
        }
    }
}


###
# Invariant check
###
def get_substitution(code, place='body', replace_index=False):
    substitution = {}
    for key in code['map'].keys():
        index = code['map'][key]['pre'] if replace_index else None
        if place == 'body':
            substitution[get_var(key, index)] = get_var(
                key, code['map'][key]['body'])
        elif place == 'pre':
            substitution[get_var(key, index)] = get_var(
                key, code['map'][key]['pre'])
        else:
            raise Exception("Place needs to be 'body' or 'pre'.")
    return substitution


def is_invariant_correct(code, invariant):
    # test (4)
    formula = And(
        code['pre'],
        Not(invariant.substitute(get_substitution(code, 'pre')))
    )
    if is_sat(formula):
        return (False, get_lowest_variables(get_model(formula).__iter__()))

    # test (5)
    sp = And(
        code['cond'],
        code['body'],
        invariant.substitute(get_substitution(code, 'pre'))
    )
    formula = And(
        sp,
        Not(invariant.substitute(get_substitution(code, 'body')))
    )
    if is_sat(formula):
        # print(get_model(formula).get_values(formula))
        return (False, get_lowest_variables(get_model(formula).__iter__()))

    # test (6)
    formula = And(
        invariant.substitute(get_substitution(code, 'body')),
        Not(code['cond'].substitute(get_substitution(code, 'body', True))),
        Not(code['post'])
    )
    if is_sat(formula):
        return (False, get_lowest_variables(get_model(formula).__iter__()))

    return (True, )


###
# Other
###
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
        # TODO
        # check_invariant(x, y, invariant)
        pass
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


###
# Test code
###
correct_invariant = LE(Symbol('x', INT), Plus(Symbol('y', INT), Int(16)))
incorrect_invariant = LE(Symbol('x', INT), Plus(Symbol('y', INT), Int(9)))
print(is_invariant_correct(code_1, incorrect_invariant))
