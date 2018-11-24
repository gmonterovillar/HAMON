from scipy.interpolate import Rbf
import numpy as np

class MetaModel:

    def __init__(self, n_var, n_of, n_lim):
        self._n_var = n_var
        self._n_of = n_of
        self._n_lim = n_lim
        self._var_data = []
        self._func_data = []
        self._construct_var = []
        self._validation_var = []
        self._construct_func = []
        self._validation_func = []

    def addData(self, var_data, func_data):
        if self._func_data == []:
            self._var_data = np.asarray(var_data)
            self._func_data = np.asarray(func_data)
        else:
            self._var_data = np.concatenate((self._var_data, np.asarray(var_data)))
            self._func_data = np.concatenate((self._func_data, np.asarray(func_data)))

    def getObjectiveFunctions(self):
        return self._objective_functions

    def getValidationVar(self):
        return self._validation_var

    def getValidationFunc(self):
        return self._validation_func

    def getConstructVar(self):
        return self._construct_var

    def getConstructFunc(self):
        return self._construct_func


class RBF(MetaModel):

    def __init__(self, n_var, n_of, n_lim, perc_training = 0.8, eps_scale_range = 3, basis=['multiquadric'], eps_eval = 1000):
        super().__init__(n_var, n_of, n_lim)
        self.__basis = basis
        self.__eps_scale_range = eps_scale_range
        self.__eps_eval = eps_eval
        self.__perc_training = perc_training
        self.__rbf = []
        self._objective_functions = []
        for i in range(self._n_of):
            self._objective_functions.append([])

    def getErrorOfRBF(self):
        func_rbf_values = self.__rbf(*np.transpose(self._validation_var).tolist())
        error = 0.
        for i in range(len(func_rbf_values)):
            error += (func_rbf_values[i] - self._validation_func[i]) ** 2
        error = (error / len(func_rbf_values)) ** 0.5
        return error

    def evaluate(self, var):
        f = self.__rbf
        command = 'f('
        for v in var:
            command +=  str(v) + ','
        command = command[:-1] + ')'
        rbf_val = eval(command)
        return rbf_val

    def contructRbf(self, data, func, basis='', eps = 0):
        settings_str = ''
        if not basis == '' and not eps == 0:
            settings_str += ', function=basis,epsilon=eps'

        command = 'Rbf('
        for v in range(self._n_var):
            command += 'data[:,' + str(v) + '],'
        command += 'func' + settings_str + ')'
        rbf = eval(command)
        return rbf

    def optimize(self):
        for of in range(self._n_of):
            self._construct_var = self._var_data[:int(len(self._var_data) * self.__perc_training), :]
            self._construct_func = self._func_data[:int(len(self._func_data) * self.__perc_training), of]
            self._validation_var = self._var_data[int(len(self._var_data) * self.__perc_training):, :]
            self._validation_func = self._func_data[int(len(self._func_data) * self.__perc_training):, of]

            eps_def = self.contructRbf(self._construct_var, self._construct_func).epsilon
            eps_range = np.linspace(eps_def / self.__eps_scale_range, self.__eps_scale_range * eps_def, num=self.__eps_eval)
            eps_range = np.append(eps_range, eps_def)

            basis_opt = ''
            eps_opt = 0
            min_error = float('inf')
            for b in self.__basis:
                for eps in eps_range:
                    self.__rbf = self.contructRbf(self._construct_var, self._construct_func, b, eps)
                    error = self.getErrorOfRBF()
                    if error < min_error:
                        min_error = error
                        basis_opt = b
                        eps_opt = eps
            self._objective_functions[of] = self.contructRbf(self._construct_var, self._construct_func, basis_opt, eps_opt)



