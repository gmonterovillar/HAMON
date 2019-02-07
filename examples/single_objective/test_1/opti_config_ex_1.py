##============================ opti_config_ex_1.py ================================

# Config file for the minimization of the De Jong’s fifth function or Shekel’s foxholes[1]:
# f(x) = (0.002 + sum^25_{i=1} 1/(i + (x_1 - a_1i)^6+(x_2-a_2i)^6))^(-1)
# where a = [-32 -16   0  16  32 -32 ...  0 16 32
#            -32 -32 -32 -32 -32 -16 ... 32 32 32]

# References:
# [1] - Molga, M., & Smutnicki, C. Test functions for optimization needs (2005)
# [2] - https://www.sfu.ca/~ssurjano/dejong5.html

print('Minimizing the De Jong’s fifth function. The minimum value is around 0.998004\n')

n_of = 1
n_var = 2
var_range = [[-65.536, 65.536], [-65.536, 65.536]]
n_lim = 0
any_int_var = False
int_var_indexes = []
project_name = 'ex_1'
var_names = ['x', 'y']
of_names = ['of_1']
lim_var_names = []
lim_range_orig = [('greater', 0.0)]
range_gen = 0
mod_lim_range = []
max_min = ['min']
analytical_funcs = True
working_directory = '.'
plotting = True


def getFunctionsAnalytical():
    def of(x1, x2):
        a_i = [-32, -16, 0, 16, 32]
        a = []
        for i in range(5):
            a = a + a_i
        b = []
        for i in range(25):
            if i < 5:
                b.append(-32)
            elif i < 10:
                b.append(-16)
            elif i < 15:
                b.append(0)
            elif i < 20:
                b.append(16)
            else:
                b.append(32)

        fitness = 0.002
        for i in range(25):
            fitness += (i + 1 + (x1 - a[i]) ** 6 + (x2 - b[i]) ** 6) ** (-1)
        return fitness ** (-1)

    return [of]
