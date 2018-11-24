# -*- coding: utf-8 -*-
##================================ HAMON.py ====================================

# Gonzalo Montero Villar
# Department of Mechanics and Maritime Sciences
# Division fo Fluid Dynamics
# Chalmers University of Technology, Gothenburg, Sweden
# villar@chalmers.se
# March 2016

import numpy as np
import os
import sys
import glob
import re

# import the ./src path so that python can find the modules
sys.path.append(os.getcwd() + '/src/')

#import HAMON_Single_config as conf
import HAMON_multi_contrained_conf as conf
#import HAMON_Multi_config as conf
import EA_config as confEA
import genetic_algorithm as ga
import differential_evolution as de
import metamodels


def main():
    #printLogoAndHeader()

    # Get the variables from HAMON_config.py file
    n_var = conf.n_var
    n_of = conf.n_of
    n_lim = conf.n_lim
    project_name = conf.project_name
    var_range = conf.var_range
    lim_range_orig = conf.lim_range_orig
    range_gen = conf.range_gen
    mod_lim_range = conf.mod_lim_range
    max_min = conf.max_min
    var_names = conf.var_names
    of_names = conf.of_names
    lim_var_names = conf.lim_var_names
    analytical_funcs = conf.analytical_funcs
    any_int_var = conf.any_int_var
    working_directory = conf.working_directory

    if not analytical_funcs:
        max_opti_loops = conf.max_opti_loops
        data_base_file = conf.data_base_file
        existing_data_base = conf.existing_data_base
        n_LHS = conf.n_LHS

    if any_int_var:
        int_var_indexes = conf.int_var_indexes
    else:
        int_var_indexes = []

    # Add names in case the are not any
    if var_names == []:
        for i in range(n_var):
            var_names.append('var_%d' % (i + 1))
    if of_names == []:
        for i in range(n_of):
            of_names.append('of_%d' % (i + 1))
    if lim_var_names == []:
        for i in range(n_lim):
            lim_var_names.append('lim_var_%d' % (i + 1))

    os.chdir(working_directory)
    EA_path = os.getcwd() + '/EA_data/'
    if not os.path.isdir(EA_path):
        print('Creating directory %s' % (EA_path))
        os.system('mkdir %s' % (EA_path))

    if not analytical_funcs:
        if existing_data_base:
            # Read the existing data base
            print('Reading existing data base from ' + data_base_file + ' ...')
            [var_data, of_data, lim_data] = readDataBase(data_base_file, n_var, n_of, n_lim)
        else:
            # Create the LHS and evaluate it
            import pyDOE

            LHS = pyDOE.lhs(n_var, samples=n_LHS)
            # Convert the variables to their original range
            initial_design_set = np.zeros((n_LHS, n_var))
            for ii in range(n_var):
                deltaV = var_range[ii][1] - var_range[ii][0]
                varMin = var_range[ii][0]
                initial_design_set[:, ii] = varMin + deltaV * LHS[:, ii]
            var_data = initial_design_set

            # Write the LHS variables so that in case the process is stopped, the remaining cases from the LHS can be run
            file_name_LHS = os.getcwd() + '/LHS.csv'
            print('DOE by means of LHS created with ' + str(len(var_data)) + ' designs, the design variables are written in ' + file_name_LHS)
            writeDataBase(file_name_LHS, var_data, var_names)

            # var_data to list
            var_data = var_data.tolist()

            # Evaluate cases from LHS
            print('Evaluating initial design set')
            if not n_lim:
                [_, of_data, _, successful] = conf.evaluateSetOfCases(var_data)
            else:
                [_, of_data, lim_data, successful] = conf.evaluateSetOfCases(var_data, n_lim)

            #TODO only take the successful ones for the Meta model

    if n_of > 1:
        if confEA.EA_type == 'GA':
            print('Optimizer : NSGA_II')
            optimizer = ga.NSGA_II(var_names, of_names, lim_var_names, n_var, n_of, n_lim, max_min, any_int_var,
                                    int_var_indexes)
        elif confEA.EA_type == 'DE':
            print('Optimizer : multi-objective DE')
            optimizer = de.MODE(var_names, of_names, lim_var_names, n_var, n_of, n_lim, max_min, any_int_var,
                                   int_var_indexes)
    else:
        if confEA.EA_type == 'GA':
            print('Optimizer : single objective GA')
            optimizer = ga.GA(var_names, of_names, lim_var_names, n_var, n_lim, max_min, any_int_var,
                                  int_var_indexes)
        elif confEA.EA_type == 'DE':
            print('Optimizer : single objective DE')
            optimizer = de.DE(var_names, of_names, lim_var_names, n_var, n_lim, max_min, any_int_var,
                                  int_var_indexes)

    # Get the objective functions and the limiting functions from what has been defined in HAMON_config.py
    if analytical_funcs:
        if not n_lim:
            of_functions = conf.getFunctionsAnalytical()
            lim_functions = []
        else:
            [of_functions, lim_functions] = conf.getFunctionsAnalytical()

        var_data = []
        of_data = []

        optimizer.optimize(EA_path + project_name, var_range, of_functions, var_data, of_data, \
                              lim_range_orig, range_gen, lim_functions, mod_lim_range)

    else:
        meta_model_type = conf.meta_model_type
        #TODO fix this so that it can be taken from HAMON_config.py
        perc_training = 0.8
        eps_scale_range = 3
        basis = ['multiquadric','gaussian']
        eps_eval = 250
        var_data_to_add = var_data[:]
        of_data_to_add = of_data[:]
        if meta_model_type == 'RBF':
            print('Meta model: RBF')
            MM = metamodels.RBF(n_var, n_of, n_lim, eps_eval=eps_eval)

        current_opti_loops = getOptiLoopsAlreadyRun(EA_path, project_name)

        for i in range(current_opti_loops, max_opti_loops):
            print('Running optimization loop ' + str(i+1) + ', currently a total of ' + str(len(var_data)) + ' successful evaluations have been made')
            if not n_lim:
                MM.addData(var_data_to_add, of_data_to_add)
                print('Optimizing meta-model')
                MM.optimize()
                of_functions = MM.getObjectiveFunctions()
                lim_functions = []
            else:
                #TODO fix the meta-model when there are limitations
                [of_functions, lim_functions] = conf.getFunctionsFromRBF(var_data, of_data, lim_data)

            selected_individuals = optimizer.optimize(EA_path + project_name + '_'  + str(i+1), var_range, \
                                                        of_functions, var_data, of_data, lim_range_orig, range_gen,
                                                        lim_functions, mod_lim_range)


            [variables_selected, ofs_selected, lim_selected] = checkConvergence(selected_individuals, of_functions)

            var_data_to_add = []
            of_data_to_add = []

            for i in range(len(variables_selected)):
                # TODO check this out
                var_data.append(variables_selected[i])
                of_data.append(ofs_selected[i])
                var_data_to_add.append(variables_selected[i])
                of_data_to_add.append(ofs_selected[i])

            # Write data base
            print('Writing data base to ' + os.getcwd() + '/' + project_name + '_data_base.csv')
            writeDataBase(os.getcwd() + '/' + project_name + '_data_base.csv', var_data, [], of_data)

    return


