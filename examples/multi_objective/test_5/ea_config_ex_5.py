##============================ ea_config_ex_5.py ================================

# Some of the input parameters and options in order to select the settings of the
# evolutionary algorithm are given here for the minimization of f1(x) and f2(x)
# of the ZDT 1 using Differential Evolution.

EA_type = 'DE'
pop_size = 80
n_gen = 250
mut_rate = 0.5
recomb_rate = 0.5
perc_rank1 = 1.0
perc_nf = 0

# Needed because RBFs are used
n_to_select = 25
type_dist = 0
compare_w_data = True
