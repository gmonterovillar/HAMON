##============================ opti_config_ex_4.py ================================

# Config file for the minimization of f1(x) and f2(x) of the TNK function:
# f1(x) = x_1
# f2(x) = x_2
# Subjected to the following constraints:
# x_1^2 - x_2^2 + 1 + 0.1cos(16arctan(x_1/x_2)) < 0
# (x_1 - 0.5)^2 + (x_2 - 0.5)^2 - 0.5 < 0
# Both x_1 and x_2 in the range (0, pi]

print('Minimizing both f1(x) and f2(x) of the TNK function\n')

var_range = [[0, 3.1415926535]]*2
project_name = 'ex_4'
var_names = ['x', 'y']
lim_range_orig = [('lower', 0.0)]*2
max_min = ['min', 'min']
analytical_funcs = True
working_directory = '.'
plotting = True
true_pareto = True

def getFunctionsAnalytical():
    import numpy as np
    def of1(*vars):
        return vars[0]

    def of2(*vars):
        return vars[1]

    def l1(*vars):
        if vars[1] < 1e-9: # to avoid possible division by zero
            return 1
        else:
            return -vars[0] ** 2 - vars[1] ** 2 + 1 + 0.1 * np.cos(16 * np.arctan(vars[0] / vars[1]))

    def l2(*vars):
        return (vars[0] - 0.5) ** 2 + (vars[1] - 0.5) ** 2 - 0.5

    return [[of1, of2], [l1, l2]]
