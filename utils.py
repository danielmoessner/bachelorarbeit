import numpy as np
import math
from settings import SETTINGS
from pysmt.shortcuts import Symbol, LE, GE, Int, GT, LT, And, Equals, Plus, Solver, is_sat, Or, Not, Minus, Ite, Implies, is_unsat, get_model, Times, Not, simplify
from pysmt.typing import INT, STRING, BOOL, REAL
import matplotlib.pyplot as plt


###
# Helper functions
###
def get_mirror_point(a, b, c, x1, y1): 
    if (a * a + b * b) == 0:
        return np.empty((0, 2), int)
    if (a * x1 + b * y1 + c) == 0:
        return np.array([
            [x1 - SETTINGS['POINTS']['MIRROR_ADD'], y1], 
            [x1 + SETTINGS['POINTS']['MIRROR_ADD'], y1], 
            [x1, y1 - SETTINGS['POINTS']['MIRROR_ADD']], 
            [x1, y1 + SETTINGS['POINTS']['MIRROR_ADD']]
        ])
    temp = -2 * (a * x1 + b * y1 + c) / (a * a + b * b)
    x = temp * a + x1
    y = temp * b + y1 
    x = math.ceil(x) if x > x1 else math.floor(x)
    y = math.ceil(y) if y > y1 else math.floor(y)
    x = int(x)
    y = int(y)
    return np.array([x, y], int)


def plot_sp(single_points, clf=None):
    # draw a plot of the data; helps visualizing what is happening
    POSITIVE = np.array(single_points['POSITIVE'])
    NEGATIVE = np.array(single_points['NEGATIVE'])
    NP = np.array(single_points['NP'])
    plt.scatter(NP[:, 0], NP[:, 1], s=30)
    plt.scatter(NEGATIVE[:, 0], NEGATIVE[:, 1], s=30)
    plt.scatter(POSITIVE[:, 0], POSITIVE[:, 1], s=30)
    # plot the` decision function
    ax = plt.gca()
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    # plot margin if clf exists
    if clf is not None:
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
        # my special line
        # plt.plot([0, -clf.intercept_ / clf.coef_[0][0]], [-clf.intercept_ / clf.coef_[0][1], 0])
    plt.show()


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


def find_points_from_formula(formula, n_points=20):
    points = []
    while (len(points) < n_points):
        print(get_model(formula))
        raise Exception()
    return points
