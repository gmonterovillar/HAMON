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