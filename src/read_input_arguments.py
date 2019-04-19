import sys

def getInputArguments(s, verbose=True):
    try:
        option_1 = str(s[1])
        option_2 = str(s[3])
        conf_1 = str(s[2])
        conf_2 = str(s[4])
    except:
        print('\nMake sure that execution command contains "-c filename1 -ea filename2"\nArguments missing\n')
        sys.exit()

    conf_given = False
    conf_ea_given = False

    if option_1 == '-c':
        conf_file = conf_1
        conf_given = True
    elif option_1 == '-ea':
        conf_file_ea = conf_1
        conf_ea_given = True
    else:
        print('\nWARNING: %s is not a valid command!\n' % (option_1))
        sys.exit()

    if option_2 == '-c':
        conf_file = conf_2
        conf_given = True
    elif option_2 == '-ea':
        conf_file_ea = conf_2
        conf_ea_given = True
    else:
        print('\nWARNING: %s is not a valid command!\n' % (option_2))
        sys.exit()

    if conf_ea_given and conf_given:
        if verbose:
            print('Config file for optimization ', conf_file)
            print('Config file for EA ', conf_file_ea)
            print('')
        return [conf_file, conf_file_ea]
    else:
        print('\nBoth the config file for the optimization and EA settings are needed\n')
        sys.exit()

def getParametersOptiConfig(dirname, filename):
    sys.path.append(dirname)
    conf = __import__(filename)

    try:
        var_range = conf.var_range
    except:
        printWarningInputMissing("var_range", dirname + '/' + filename)
    try:
        max_min = conf.max_min
    except:
        printWarningInputMissing("max_min", dirname + '/' + filename)
    try:
        analytical_funcs = conf.analytical_funcs
    except:
        printWarningInputMissing("analytical_funcs", dirname + '/' + filename)
    try:
        working_directory = conf.working_directory
    except:
        printWarningInputMissing("working_directory", dirname + '/' + filename)
    try:
        project_name = conf.project_name
    except:
        project_name = 'opti_proj'
        printWarningDefaultValue("project_name", project_name)
    try:
        lim_range_orig = conf.lim_range_orig
    except:
        lim_range_orig = []
        printWarningDefaultValue("lim_range_orig", lim_range_orig)
        print("This means that no constraints will be taken into consideration")

    n_lim = len(lim_range_orig)

    try:
        range_gen = conf.range_gen
    except:
        range_gen = 0
        if n_lim:
            printWarningDefaultValue("range_gen", range_gen)
    try:
        mod_lim_range = conf.mod_lim_range
    except:
        mod_lim_range = lim_range_orig
        if range_gen > 0 and n_lim > 0:
            printWarningDefaultValue("mod_lim_range", mod_lim_range)
    try:
        var_names = conf.var_names
    except:
        var_names = []
    try:
        of_names = conf.of_names
    except:
        of_names = []
    try:
        lim_var_names = conf.lim_var_names
    except:
        lim_var_names = []
    try:
        any_int_var = conf.any_int_var
    except:
        any_int_var = False
    try:
        int_var_indexes = conf.int_var_indexes
    except:
        int_var_indexes = []
        if any_int_var:
            printWarningInputMissing("int_var_indexes", dirname + '/' + filename)
    try:
        plotting = conf.plotting
    except:
        plotting = False
    try:
        true_pareto = conf.true_pareto
    except:
        true_pareto = False

    n_var = len(var_range)
    n_of = len(max_min)

    return [n_var, n_of, n_lim, project_name, var_range, lim_range_orig, range_gen, mod_lim_range, max_min, var_names,
            of_names, lim_var_names, analytical_funcs, any_int_var, working_directory, int_var_indexes, plotting, true_pareto]

def printWarningDefaultValue(var_name, value):
    print("Warning: default value of ", value, " assigned to %s" % (var_name))

def printWarningInputMissing(input_name, input_file):
    print("WARNING: %s input is missing in %s.py!!\n\n" % (input_name, input_file))
    sys.exit()
