##============================ ea_config_ex_3.py ================================

# Some of the input parameters and options in order to select the settings of the
# evolutionary algorithm are given here for the minimization of f1(x) and f2(x)
# of the ZDT 1 using NSGA-II (Genetic Algorithms).

EA_type = 'GA'
pop_size = 80
n_gen = 300
mut_rate = -1
n_gen_var = 25
cross_rate = 0.9
tour_sel_param = 0.8
perc_rank1 = 1.0
perc_nf = 0
