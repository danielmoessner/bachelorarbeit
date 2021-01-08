from pysmt.shortcuts import Symbol, LE, GE, Int, GT, LT, And, Equals, Plus, Solver, is_sat, Or, Not, Minus, Ite, Implies, is_unsat, get_model, Times, Not, simplify
from utils import get_var


###
# Example programs from the paper
###
code_1 = {
    'pre': LT(get_var('x', 1), get_var('y', 1)),
    'cond': LT(get_var('x', 1), get_var('y', 1)),
    'body': And(
        Ite(
            LT(get_var('x', 1), Int(0)),
            Equals(
                get_var('x', 2),
                Plus(get_var('x', 1), Int(7))
            ),
            Equals(
                get_var('x', 2),
                Plus(get_var('x', 1), Int(10))
            )
        ),
        Ite(
            LT(get_var('y', 1), Int(0)),
            Equals(
                get_var('y', 2),
                Minus(get_var('y', 1), Int(10))
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
    'paths': [
        LT(get_var('x', 1), Int(0)),
        LT(get_var('y', 1), Int(0))
    ],
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

code_2 = {
    'pre': Or(
        GT(get_var('x', 1), Int(0)), 
        GT(get_var('y', 1), Int(0))
    ),
    'cond': LE(
        Plus(get_var('x', 1), get_var('y', 1)), 
        Int(-2)
    ),
    'body': Ite(
        GT(get_var('x', 1), Int(0)),
        And(
            Equals(get_var('x', 2), Plus(get_var('x', 1), Int(1))),
            Equals(get_var('y', 2), get_var('y', 1))
        ),
        And(
            Equals(get_var('y', 2), Plus(get_var('y', 1), Int(1))),
            Equals(get_var('x', 2), get_var('x', 1))
        )
    ),
    'post': Or(
        GT(get_var('x', 2), Int(0)), 
        GT(get_var('y', 2), Int(0))
    ),
    'paths': [
        GT(get_var('x'), Int(0))
    ],
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

code_3 = {
    'pre': And(
        Equals(get_var('x', 1), Int(1)), 
        Equals(get_var('y', 1), Int(0))
    ),
    'cond': LT(get_var('x', 1), Int(3)),  # while(*)
    'body': And(
        Equals(get_var('x', 2), Plus(get_var('x', 1), get_var('y', 1))),
        Equals(get_var('y', 2), Plus(get_var('y', 1), Int(1)))
    ),
    'post': GE(get_var('x', 2), get_var('y', 2)),
    'paths': [],
    'map': {
        'x': {
            'pre': 1,
            'body': 2,
        },
        'y': {
            'pre': 1,
            'body': 2,
        }
    }
}

code_4 = {
    'pre': LT(get_var('x', 1), Int(0)),
    'cond': LT(get_var('x', 1), Int(0)),
    'body': And(
        Equals(
            get_var('x', 2),
            Plus(get_var('x', 1), get_var('y', 1))
        ),
        Equals(
            get_var('y', 2),
            Plus(get_var('y', 1), Int(1))
        )
    ),
    'post': GT(get_var('y', 2), Int(0)),
    'paths': [],
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