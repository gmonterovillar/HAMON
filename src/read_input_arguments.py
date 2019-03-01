import sys

def getInputArguments(s, verbose=True):

    conf_file = ''
    conf_file_ea = ''
    err = ''

    if len(s) < 5:
        if verbose:
            err = 'Error in executing HAMON, not enough input arguments'
        sys.exit(err)
    else:
        for i in range(1, 4, 2):

            if str(s[i]) == '-c' and str(s[i+1])[-3:] == '.py':
                conf_file = str(s[i+1])
            elif str(s[i]) == '-ea' and str(s[i+1])[-3:] == '.py':
                conf_file_ea = str(s[i+1])
            else:
                if verbose:
                    err = 'Error in executing HAMON, input argument \"' + str(s[i]) + ' ' + str(s[i+1]) + '\" invalid'
                sys.exit(err)

        if verbose:
            print('Config file for optimization: ' + conf_file   )
            print('Config file for EA          : ' + conf_file_ea)
            print(' ')

        return [conf_file, conf_file_ea]
