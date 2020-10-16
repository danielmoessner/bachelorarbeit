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
        'GENERATE': {
            'START': 40,
            'ZONE': 100
        },
        'X': {
            'START': -32,
            'END': 32
        },
        'Y': {
            'START': -32,
            'END': 32
        },
        'MARGIN_MULTIPLIER': 5
    }
}


###
# Helper functions
###
def get_var(name, index=None):
    if index is None:
        return Symbol(name, INT)
    return Symbol(name + str(index), INT)


def get_variables_from_formula(formula, index='lowest'):
    assert index == 'lowest' or index == 'highest'
    variables = get_model(formula).__iter__()
    values = {}
    for variable in variables:
        name = variable[0].serialize()
        key = name[0]
        height = int(name[1:])
        value = int(variable[1].serialize())
        if index == 'lowest' and key in values.keys() and values[key]['height'] < height:
            continue
        if index == 'highest' and key in values.keys() and values[key]['height'] > height:
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
        return (False, get_variables_from_formula(formula))

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
        return (False, get_variables_from_formula(formula))

    # test (6)
    formula = And(
        invariant.substitute(get_substitution(code, 'body')),
        Not(code['cond'].substitute(get_substitution(code, 'body', True))),
        Not(code['post'])
    )
    if is_sat(formula):
        return (False, get_variables_from_formula(formula))

    return (True, )


def evaluate(code, variables):
    # s := variables
    numbers = And()
    for key, item in variables.items():
        numbers = And(numbers, Equals(get_var(key), Int(item)))

    # s ∈ pre
    formula = And(
        code['pre'],
        numbers.substitute(get_substitution(code, 'pre'))
    )
    pre = is_sat(formula)

    # s ⇒ s'
    def body(variables):
        numbers = And()
        for key, item in variables.items():
            numbers = And(numbers, Equals(get_var(key), Int(item)))

        cond = And(
            code['cond'],
            numbers.substitute(get_substitution(code, 'pre'))
        )
        if is_sat(cond):
            formula = And(
                code['body'],
                numbers.substitute(get_substitution(code, 'pre'))
            )
            variables = get_variables_from_formula(formula, 'highest')
            return body(variables)

        return variables

    # s' := variables
    variables = body(variables)
    numbers = And()
    for key, item in variables.items():
        numbers = And(numbers, Equals(get_var(key), Int(item)))

    # s' ∈ cond
    formula = And(
        code['cond'],
        numbers.substitute(get_substitution(code, 'pre'))
    )
    cond = is_sat(formula)

    # s' ∈ post
    formula = And(
        code['post'],
        numbers.substitute(get_substitution(code, 'body'))
    )
    post = is_sat(formula)

    # evaluate
    if pre and not cond and not post:
        # CE = { s ∈ SP | s ∈ Pre ∧ s ⇒ s' ∧ s' !∈ Cond ∧ s' !∈ Post }
        return 'CE'
    if pre and not cond and post:
        # POSITIVE = { s ∈ SP | s ∈ Pre ∧ s ⇒ s' ∧ s' !∈ Cond ∧ s' ∈ Post }
        return 'POSITIVE'
    if not pre and not cond and not post:
        # NEGATIVE = { s ∈ SP | s !∈ Pre ∧ s ⇒ s' ∧ s' !∈ Cond ∧ s' !∈ Post }
        return 'NEGATIVE'
    # NP = SP - CE - POSITIVE - NEGATIVE
    return 'NP'


###
# Evaluate points
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

        # points.append((x, y))
        # this is wrong
        #
        # example:
        # x = -12, y = -8
        # pre is satisfied, cond is satisfied
        #
        # x and y become:
        # x = -5, y = -18
        # cond is not satisfied, post is satisfied
        #
        # now this function returns 'POSITIVE'
        # but the point (-5, -18) should not be positive
        # (-5, -18) is 'NEGATIVE'

    post_violated = not (y <= x and x <= y + 16)
    if post_violated:
        if pre_violated:
            return ('NEGATIVE', points)
        return ('CE', points)
    if pre_violated:
        # return ('NEGATIVE', points)
        return ('NP', points)
    return ('POSITIVE', points)


###
# Verify function
# Finds correct invariants
###
def verify(code):
    SP = {}
    SP['CE'], SP['NEGATIVE'], SP['NP'], SP['POSITIVE'], SP['UNKNOWN'] = (
        [], [], [], [], []
    )

    # generate points
    for _ in range(0, SETTINGS['POINTS']['GENERATE']['START']):
        x = random.randint(SETTINGS['POINTS']['X']['START'],
                           SETTINGS['POINTS']['X']['END'])
        y = random.randint(SETTINGS['POINTS']['Y']['START'],
                           SETTINGS['POINTS']['Y']['END'])
        point = (x, y)
        SP['UNKNOWN'].append(point)

    # find an invariant
    while True:
        # evaluate points
        for point in SP['UNKNOWN']:
            evaluation = evaluate(code, {'x': point[0], 'y': point[1]})
            SP[evaluation].append(point)
        SP['UNKNOWN'] = []

        # get a possible invariant
        invariant = activeLearn(SP)
        if not invariant[0]:
            return 'DISPROVED'

        # check if the invariant is actually correct
        correct = is_invariant_correct(code_1, invariant[1])
        if correct[0]:
            return invariant[1]

        # add points to sp
        # point with which the invariant failed, this line actually does not have a big impact
        SP['UNKNOWN'].append((correct[1]['x'], correct[1]['y']))
        # points which are in the margin zone of the support vector machine
        SP['UNKNOWN'] = invariant[2]


