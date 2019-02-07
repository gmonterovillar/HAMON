import numpy as np
import os
import sys
import importlib.util
import matplotlib.pyplot as plt
import glob
import re

# import the ./src path so that python can find the modules
sys.path.append(os.getcwd() + '/src/')

import populations

def main():
    done = False
    #TODO uncomment so that the path is read not fixed
    #HAMON_config_file_path = input('Introduce path and of the HAMON_config.py file:\n')
    #HAMON_config_file_name = input('Introduce name of the HAMON_config file (without .py extension):\n')
    #EA_config_file_path = input('Introduce path and of the EA_config.py file:\n')
    #EA_config_file_name = input('Introduce name of the EA_config file (without .py extension):\n')
    HAMON_config_file_path = '/Users/gonzalomv//Programs/HAMON/examples/multi_objective/test_3/'
    HAMON_config_file_name = 'opti_config_ex_3'
    EA_config_file_path = '//Users/gonzalomv//Programs/HAMON/examples/multi_objective/test_3/'
    EA_config_file_name = 'ea_config_ex_3'

    # import both config files
    sys.path.append(HAMON_config_file_path)
    HAMON_conf = importlib.import_module(HAMON_config_file_name, package=None)
    sys.path.append(EA_config_file_path)
    EA_conf = importlib.import_module(EA_config_file_name, package=None)

    # read data from config files
    n_var = HAMON_conf.n_var
    n_of = HAMON_conf.n_of
    n_lim = HAMON_conf.n_lim
    project_name = HAMON_conf.project_name
    max_min = HAMON_conf.max_min
    working_directory = HAMON_conf.working_directory
    n_LHS = HAMON_conf.n_LHS
    n_select = EA_conf.n_to_select
    data_base_file = HAMON_conf.data_base_file
    var_range = HAMON_conf.var_range
    analytical_funcs = HAMON_conf.analytical_funcs

    EA_path = working_directory + '/EA_data/'

    while not done:
        correct_input = False
        while not correct_input:
            try:
                option = int(input('Choose an option:\n\t1 - Change config files\n\t2 - Plot all evaluated designs with '
                                   'pareto-front\n\t3 - Show the evolution of the EA over the optimization loops (or the results of the EA in case of analytical functions)\n\t'
                                   '4 - Plot the last evaluated individuals for a optimization loop range\n\t'
                                   '5 - Check the ranges of the variables of the individuals in the pareto-front\n\t6 - Finish\n'))
                correct_input = True
            except:
                print('Invalid option, please choose again.')
        if option == 1:
            #TODO implement
            pass

        elif option == 2:
            # TODO make this also work when analytical functions are used and there is no database but fg_summary
            if(n_of == 2):
                pop = populations.PopulationPostMOEA(working_directory + '/' + project_name + '_data_base.csv', n_var, n_of, n_lim)
                pop_f = []
                pop_nf = []
                for ind in pop.population:
                    if ind.getFeasibility():
                        pop_f.append(ind)
                    elif not ind.getFeasibility:
                        pop_nf.append(ind)

                [pop_fp, rank_list_fp] = pop.rankPopulation(pop_f, max_min)
                [pop_nfp, _] = pop.rankPopulation(pop_nf, max_min)

                rank_1_ofs = []
                rest_ofs = []
                for i in range(n_of):
                    rest_ofs.append([])
                for rank in range(len(rank_list_fp)):
                    for i in rank_list_fp[rank]:
                        ofs = pop_fp[i].getOf()
                        if rank == 0:
                            rank_1_ofs.append((ofs[0], ofs[1]))
                        else:
                            for of in range(len(ofs)):
                                rest_ofs[of].append(ofs[of])

                rank_1_sorted = sorted(rank_1_ofs, key=lambda x: x[0])
                rank_1_to_plot = np.asarray((rank_1_sorted))

                plt.figure()
                plt.plot(rest_ofs[0], rest_ofs[1], 'bo', label='other ranks')
                plt.plot(rank_1_to_plot[:,0], rank_1_to_plot[:,1], 'ro-', label='pareto_front')
                plt.legend()
                plt.show()
            else:
                print('Number of objective functions is to big in order to plot, please chose another option\n')

        elif option == 3:
            correct_input = False
            while not correct_input:
                selected_or_final = int(input('What would you like to plot?\n\t1 - entire population\n\t2 - selected individuals\n'))
                if selected_or_final != 1 and selected_or_final != 2:
                    print('Invalid value, please chose again.')
                else:
                    correct_input = True
            if selected_or_final == 1:
                file_type_name = 'fg'
            else:
                file_type_name = 'sel'

            all_files = glob.glob(EA_path + project_name + '*')
            if not analytical_funcs:
                if len(all_files) > 0:
                    all_files.sort(key=lambda x: int(re.search(project_name + '_(\d+)_', x).group(1)))
                    lower_data = int(re.search(project_name + '_(\d+)_', all_files[0]).group(1))
                    upper_data = int(re.search(project_name + '_(\d+)_', all_files[-1]).group(1))
                    print('The lower optimization loop number found in ' + str(EA_path) + ' is ' + str(lower_data) + ' and the highest one is ' + str(upper_data))
                    lower = lower_data - 1
                    upper = upper_data + 1
                    correct_input = False
                    while  not correct_input:
                        while lower < lower_data:
                            lower = int(input('Input the lower bound of the ranges of optimization loops you would like to plot:\n'))
                            if lower < lower_data:
                                print('Data for optimization loop ' + str(lower) + ' is not available.')
                        while upper > upper_data:
                            upper = int(input('Input the upper bound of the ranges of optimization loops you would like to plot:\n'))
                            if upper > upper_data:
                                print('Data for optimization loop ' + str(lower) + ' is not available.')
                        if lower > upper:
                            print('The lower bound is higher than the upper bound, please choose again.')
                            lower = lower_data - 1
                            upper = upper_data + 1
                        else:
                            correct_input = True

                    file = open(EA_path + project_name + '_' + str(lower) + '_' + file_type_name + '_summary.csv')
                    for line in file:
                        line_s = line.split(',')
                        of_names = line_s[1:1+n_of]
                        break
                    file.close()

                    true_front_ZDT1 = np.genfromtxt('/home/villar/Downloads/plotting_paper//ZDT_1_pareto.csv', delimiter=',')

                    plt.figure()
                    plt.plot(true_front_ZDT1[:, 0], true_front_ZDT1[:, 1], 'k', label='true_front')
                    for loop in range(lower, upper + 1):
                        data = np.genfromtxt(EA_path + project_name + '_' + str(loop) + '_' + file_type_name + '_summary.csv', skip_header=1, delimiter=',')
                        plt.plot(data[:,1], data[:,2], 'o', label='loop ' + str(loop))
                    plt.xlabel(of_names[0])
                    plt.ylabel(of_names[1])
                    plt.legend()
                    plt.show()
                else:
                    print('No files found according to ' + EA_path + project_name + '*')
            else:
                    file = open(EA_path + project_name + '_' + file_type_name + '_summary.csv')
                    for line in file:
                        line_s = line.split(',')
                        of_names = line_s[1:1 + n_of]
                        break
                    file.close()

                    plt.figure()
                    data = np.genfromtxt(EA_path + project_name + '_' + file_type_name + '_summary.csv', skip_header=1, delimiter=',')
                    plt.plot(data[:, 1], data[:, 2], 'o')
                    plt.xlabel(of_names[0])
                    plt.ylabel(of_names[1])
                    plt.show()

        elif option == 4:
            all_files = glob.glob(EA_path + project_name + '*')
            if len(all_files) > 0:
                all_files.sort(key=lambda x: int(re.search(project_name + '_(\d+)_', x).group(1)))
                lower_data = int(re.search(project_name + '_(\d+)_', all_files[0]).group(1))
                upper_data = int(re.search(project_name + '_(\d+)_', all_files[-1]).group(1))
                print('The lower optimization loop number found in ' + str(EA_path) + ' is ' + str(
                    lower_data) + ' and the highest one is ' + str(upper_data))
                lower = lower_data - 1
                upper = upper_data + 1
                correct_input = False
                while not correct_input:
                    while lower < lower_data:
                        lower = int(input(
                            'Input the lower bound of the ranges of optimization loops you would like to plot:\n'))
                        if lower < lower_data:
                            print('Data for optimization loop ' + str(lower) + ' is not available.')
                    while upper > upper_data:
                        upper = int(input(
                            'Input the upper bound of the ranges of optimization loops you would like to plot:\n'))
                        if upper > upper_data:
                            print('Data for optimization loop ' + str(lower) + ' is not available.')
                    if lower > upper:
                        print('The lower bound is higher than the upper bound, please choose again.')
                        lower = lower_data - 1
                        upper = upper_data + 1
                    else:
                        correct_input = True
            data = np.genfromtxt(working_directory + '/' + project_name + '_data_base.csv', skip_header=1, delimiter=',')
            file = open(working_directory + '/' + project_name + '_data_base.csv')
            file = open(working_directory + '/' + project_name + '_data_base.csv')
            for line in file:
                line_s = line.split(',')
                if n_lim == 0:
                    of_names = line_s[-n_lim - n_of:]
                else:
                    of_names = line_s[-n_lim - n_of: -n_lim]
                break
            file.close()

            beginnig = len(data) - (upper_data-lower)*n_select

            plt.figure()
            for loop in range(upper - lower + 1):
                plt.plot(data[beginnig + loop*n_select:beginnig + (loop+1)*n_select, -n_lim-2],data[beginnig + loop*n_select:beginnig + (loop+1)*n_select, -n_lim-1], 'o' ,label='loop ' + str(loop+lower))
            plt.xlabel(of_names[0])
            plt.ylabel(of_names[1])
            plt.legend()
            plt.show()

        elif option == 5:
            pop = populations.PopulationPostMOEA(working_directory + '/' + project_name + '_data_base.csv', n_var, n_of, n_lim)
            pop_f = []
            pop_nf = []
            for ind in pop.population:
                if ind.getFeasibility():
                    pop_f.append(ind)
                elif not ind.getFeasibility:
                    pop_nf.append(ind)

            [pop_fp, rank_list_fp] = pop.rankPopulation(pop_f, max_min)

            rank_1_vars = np.zeros([len(rank_list_fp[0]), n_var])

            for i in range(len(rank_list_fp[0])):
                indv_vars = pop_fp[rank_list_fp[0][i]].getVar()
                print(indv_vars)
                for j in range(len(indv_vars)):
                    rank_1_vars[i,j] = indv_vars[j]

            file = open(data_base_file, 'r')
            for line in file:
                var_names = line.split(',')[1:1+n_var]
                break
            file.close()
            print('The max and min values of each of the variables taking into account individuals of rank 1 are:')
            for i in range(n_var):
                print('For variable %s -> min %8.7e and max %8.7e where the allowed range is [%8.7e, %8.7e]' % (var_names[i], min(rank_1_vars[:,i]), max(rank_1_vars[:,i]), var_range[i][0], var_range[i][1]))
            print()

        elif option == 6:
            done = True




# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    main()