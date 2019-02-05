import sys

def getInputArguments(s, verbose=True):
    option_1 = str(s[1])
    option_2 = str(s[3])
    conf_1 = str(s[2])
    conf_2 = str(s[4])

    conf_given = False
    conf_ea_given = False

    if option_1 == '-c':
        conf_file = conf_1
        conf_given = True
    elif option_1 == '-ea':
        conf_file_ea = conf_1
        conf_ea_given = True

    if option_2 == '-c':
        conf_file = conf_2
        conf_given = True
    elif option_2 == '-ea':
        conf_file_ea = conf_2
        conf_ea_given = True

    if conf_ea_given and conf_given:
        if verbose:
            print('Config file for optimization ', conf_file)
            print('Config file for EA ', conf_file_ea)
            print('')
        return [conf_file, conf_file_ea]
    else:
        print('Both the config file for the optimization and EA settings are needed')
        sys.exit()