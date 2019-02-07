##============================ opti_config_ex_2.py ================================

# Config file for the minimization of Golinski's spped reducer problem[1].
# It has eleven constraints

# References:
# [1] - Ray,T., “Golinski’s Speed Reducer Problem Revisited,” AIAA journal, Vol.41, No.3, 2003

print('Minimizing Golinski\'s spped reducer problem. The minimum value is around 2994.4\n')

n_of = 1
n_var = 7
var_range = [[2.6, 3.6], [0.7, 0.8], [17.0, 28.0], [7.3, 8.3], [7.3, 8.3], [2.9, 3.9], [5.0, 5.5]]
n_lim = 11
any_int_var = True
int_var_indexes = [2]
project_name = 'ex_2'
var_names = ['x_1', 'x_2', 'x_3', 'x_4', 'x_5', 'x_6', 'x_7']
of_names = ['of_1']
lim_var_names = []
lim_range_orig = [('lower', 0.0)]*11
range_gen = 0
mod_lim_range = []
max_min = ['min']
analytical_funcs = True
working_directory = '.'
plotting = True


def getFunctionsAnalytical():
    def of(*vars):
        return 0.7854 * vars[0] * vars[1] ** 2 * (3.3333 * vars[2] ** 2 + 14.9334 * vars[2] - 43.0934) - 1.508 * vars[
            0] * (
                       vars[5] ** 2 + vars[6] ** 2) + 7.477 * (vars[5] ** 3 + vars[6] ** 3) + 0.7854 * (
                       vars[3] * vars[5] ** 2 + vars[4] * vars[6] ** 2)

    def l1(*vars):
        return 27 - vars[0] * vars[1] ** 2 * vars[2]

    def l2(*vars):
        return 397.5 - vars[0] * vars[1] ** 2 * vars[2] ** 2

    def l3(*vars):
        return 1.93 * vars[3] ** 3 - vars[1] * vars[2] * vars[5] ** 4

    def l4(*vars):
        return 1.93 * vars[4] ** 3 - vars[1] * vars[2] * vars[6] ** 4

    def l5(*vars):
        return ((745 * vars[3] / (vars[1] * vars[2])) ** 2 + 16.9 * 10 ** 6) ** 0.5 - 110 * vars[5] ** 3

    def l6(*vars):
        return ((745 * vars[4] / (vars[1] * vars[2])) ** 2 + 157.5 * 10 ** 6) ** 0.5 - 85 * vars[6] ** 3

    def l7(*vars):
        return vars[1] * vars[2] - 40

    def l8(*vars):
        return 5 * vars[1] - vars[0]

    def l9(*vars):
        return vars[0] - 12 * vars[1]

    def l10(*vars):
        return 1.5 * vars[5] - vars[3] + 1.9

    def l11(*vars):
        return 1.1 * vars[6] - vars[4] + 1.9


    return [[of], [l1, l2, l3, l4, l5, l6, l7, l8, l9, l10, l11]]