def checkConvergence(selected_var, of_functions, lim_functions=0):
    #TODO change this so that it will work with limitations
    """Check the convergence of the meta model"""
    n_of = len(of_functions)
    if not lim_functions:
        n_lim = 0
    else:
        n_lim = len(lim_functions)
    [variables, ofs, lim, successful] = conf.evaluateSetOfCases(selected_var, n_lim)
    variables_to_check = []
    ofs_to_check = []
    lim_to_check = []
    for i in range(len(successful)):
        if successful[i]:
            variables_to_check.append(variables[i])
            ofs_to_check.append(ofs[i])
            #lim_to_check.append(lim[i])

    percError = 0
    for i in range(len(variables_to_check)):
        of_individual = []
        for j in range(n_of):
            f = of_functions[j]
            of_individual.append(f(*variables_to_check[i]))
            percError += abs((of_individual[j] - ofs_to_check[i][j]) / ofs_to_check[i][j]) / (n_of * len(variables_to_check))
    print('the percentage error is %.5f' % (percError * 100))

    return [variables_to_check, ofs_to_check, lim_to_check]

def getOptiLoopsAlreadyRun(EA_path, project_name):
    all_files = glob.glob(EA_path + project_name + '*')
    if len(all_files) > 0:
        all_files.sort(key=lambda x: int(re.search(project_name + '_(\d+)_', x).group(1)))
        opti_loops_run = int(re.search(project_name + '_(\d+)_', all_files[-1]).group(1))
    else:
        opti_loops_run = 0
    return opti_loops_run


