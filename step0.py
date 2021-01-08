from pysmt.shortcuts import Symbol, LE, GE, Int, GT, LT, And, Equals, Plus, Solver, is_sat, Or, Not, Minus, Ite, Implies, is_unsat, get_model, Times, Not, simplify
from pysmt.typing import INT, STRING, BOOL, REAL
from sklearn import svm
import numpy as np
from settings import SETTINGS
from programs import code_1, code_2, code_3, code_4
from utils import get_var, get_mirror_point, plot_sp, get_variables_from_formula


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
    # pre ∧ ¬invariant
    formula = And(
        code['pre'],
        Not(invariant.substitute(get_substitution(code, 'pre')))
    )
    if is_sat(formula):
        return (False, get_variables_from_formula(formula))

    # test (5)
    # sp(invariant ∧ cond, body) ∧ ¬invariant
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
    # invariant ∧ ¬cond ∧ ¬post
    formula = And(
        invariant.substitute(get_substitution(code, 'body')),
        Not(code['cond'].substitute(get_substitution(code, 'body', True))),
        Not(code['post'])
    )
    if is_sat(formula):
        return (False, get_variables_from_formula(formula))

    return (True, ())


def evaluate_point(code, variables):
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
    # return all s and s'
    def body(variables):
        variables_list = [variables]

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
            variables_list += body(variables)

        return variables_list

    # s' := last point in variables list
    variables_list = body(variables)
    numbers = And()
    for key, item in variables_list[-1].items():
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
        # CE = { s ∈ Pre ∧ s ⇒ s' ∧ s' !∈ Cond ∧ s' !∈ Post }
        evaluation = 'CE' 
    elif pre and not cond and post:
        # POSITIVE = { s ∈ Pre ∧ s ⇒ s' ∧ s' !∈ Cond ∧ s' ∈ Post }
        evaluation = 'POSITIVE'
    elif not pre and not cond and not post:
        # NEGATIVE = { s !∈ Pre ∧ s ⇒ s' ∧ s' !∈ Cond ∧ s' !∈ Post }
        evaluation = 'NEGATIVE'
    else:
        # NP = REST
        evaluation = 'NP'
    return (evaluation, variables_list)


###
# Verify function
# Finds correct invariants
###
def verify(code):
    single_points = {}
    for valuation in ['CE', 'NEGATIVE', 'NP', 'POSITIVE', 'UNKNOWN']:
        single_points[valuation] = np.empty((0,2), int)

    # generate points
    unknown = np.random.randint(
        low = SETTINGS['POINTS']['GENERATE']['LOW'], 
        high = SETTINGS['POINTS']['GENERATE']['HIGH'],
        size = (SETTINGS['POINTS']['GENERATE']['START'], 2),
        dtype=int
    )
    single_points['UNKNOWN'] = unknown

    # find an invariant
    while True:
        # evaluate points
        for point in single_points['UNKNOWN']:
            evaluation, points = evaluate_point(code, {'x': int(point[0]), 'y': int(point[1])})
            points = np.array(list(map(lambda point: [point['x'], point['y']], points)))
            single_points[evaluation] = np.append(single_points[evaluation], points, axis=0)
        single_points['UNKNOWN'] = np.empty((0,2), int)
        
        # break if disproved
        if len(single_points['CE']) != 0:
            return 'DISPROVED'

        # get a possible invariant
        # invariant, hesse_normal_forms = find_conjunctive_invariant(single_points)
        invariant, hesse_normal_forms = find_disjunctive_invariant(single_points, code)

        # print
        if SETTINGS['PRINT']:
            print(
                SETTINGS['#'], 'testing invariant\n',
                invariant.serialize()
            )

        # check if the invariant is actually correct
        invariant_correct, error_point = is_invariant_correct(code, invariant)
        
        # return invariant if correct
        if invariant_correct:
            return invariant
        
        # calculate mirror points to hesse forms and add to sp
        error_points = np.empty((0, 2), int)
        error_point = np.array([error_point['x'], error_point['y']], dtype=int)
        error_points = np.vstack([error_points, error_point])
        for form in hesse_normal_forms:
            error_points = np.vstack([error_points, get_mirror_point(*form, *error_point)])

        # print
        if SETTINGS['PRINT']:
            print(
                SETTINGS['#'], 'verify error_points\n',
                error_points
            )
        
        # add the error points
        single_points['UNKNOWN'] = np.append(single_points['UNKNOWN'], error_points, axis=0)
        

