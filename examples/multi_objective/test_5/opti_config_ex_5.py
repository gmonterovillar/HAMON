##============================ opti_config_ex_5.py ================================

# Config file for the minimization of f1(x) and f2(x) of the ZDT 1 function[1]:
# f1(x) = x_1
# f2(x) = g(x)[1-sqrt(x_1/g(x))]
# g(x) = 1+9(sum^30_{i=2} x_i)/29
# 30 variables all in the range of [0, 1]

# The same functions as for test_3 are minimized but in this case the RBF method is going to be used. This
# means that the evolutionary algorithm (EA) will not evaluate the analytical expressions directly,
# instead, and initial design set is constructed and a RBF fit to it. This RBF is passed to the EA to
# optimized on, the EA selects some design along the pareto front and the RBF is reconstructed with the
# Additional information. The EA is executed again ... this process is repeated several times. For more
# information please refer to [2][3]

# References:
# [1] - Zitzler, E., Deb, K., and Thiele, L., “Comparison of Multiobjective Evolutionary Algorithms:
#       Empirical Results,” Evolutionary Computation, Vol. 8, No. 2, 2000
# [2] - Montero Villar, G., Lindblad, D. , and Andersson, N., “Multi-Objective Optimization of an Counter
#       Rotating Open Rotor using Evolutionary Algorithms,” 2018 Multidisciplinary Analysis and Optimization
#       Conference, 2018.
# [3] - Montero Villar, G., Lindblad, D., & Andersson, N. (2019). Effect of Airfoil Parametrization on the
#       Optimization of Counter Rotating Open Rotors. In AIAA Scitech 2019 Forum

print('Minimizing both f1(x) and f2(x) of the ZDT 1 function using RBFs\n')

var_range = [[0, 1]] * 30
project_name = 'ex_5'
of_names = ['f1(x)', 'f2(x)']
max_min = ['min', 'min']
analytical_funcs = False
working_directory = '.'
plotting = True
true_pareto = True

# For the RBF and optimization loop set up
meta_model_type = 'RBF'
max_opti_loops = 5
data_base_file = 'data_base_ex_5.csv'
existing_data_base = False
n_LHS = 350
perc_construct = 0.8
eps_scale_range = 3
basis = ['multiquadric', 'gaussian', 'linear']
eps_eval = 200


def evaluateSetOfCases(var_data, n_lim=0):
    successful = []
    lim_data = []
    of_data = []
    for i in range(len(var_data)):
        successful.append(True)
        vars = var_data[i]
        of_1 = vars[0]
        g = 1 + 9 * (sum(vars[1:])) / (len(vars) - 1)
        of_2 = g * (1 - (vars[0] / g) ** 0.5)
        of_data.append([of_1, of_2])

    return [var_data, of_data, lim_data, successful]