def writeDataBase(fileName, var, var_names, of=[], of_names=0, lim=[], lim_names=0):
    n_var = len(var[0])
    n_cases = len(var)
    if var_names == []:
        # Generate standard of names
        var_names = []
        for i in range(n_var):
            var_names.append('var_%d' % (i + 1))
    if not of:
        n_of = 0
    else:
        n_of = len(of[0])
        if of_names == 0 or of_names == []:
            # Generate standard names
            of_names = []
            for i in range(n_of):
                of_names.append('of_%d' % (i + 1))
    if not lim:
        n_lim = 0
    else:
        n_lim = len(of[0])
        if lim_names == 0 or lim_names == []:
            # Generate standard names
            lim_names = []
            for i in range(n_lim):
                lim_names.append('lf_%d' % (i + 1))

    data_base = open(fileName, 'w')
    # Write the header
    str_to_write = 'id,  '
    for i in range(n_var):
        str_to_write += var_names[i] + ', '
    for i in range(n_of):
        str_to_write += of_names[i] + ', '
    for i in range(n_lim):
        str_to_write += lim_names[i] + ', '
    data_base.write(str_to_write[:-2] + '\n')

    # Write the variables
    for i in range(n_cases):
        str_to_write = '%d, ' % (i + 1)
        for j in range(n_var):
            str_to_write += '%.8f, ' % (var[i][j])
        for j in range(n_of):
            str_to_write += '%.8f, ' % (of[i][j])
        for j in range(n_lim):
            str_to_write += '%.8f, ' % (lim[i][j])
        data_base.write(str_to_write[:-2] + '\n')
    data_base.close()

    return


def readDataBase(file_name, n_var, n_of, n_lim):
    data = np.genfromtxt(file_name, skip_header=1, delimiter=',')

    #data = np.loadtxt(fileName, delimiter=',', skiprows=1)
    var_data = data[:, 1:-n_of - n_lim]
    if n_lim > 0:
        of_data = data[:, 1 + n_var:-n_lim]
        lim_data = data[:, 1 + n_var + n_of:]
        return [var_data.tolist(), of_data.tolist(), lim_data.tolist()]
    else:
        of_data = data[:, 1 + n_var:]
        return [var_data.tolist(), of_data.tolist(), []]

