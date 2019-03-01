from src import populations

import sys

class DE:
    def __init__(self, var_names, of_names, lim_var_names, n_var, n_lim, max_min, any_int_var, int_var_indexes, conf):
        self._pop = []
        self._var_names = var_names
        self._of_names = of_names
        self._lim_var_names = lim_var_names
        self._n_var = n_var
        self._n_lim = n_lim
        if type(max_min) is list and len(max_min) == 1:
            self._max_min = max_min[0]
        else:
            self._max_min = max_min
        self._any_int_var = any_int_var
        self._int_var_indexes = int_var_indexes

        self.__found_best = False
        self.__best_index = 0

        # Get the variables in the EA_config.py file
        self._pop_size = int(conf.pop_size)
        self._n_gen = conf.n_gen
        self._mut_rate = conf.mut_rate
        self._recomb_rate = conf.recomb_rate

    def optimize(self, project_name, var_range, of_function, var_data, of_data, lim_range_orig, \
                 range_gen, lim_functions, mod_lim_range):
        """Runs the DE optimization algorithm with the given objective and limiting functions for a given
                number of generations"""

        # Some checks:
        self.__checkInputs(var_range, range_gen)

        # Initialise random population
        if not self._any_int_var:
            self._pop = populations.PopulationDE(self._pop_size, self._n_var, 1, self._n_lim)
        else:
            # TODO implement any integer var class
            self._pop = populations.PopulationDEIntegerVar(self._pop_size, self._n_var,
                                                                 1, self._n_lim, self._int_var_indexes)

        # Initialize population
        self._pop.initialize(var_range)

        # Obtain the value of the objective functions, value for limiting
        # variables and check if feasible of population
        self._pop.nulliffyFeasibility(self._pop.population)
        self._pop.evaluate(self._pop.population, of_function, lim_functions)

        if self._n_lim > 0:
            # Check which limitation range has to be used
            if range_gen > 0:
                lim_range = mod_lim_range
            else:
                lim_range = lim_range_orig
            self._pop.checkFeasibility(self._pop.population, lim_range)
        else:
            lim_range = []

        best_fitness_over_iter = []
        perc_feasibles_over_iter = []

        # Beginning of the loop over the generations
        print('Evaluating DE generations:')

        for generation in range(self._n_gen):
            self._waitbar(generation, self._n_gen)

            if self._n_lim > 0:
                # Check what the range of the limitations is based on range_gen
                if generation + 1 <= self._n_gen * range_gen:
                    lim_range = mod_lim_range
                else:
                    lim_range = lim_range_orig

                # Nullify feasibility of population and recheck
                self._pop.nulliffyFeasibility(self._pop.population)
                if self._n_lim > 0:
                    self._pop.checkFeasibility(self._pop.population, lim_range)

            new_population_vars = []

            for i in range(int(self._pop_size)):
                # Generate next generation population by applying mutation, recombination and selection
                # Mutation
                self._pop.getCandidateByMutation(i, self._mut_rate, var_range, range(self._pop_size))
                # Recombination, ensuring that at least one of the parameters in taken from Y with ri
                self._pop.getCandidateByRecombination(i, self._recomb_rate, var_range)
                # Selection
                new_population_vars.append(self._pop.selection(i, of_function, lim_functions, lim_range, self._max_min))
            # Put the parameter vectors obtained by into the new population and evaluate them
            self.__updateVarsOfNewGeneration(new_population_vars[:])
            self._pop.evaluate(self._pop.population, of_function, lim_functions)

            if self._n_lim > 0:
                self._pop.nulliffyFeasibility(self._pop.population)
                self._pop.checkFeasibility(self._pop.population, lim_range)

            self.__findBest()
            if self.__found_best:
                best_fitness_over_iter.append([generation + 1, self._pop.population[self.__best_index].getOf()[0],
                                               self._pop.population[self.__best_index].getLimVar(),
                                               self._pop.population[self.__best_index].getVar()])

            perc_feasibles_over_iter.append(self._pop.obtainPercentageOfFeasibles())

        # Write data base best individual summary
        bi_summary_file = open(project_name + '_bi_summary.csv', 'w')
        header = 'Generation, %s ' % (self._of_names[0])
        if self._n_lim > 0:
            for l_name in self._lim_var_names:
                header += ', ' + l_name
        header += '\n'
        bi_summary_file.write(header)
        for i in range(len(best_fitness_over_iter)):
            str_best = str(best_fitness_over_iter[i][0]) + ', ' + str(best_fitness_over_iter[i][1])
            if self._n_lim > 0:
                for lim in best_fitness_over_iter[i][2]:
                    str_best += ', ' + str(lim)
            str_best += '\n'
            bi_summary_file.write(str_best)
        bi_summary_file.close()

        # Write data base best individual
        bi_file = open(project_name + '_bi.csv', 'w')
        header = 'Generation'
        for v_name in self._var_names:
            header += ', ' + v_name
        header += '\n'
        bi_file.write(header)
        for i in range(len(best_fitness_over_iter)):
            str_best = str(best_fitness_over_iter[i][0]) + ', '
            for var in best_fitness_over_iter[i][3]:
                str_best += ', ' + str(var)
            str_best += '\n'
            bi_file.write(str_best)
        bi_file.close()

        # TODO put all this into a function
        if self.__found_best:
            str_best = '\nThe best found individual:\n\tDesign variables:\n'
            best_var = self._pop.population[self.__best_index].getVar()
            for i in range(self._n_var):
                str_best += '\t\t%s = %.10f\n' % (self._var_names[i], best_var[i])
            if self._n_lim:
                best_lim = self._pop.population[self.__best_index].getLimVar()
                str_best += '\tLimiting variables:\n'
                for i in range(self._n_lim):
                    str_best += '\t\t%s = %.10f\n' % (self._lim_var_names[i], best_lim[i])
            str_best += ('\tFitness value:\n\t\t%s = %.10f\n' % (self._of_names[0], self._pop.population[self.__best_index].getOf()[0]))
            print(str_best)
        else:
            print('\nNo individual that fulfills all constraints has been found!!\n')

        if self._n_lim > 0:
            return [[], perc_feasibles_over_iter]
        else:
            return

    def __updateVarsOfNewGeneration(self, new_population_vars):
        for i in range(self._pop_size):
            self._pop.population[i].setVars(new_population_vars[i][:])

    def __findBest(self):
        self.__found_best = False
        if self._max_min == 'max':
            best_fitness = -float('inf')
            for i in range(self._pop_size):
                if self._pop.population[i].getOf()[0] > best_fitness and self._pop.population[i].getFeasibility():
                    best_fitness = self._pop.population[i].getOf()[0]
                    self.__best_index = i
                    self.__found_best = True
        else:
            best_fitness = float('inf')
            for i in range(self._pop_size):
                self._pop.population[i].getFeasibility()
                if self._pop.population[i].getOf()[0] < best_fitness and self._pop.population[i].getFeasibility():
                    best_fitness = self._pop.population[i].getOf()[0]
                    self.__best_index = i
                    self.__found_best = True

    def __checkInputs(self, var_range, range_gen):
        """Check if some of the given inputs need to be corrected. For instance, the size of the population has to
        be an even number."""

        #TODO check that all the inputs are correct, 0<mut_rate<1 and so on

        correct_inputs = True
        print("Performing some checks on the inputs...")
        # Check if the length of range variables is equal to n_var
        if self._n_var != len(var_range):
            correct_inputs = False
            sys.exit('\n\nFINISHING RUN!!!\nThe number of variables and len(var_range) does not match!!\n\n')

        if correct_inputs:
            print("All the checks were satisfactory!")
        else:
            print("The inputs have been corrected!")

    def _waitbar(self, i, N, toolbar_width=50):
        """Displays a waitbar representing the progress of the EA"""
        perc = float(i + 1) / N
        perc_bar = int(perc * toolbar_width)
        bar = '[%s>%s] %d%%' % ('=' * (perc_bar - 1), ' ' * (toolbar_width - perc_bar), int(perc * 100))
        sys.stdout.write('\r%s' % (bar))
        sys.stdout.flush()