def activeLearn(SP):
    # safety check
    if len(SP['CE']) != 0:
        return (False,)

    # shape the data for the support vector machine
    x = SP['POSITIVE'] + SP['NEGATIVE']
    y = len(SP['POSITIVE']) * [1] + len(SP['NEGATIVE']) * [0]
    x = np.array(x)
    y = np.array(y)
    clf = svm.SVC(kernel='linear', C=1000)
    clf.fit(x, y)
    print('POSITIVE', '(yellow)', len(y[y == 1]))
    print('NEGATIVE', '(purple)', len(y[y == 0]))
    print('NP      ', '(blue)  ', len(SP['NP']))

    # calculate the seperating line
    W = clf.coef_[0]
    I = clf.intercept_
    a = int(round(-W[0] / W[1]))
    b = int(round(I[0] / W[1]))
    def line(x): return a*x - b

    # margin calculation
    margin = int(round(1 / np.linalg.norm(clf.coef_)) *
                 SETTINGS['POINTS']['MARGIN_MULTIPLIER'])

    # check wheter <= or >= is correct
    if clf.predict([(1, line(1) - 1)]) == 0:
        invariant = LE(
            Minus(Times(Int(a), Symbol('x', INT)), Int(b)),
            Symbol('y', INT)
        )
    else:
        invariant = GE(
            Minus(Times(Int(a), Symbol('x', INT)), Int(b)),
            Symbol('y', INT)
        )
    print(invariant, '\n')

    # generate points in the seperation zone
    points = []
    for _ in range(0, SETTINGS['POINTS']['GENERATE']['ZONE']):
        xp = random.randint(SETTINGS['POINTS']['X']['START'],
                            SETTINGS['POINTS']['Y']['END'])
        yp = line(xp) + random.randint(-margin, margin)
        points.append((xp, yp))

    # draw a plot of the data; helps visualizing what is happening
    z = np.array(SP['NP'])
    plt.scatter(z[:, 0], z[:, 1])
    plt.scatter(x[:, 0], x[:, 1], c=y, s=30)
    # plot the` decision function
    ax = plt.gca()
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    # create grid to evaluate model
    xx = np.linspace(xlim[0], xlim[1], 30)
    yy = np.linspace(ylim[0], ylim[1], 30)
    YY, XX = np.meshgrid(yy, xx)
    xy = np.vstack([XX.ravel(), YY.ravel()]).T
    Z = clf.decision_function(xy).reshape(XX.shape)
    # plot decision boundary and margins
    ax.contour(XX, YY, Z, colors='k', levels=[-1, 0, 1], alpha=0.5,
               linestyles=['--', '-', '--'])
    # plot support vectors
    ax.scatter(clf.support_vectors_[:, 0], clf.support_vectors_[:, 1], s=100,
               linewidth=1, facecolors='none', edgecolors='k')
    # plt.show()

    # return found invariant and points in the seperation zone
    return (True, invariant, points)


###
# Test code
###

# correct_invariant = LE(Symbol('x', INT), Plus(Symbol('y', INT), Int(16)))
# incorrect_invariant = LE(Symbol('x', INT), Plus(Symbol('y', INT), Int(9)))
# print(is_invariant_correct(code_1, incorrect_invariant))

print(verify(code_1))

# print(evaluate_point(-5, -18))
# print(evaluate_point(-12, -10))
# SP = {}
# SP['UNKNOWN'] = []
# for _ in range(0, SETTINGS['POINTS']['GENERATE']['START']):
#     x = random.randint(SETTINGS['POINTS']['X']['START'],
#                        SETTINGS['POINTS']['X']['END'])
#     y = random.randint(SETTINGS['POINTS']['Y']['START'],
#                        SETTINGS['POINTS']['Y']['END'])
#     point = (x, y)
#     SP['UNKNOWN'].append(point)

# for point in SP['UNKNOWN']:
#     print(evaluate_point(*point),
#           evaluate(code_1, {'x': point[0], 'y': point[1]}))

# print(evaluate(code_1, {'x': -18, 'y': 24}))

# print(evaluate_point(-18, -29))
# print(evaluate_point(-19, -29))
# print(evaluate_point(-19, -32))