def find_conjunctive_invariant(single_points):
    # print
    if SETTINGS['PRINT']:
        print(SETTINGS['#'], 'find_conjunctive_invariant single_points')
        print('POSITIVE', '(green) ', len(single_points['POSITIVE']))
        print('NEGATIVE', '(orange)', len(single_points['NEGATIVE']))
        print('NP      ', '(blue)  ', len(single_points['NP']))
        print('TOTAL            ', len(single_points['POSITIVE']) + len(single_points['NEGATIVE']) + len(single_points['NP']))
    
    # plot
    if SETTINGS['PLOT']:
        plot_sp(single_points)

    complete_invariant = And()
    negative = single_points['NEGATIVE']
    positive = single_points['POSITIVE']
    hesse_normal_forms = []

    while(len(negative) != 0):

        # shape the data for the support vector machine
        random_negative_point = negative[np.random.choice(len(negative)), :]
        x = np.vstack([positive, random_negative_point])
        y = np.append(np.ones(len(positive), int), np.array([0]))

        # run the support vector machine
        clf = svm.SVC(kernel='linear', C=1000)
        clf.fit(x, y)

        # calculate the hesse normal form
        a = int(round(clf.coef_[0][0] * SETTINGS['HESSE_FORM_MULTIPLIER']))
        b = int(round(clf.coef_[0][1] * SETTINGS['HESSE_FORM_MULTIPLIER']))
        c = int(round(clf.intercept_[0] * SETTINGS['HESSE_FORM_MULTIPLIER']))
        
        # save the hesse normal form for later
        hesse_normal_forms.append((a, b, c))

        # set the invariant that correctly classifies positive points
        invariant = GT(
            Plus(
                Times(Int(a), get_var('x')),
                Times(Int(b), get_var('y')), 
                Int(c)
            ), 
            Int(0)
        )

        # remove successfully classified from negative
        prediction = clf.predict(negative)
        negative = negative[prediction > 0]
        
        # plot
        if SETTINGS['PLOT']:
            plot_sp(single_points, clf)
        
        # combine all invariants
        complete_invariant = And(complete_invariant, invariant)
    
    # print
    if SETTINGS['PRINT']:
        print(
            SETTINGS['#'], 'find_conjunctive_invariant invariant\n',
            complete_invariant.serialize()
        )
    
    # return found invariant and points in the seperation zone
    return complete_invariant, hesse_normal_forms


def find_disjunctive_invariant(single_points, code):
    path_seperations = 2 ** len(code['paths'])
    # cond_seperation = 1
    cond_seperation = path_seperations
    single_points_seperated = (path_seperations + cond_seperation) * [[]]
    for i in range(path_seperations + cond_seperation):
        single_points_seperated[i] = {'POSITIVE': np.empty((0,2), int), 'NEGATIVE': np.empty((0,2), int)}
    
    cond = code['cond'].substitute({get_var('x1'): get_var('x'), get_var('y1'): get_var('y')})
    path_conditions = path_seperations * [cond] + cond_seperation * [Not(cond)]

    path_allocation = {}
    for i in range(len(code['paths'])):
        path_allocation[2**i] = code['paths'][i]

    for i in range(path_seperations):
        k = i
        while True:
            for key, path in path_allocation.items():
                if key > k:
                    path_conditions[i] = And(path_conditions[i], Not(path))
                else:
                    path_conditions[i] = And(path_conditions[i], path)
                    k -= key
            if k == 0:
                break
    
    if cond_seperation != 1:
        for i in range(path_seperations):
            k = i
            while True:
                for key, path in path_allocation.items():
                    if key > k:
                        path_conditions[i+2] = And(path_conditions[i+2], Not(path))
                    else:
                        path_conditions[i+2] = And(path_conditions[i+2], path)
                        k -= key
                if k == 0:
                    break

    for valuation in ['POSITIVE', 'NEGATIVE']:
        for point in single_points[valuation]:
            assert_check = False
            for i in range(len(path_conditions)):
                sat = is_sat(
                    And(
                        path_conditions[i], 
                        Equals(get_var('x'), Int(point[0])), 
                        Equals(get_var('y'), Int(point[1]))
                    )
                )
                assert_check = assert_check or sat
                if sat:
                    single_points_seperated[i][valuation] = (
                        np.vstack([single_points_seperated[i][valuation], point])
                    )
            assert assert_check == True

    all_hesse_normal_forms = []
    complete_invariant = Or()
    for i in range(len(single_points_seperated)):
        single_points_seperated[i]['NP'] = single_points['NP']
        single_points_seperated[i]['CE'] = single_points['CE']
        if len(single_points_seperated[i]['POSITIVE']) == 0 or len(single_points_seperated[i]['NEGATIVE']) == 0:
            invariant = And()
            hesse_normal_forms = []
        else:
            invariant, hesse_normal_forms = find_conjunctive_invariant(single_points_seperated[i])    
        all_hesse_normal_forms += hesse_normal_forms
        if SETTINGS['PRINT']:
            print(
                SETTINGS['#'], 'find_disjunctive_invariant path_condition\n',
                path_conditions[i].serialize()
            )
        invariant = And(invariant, path_conditions[i])
        complete_invariant = Or(complete_invariant, invariant)
    
    return complete_invariant, all_hesse_normal_forms


###
# Test code
###

# correct_invariant = LE(Symbol('x', INT), Plus(Symbol('y', INT), Int(16)))
# incorrect_invariant = LE(Symbol('x', INT), Plus(Symbol('y', INT), Int(9)))
# print(is_invariant_correct(code_1, incorrect_invariant))

test_code = code_1
print(SETTINGS['#'], 'final result\n', simplify(verify(test_code)).serialize())
# print(is_invariant_correct(test_code, Or()))
# print(evaluate(code_2, {'x': 0, 'y': -1}))
# print(evaluate_point(code_1, {'x': 323, 'y': 324}))
# single_points = {}
# single_points['UNKNOWN'] = []
# for _ in range(0, SETTINGS['POINTS']['GENERATE']['START']):
#     x = random.randint(SETTINGS['POINTS']['X']['START'],
#                        SETTINGS['POINTS']['X']['END'])
#     y = random.randint(SETTINGS['POINTS']['Y']['START'],
#                        SETTINGS['POINTS']['Y']['END'])
#     point = (x, y)
#     single_points['UNKNOWN'].append(point)

# print(evaluate(code_1, {'x': -18, 'y': 24}))
# left = Minus(Times(Int(1), Symbol('x', INT)), Int(18))
# right = Symbol('y', INT)
# formula = LE(left, right)
# find_points_from_formula(formula)


# print(mirror_point(1, -1, 0, 0, 0))
# print(mirror_point(0, 1, -10, 0, 0))