class MODE(DE):

    def __init__(self, var_names, of_names, lim_var_names, n_var, n_of, n_lim, max_min, any_int_var, int_var_indexes, conf):
        super().__init__(var_names, of_names, lim_var_names, n_var, n_lim, max_min, any_int_var, int_var_indexes, conf)
        self._n_of = n_of

        # Some default settings
        self.__type_dist = 1
        self.__compare_w_data = False
        self.__n_to_select = -1

        self.__perc_rank1 = conf.perc_rank1
        self.__perc_nf = conf.perc_nf

        try:
            self.__n_to_select = conf.n_to_select
        except:
            pass

        if self.__n_to_select > 0:
            self.__type_dist = conf.type_dist
            self.__compare_w_data = conf.compare_w_data


    def optimize(self, project_name, var_range, of_functions, var_data, of_data, lim_range_orig, \
                 range_gen, lim_functions, mod_lim_range):

        # population
        if not self._any_int_var:
            self._pop = populations.PopulationsMODE(self._pop_size, self._n_var, self._n_of, self._n_lim)
        else:
            # TODO implement integer population
            self._pop = populations.PopulationsMODEIntegerVar(self._pop_size, self._n_var, self._n_of,
                                                                    self._n_lim, self._int_var_indexes)

        perc_feasibles_over_iter = []

        # Initialize populationP
        self._pop.initialize(var_range)

        # Beginning of the loop over the generations
        print('Evaluating MODE generations:')

        for generation in range(self._n_gen):
            self._waitbar(generation, self._n_gen)

            if self._n_lim > 0 and generation + 1 <= self._n_gen * range_gen:
                lim_range = mod_lim_range
            else:
                lim_range = lim_range_orig

            # Nullify population Q and PQ
            self._pop.populationQ = []
            self._pop.populationPQ = []

            self._pop.evaluate(self._pop.population, of_functions, lim_functions)

            # Nullify feasibility of populationP and recheck
            if self._n_lim > 0:
                self._pop.nulliffyFeasibility(self._pop.population)
                self._pop.checkFeasibility(self._pop.population, lim_range)

            # Assign ranking to individuals by splitting populationP into feasible and unfeasible
            if self._n_lim>0:
                pop_f = []
                pop_nf = []
                for ind in self._pop.population:
                    if ind.getFeasibility() == True:
                        pop_f.append(ind)
                    elif ind.getFeasibility() == False:
                        pop_nf.append(ind)

                [pop_fp, rank_list_fp] = self._pop.rankPopulation(pop_f, self._max_min)
                [pop_nfp, rank_list_nfp] = self._pop.rankPopulation(pop_nf, self._max_min)

                self._pop.population = pop_fp + pop_nfp
                for i in range(len(rank_list_nfp)):
                    for j in range(len(rank_list_nfp[i])):
                        rank_list_nfp[i][j] += len(pop_fp)
            else:
                [_, rank_list_fp] = self._pop.rankPopulation(self._pop.population, self._max_min)
                rank_list_nfp = []

            # Assign crowded distance to every individual of the initial population
            self._pop.crowdedDistance(self._pop.population, rank_list_fp, rank_list_nfp)

            # Apply mutation forcing that if possible, the selected random individuals belong to rank 1
            # if there are not enough rank 1, go to rank 2... and finally to unfeasible
            # If there are no current feasible individuals, all will be taken from the non-feasible ones
            if len(rank_list_fp) > 0:
                candidate_indexes = rank_list_fp[0]
            else:
                candidate_indexes = rank_list_nfp[0]
            rank = 1
            while len(candidate_indexes) < 3 and rank < len(rank_list_fp):
                candidate_indexes += rank_list_fp[rank]
                rank += 1
            if len(candidate_indexes) < 3 and self._n_lim > 0:
                rank = 1
                candidate_indexes += rank_list_nfp[0]
                while len(candidate_indexes) < 3 and rank < len(rank_list_nfp):
                    candidate_indexes += rank_list_nfp[rank]
                    rank += 1

            for i in range(self._pop_size):
                self._pop.getCandidateByMutation(i, self._mut_rate, var_range, range(self._pop_size))
                # Recombination, ensuring that at least one of the parameters in taken from Y with ri
                self._pop.getCandidateByRecombination(i, self._recomb_rate, var_range)
                # Selection
                self._pop.addIndividualZToPopulationQ(var_range)

            # Obtain the value of the variables, the objective functions, value for limiting
            # variables and check if feasible of populationQ
            self._pop.evaluate(self._pop.populationQ, of_functions, lim_functions)

            if self._n_lim > 0:
                self._pop.nulliffyFeasibility(self._pop.populationQ)
                self._pop.checkFeasibility(self._pop.populationQ, lim_range)

            # Combine both populationP and populationQ to get populationPQ
            self._pop.populationPQ = self._pop.population + self._pop.populationQ

            # Assign ranking to individuals by splitting populationPQ into feasible and unfeasible
            if self._n_lim > 0:
                pop_f = []
                pop_nf = []
                for ind in self._pop.populationPQ:
                    if ind.getFeasibility() == True:
                        pop_f.append(ind)
                    elif ind.getFeasibility() == False:
                        pop_nf.append(ind)

                [pop_fpq, rank_list_fpq] = self._pop.rankPopulation(pop_f, self._max_min)
                [pop_nfpq, rank_list_nfpq] = self._pop.rankPopulation(pop_nf, self._max_min)

                self._pop.populationPQ = pop_fpq + pop_nfpq

                for i in range(len(rank_list_nfpq)):
                    for j in range(len(rank_list_nfpq[i])):
                        rank_list_nfpq[i][j] += len(pop_fpq)
            else:
                [_, rank_list_fpq] = self._pop.rankPopulation(self._pop.populationPQ, self._max_min)
                rank_list_nfpq = []

            self._pop.obtainNewPopulationP(self.__perc_rank1, self.__perc_nf, rank_list_fpq, rank_list_nfpq)

            # Count the number of feasibles
            perc_feasibles_over_iter.append(self._pop.obtainPercentageOfFeasibles())

        self._pop.evaluate(self._pop.population, of_functions, lim_functions)
        if self._n_lim > 0:
            self._pop.nulliffyFeasibility(self._pop.populationQ)
            self._pop.checkFeasibility(self._pop.populationQ, lim_range)

        # Assign ranking to individuals by splitting population into feasible and unfeasible
        if self.__n_to_select > 0:
            pop_f = []
            pop_nf = []
            total_f = 0
            for ind in self._pop.population:
                if ind.getFeasibility():
                    pop_f.append(ind)
                    total_f += 1
                else:
                    pop_nf.append(ind)

            [pop_fp, rank_list_fp] = self._pop.rankPopulation(pop_f, self._max_min)

            # If not enough feasible, add also the non feasible so that they can be selected
            if total_f < self.__n_to_select:
                [pop_nfp, rank_list_nfp] = self._pop.rankPopulation(pop_nf, self._max_min)
                rank_list_fp += rank_list_nfp

            # Select the best found individuals
            selected_indexes = self._pop.selectIndividuals(rank_list_fp, self.__n_to_select, \
                                                           self.__type_dist, var_data, of_data,
                                                           self.__compare_w_data)

            # Write the four databases of the selected individuals
            self._pop.writeDataBase(project_name, self._of_names, self._var_names, self._lim_var_names, 0,
                                    selected_indexes)
            self._pop.writeDataBase(project_name, self._of_names, self._var_names, self._lim_var_names, 1,
                                    selected_indexes)

        # Write the four databases of the final generation
        self._pop.writeDataBase(project_name, self._of_names, self._var_names, self._lim_var_names, 0)
        self._pop.writeDataBase(project_name, self._of_names, self._var_names, self._lim_var_names, 1)

        selected_designs = []

        if self.__n_to_select > 0:
            # Put the selected designs variables in a list for the output
            for i in selected_indexes:
                selected_designs.append(self._pop.population[i].getVar())

        print()
        if not self._n_lim:
            return selected_designs
        else:
            return [selected_designs, perc_feasibles_over_iter]