def printLogoAndHeader():
    print('                                                                                   ,*,,*/(#        \n                                                                                 .,/((((##*        \n                                                                             ,/,.,/*(#%&%(         \n                                                                            ,*/*/((#%%%&(          \n                                                                           .**/(###%%%%            \n                                                                    ... ..****((#%&%#              \n                                                                  .,///#%/(#%((%&,               \n                                                              (/./(&&(@#&&&(#%#                  \n                                                           ,***#&&&(#@@/%(@&&&&%%/                 \n                                                           ,*///%%&&@&@@%#&&@@&&/.                 \n                                                           */((//%@@&&@@&*&@@@%%(                  \n                                                       .*,*(((#%&(&@@@(&@@@&%%*                  \n                                                ..,,,***,,((#%%&@%#@@&,/%&&&&&%%                   \n                                         .,,*****,,**,,(((##%%%%@%%@# *#&&%%%&                   \n                                  .,,,,,*,./*,,,*,*,*.*/*//(###((%%  ,#&&&%%%&&,                   \n                              .,,..,,,,,,/,,,,,,,.*,*/((((((/#((/(  *#%&&%%%%%&                    \n                          .........,.*,,..,,,,,,***(#%%%###((((((  ,(%&&&%%%%&(                    \n                      .,,,.....,,((***,...**,,,/(###%%%%%%%%###(  ./%&&&%%%%%&.                    \n                    **,,,,....///,**,,,,,,,//((######%#%%%%%#%#   *#&&&%%%%&&&                     \n                    ,,,*/,,***,,,,,,,/(/*/////(######%%%%%%%%%.  *#%&&%%%&&&&/                     \n                    , . ....,(((*(%#(////*///((####%%%%%%&%%&,  *(%&&%%&&&&@@                      \n                  (/.....,,,***#((///////////(#%##%%%%%%%%&&,  ,(%&&&&&&&&@@&                      \n                 .//*,*,******,,,*//////////######%%%%&%%&%.  ./#&&&%&&&&@@@/                      \n                ,****/,//***/%##(////#(////(#####%%%#%%%&%    /#&&&%%%&&@@@@                       \n              *...,,*,,*/***#%#%%/%/#(((//(%#%%%##%%&%&    /#%&%%&&&@&@@                       \n             //,(/*/*,.**(//%%###%###(((/(###%%%&%%%%%(     /%&&@&&&&&&&&&&                        \n           ./(/(*,,*/.,****#%%%##%%(##(/((%##%%%%%((#,     *#&@@@%%%%&&&&&%                        \n          //////*,*,*****##(%%%###%##(/(/(%%##(((#(#    ..*%@@@@%%%&&&&&&&*...                     \n         ,///*,,.*,*((/,/%#%/%%%#%#(((((/%%//((((((    ..*&@@@@&&&&&&@((,...                     \n         ,*/(/**.*,(((#(#%#%((%###((/#((*/(/(((((*,..,...&@@@@&&&@&%%%#(/*,....  ,#%&%             \n         *(////,..*((((#####((/(((((/((/(//(#(((,        ,#&&&&&&%###(((/*,,.*%%&&&&@*             \n         /////****../(((#%%#/(#(((/*///(/(/(((/...    .   ,,***////(/////*#&@@&&@@%(,              \n         ***/*,*,**,,/((###/####((/////*///(/. .. ..  .......,,**/////#%%&&&&&&(*,.                \n        (//*/*,**//(////**/(((((////(((/(((*..,...,*,**......,,***(%%%%%%###/,..                   \n        *(**((//((*(##(////((/////##%#((/*,..//*..... ... ....,#((((((##(*..                       \n        (&(/(#(((*#%%%(/////((((%&&&%#(..*(/,........  ...,(&%(((((##/,.                           \n        ..*/(####//##((((/(#####%%&%/****,,,,.,,.......(%&%(((((#/*..                              \n      .    /#%*/(#(*(%(##%#%&@@&&&&%#((////*,,.../%&%(/(((#(*,..                                 \n .. ........,*,//##%(%%%&(@@@@@@@&&&@@%##(///*,/#%%#(((((#/,.                                      \n/**.........,#&%%(&&@@@@@@@@&%%#%&@@%##(//#%(((((#/,..                                         \n**/*//,...,.*/(#%/&&@@@&&&&%########%&%((((#(((((#(*..       . .........,.                         \n')
    print('\n\n\nGonzalo Montero Villar\nDepartment of Mechanics and Maritime Sciences\nDivision fo Fluid Dynamics\nChalmers University of Technology, Gothenburg, Sweden\nvillar@chalmers.se\n\n')

# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    main()
