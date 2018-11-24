import random
import numpy as np

class Individual:

    def __init__(self, n_var, n_of, n_lim):
        self._n_var = n_var
        self._n_of = n_of
        self._n_lim = n_lim
        self._of = self._zeros(self._n_of)
        if self._n_lim > 0:
            self._lim_var = self._zeros(self._n_lim)
        self._crowded_dist = 0.
        self._feasibility = True
        self._rank = 0

    def checkFeasibility(self, lim_range):
        """Checks if an individual is feasible or not based on the given constrains"""
        feasible = []
        for i in range(len(lim_range)):
            feasible.append(False)
            if lim_range[i][0] != 'greater' and lim_range[i][0] != 'lower':
                if lim_range[i][1] >= self._lim_var[i] >= lim_range[i][0]:
                    feasible[i] = True
            elif lim_range[i][0] == 'greater':
                if self._lim_var[i] > lim_range[i][1]:
                    feasible[i] = True
            elif lim_range[i][0] == 'lower':
                if self._lim_var[i] < lim_range[i][1]:
                    feasible[i] = True
        self._feasibility = all(j == True for j in feasible)

    def evaluate(self, of_functions, lim_functions):
        """From the varaibles of the individual, evaluates the objectives functions"""
        #TODO trying to see if the evaluate doesnt need to pass each of the variables separately
        '''
        v = self._var
        for i in range(self._n_of):
            f = of_functions[i]
            command = 'self._of[%d]=f(' % (i)
            for j in range(len(v)):
                command += 'v[%d],' % (j)
            command = '%s)' % (command[:-1])
            exec(command)
        if self._n_lim > 0:
            for i in range(self._n_lim):
                fLim = lim_functions[i]
                command = 'self._lim_var[%d]=fLim(' % (i)
                for j in range(len(v)):
                    command += 'v[%d],' % (j)
                command = '%s)' % (command[:-1])
                exec(command)
        '''
        for i in range(self._n_of):
            f = of_functions[i]
            self._of[i]=f(*self._var)
        if self._n_lim > 0:
            for i in range(self._n_lim):
                fLim = lim_functions[i]
                self._lim_var[i]=fLim(*self._var)

    def getLim(self):
        return self._lim_var


    #TODO cehck the case where either of, n_lim or n_var is =1 for setting
    def setLimVar(self, lim_var):
        self._lim_var = lim_var

    def getOf(self):
        return self._of

    def setOf(self, ofs):
        self._of = ofs[:]

    def getLimVar(self):
        return self._lim_var

    def getVar(self):
        return self._var

    def setVars(self, vars):
        for i in range(self._n_var):
            self._var[i] = vars[i]

    def setVar(self, var, var_index):
        self._var[var_index] = var

    def getFeasibility(self):
        return self._feasibility

    def getRank(self):
        return self._rank

    def _zeros(self, n):
        """Create a list containing n zeros"""
        list = []
        for i in range(n):
            list.append(0)
        return list

class IndividualGA(Individual):
    """Class representing one individual in the GA with the following information:
    chromosome, variables, objective functions, rank, crowded distance, feasibility, limitingVariables
    """

    def __init__(self, n_var, n_gen_var, n_of, n_lim):
        super().__init__(n_var, n_of, n_lim)
        self._n_gen_chro = n_gen_var * n_var
        self._n_gen_var = n_gen_var
        self._var = self._zeros(self._n_var)
        self.chromosome = self._zeros(self._n_gen_chro)
        for j in range(self._n_gen_chro):
            r = random.random()
            if r > 0.5:
                self.chromosome[j] = 1

    def decodeChromosome(self, var_range):
        """Decodes the chromosome to obtain the value of the variables from the chromosome"""
        for i in range(self._n_var):
            xrange = var_range[i]
            tmp = 0
            for j in range(self._n_gen_var):
                tmp = tmp + 2 ** (-(j + 1)) * self.chromosome[i * self._n_gen_var + j]
            self._var[i] = xrange[0] + tmp * (xrange[1] - xrange[0]) / (1 - 2 ** (-self._n_gen_var))

    def mutate(self, mut_rate):
        """Mutates each gene of the chromosome with a given probability mut_rate"""
        for i in range(self._n_gen_chro):
            if random.random() < mut_rate:
                self.chromosome[i] = 1 - self.chromosome[i]

    def getChromosome(self):
        return self.chromosome


class IndividualGAIntegerVar(IndividualGA):
    """Class representing one individual in the GA with the follwong information:
        chromosome, variables, objective functions, rank, crowded distance, feasibility, limitingVariables
        with some variables only accepting integer values"""

    def __init__(self, n_var, n_gen_var, n_of, n_lim, int_var_indexes):
        super().__init__(n_var, n_gen_var, n_of, n_lim)
        self.int_var_indexes = int_var_indexes

    def decodeChromosome(self, var_range):
        """Decodes the chromosome to obtain the value of the variables from the chromosome, taking into account
        that some variables are int variables"""
        for i in range(self._n_var):
            xrange = var_range[i]
            tmp = 0
            for j in range(self._n_gen_var):
                tmp = tmp + 2 ** (-(j + 1)) * self.chromosome[i * self._n_gen_var + j]
            self._var[i] = xrange[0] + tmp * (xrange[1] - xrange[0]) / (1 - 2 ** (-self._n_gen_var))

        for i in self.int_var_indexes:
            self._var[i] = round(self._var[i])

class IndividualDE(Individual):

    def __init__(self, n_var, var_range, n_of, n_lim):
        super().__init__(n_var, n_of, n_lim)
        self._var = np.zeros(self._n_var)
        for i in range(self._n_var):
            self._var[i] = var_range[i][0] + random.random() * (var_range[i][1] - var_range[i][0])

    # TODO Fix integers vars
    def fixIntegerVars(self, var_range):
        pass

class IndividualDEIntegerVar(IndividualDE):
    """Class representing one individual in the DE with the following information
       with some variables only accepting integer values"""

    def __init__(self, n_var, var_range, n_of, n_lim, int_var_indexes):
        super().__init__(n_var, var_range, n_of, n_lim)
        self.int_var_indexes = int_var_indexes

    def fixIntegerVars(self, var_range):
        for int_var in self.int_var_indexes:
            var = round(self._var[int_var])
            if var < var_range[int_var][0]:
                var += 1
            elif var > var_range[int_var][1]:
                var -= 1
            self._var[int_var] = var





