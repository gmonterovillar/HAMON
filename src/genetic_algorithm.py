from src import populations

import sys
import random

class GA:
    def __init__(self, var_names, of_names, lim_var_names, n_var, n_lim, max_min, any_int_var, int_var_indexes, confEA):
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

        self.__best_index = 0
        self.__best_fitness = 0
        self.__best_chromosome = []
        self.__found_best = False

        # Get the variables in the EA_config.py file
        self._pop_size = int(confEA.pop_size)
        self._n_gen = confEA.n_gen
        self._n_gen_var = confEA.n_gen_var
        if confEA.mut_rate>=0:
            self._mut_rate = confEA.mut_rate
        else:
            self._mut_rate = 1/(self._n_gen_var*self._n_var)
        self._cross_rate = confEA.cross_rate
        self._tour_sel_param = confEA.tour_sel_param

    def optimize(self, project_name, var_range, of_function, var_data, of_data, lim_range_orig, \
                 range_gen, lim_functions, mod_lim_range):
        """Runs the GA optimization algorithm with the given objective and limiting functions for a given
        number of generations"""

        # Some checks:
        self.__checkInputs(var_range, range_gen)

        # Initialise random population
        if not self._any_int_var:
            self._pop = populations.PopulationGA(self._pop_size, self._n_var, self._n_gen_var,
                                                          1, self._n_lim)
        else:
            self._pop = populations.PopulationGAIntegerVar(self._pop_size, self._n_var, self._n_gen_var,
                                                                    1, self._n_lim, self._int_var_indexes)

        # Initialize population
        self._pop.initialize()

        # Obtain the value of the variables, the objective functions, value for limiting
        # variables and check if feasible of population
        self._pop.decode(self._pop.population, var_range)
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
        print('Evaluating GA generations:')
        for generation in range(self._n_gen):
            self._waitbar(generation, self._n_gen)

            self.__selectElitism()

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

            new_population_chromosomes = []

            for i in range(int(self._pop_size / 2)):
                # Generate next generation population by applying tournament selection, crossover and mutation

                # Tournament selection process
                i1 = self._pop.tournamentSelection(self._tour_sel_param, self._max_min)
                i2 = self._pop.tournamentSelection(self._tour_sel_param, self._max_min)

                # Crossover process
                r = random.random()
                if r > self._cross_rate:
                    new_population_chromosomes.append(self._pop.population[i1].chromosome[:])
                    new_population_chromosomes.append(self._pop.population[i2].chromosome[:])
                else:
                    chromo_1 = self._pop.population[i1].chromosome[:]
                    chromo_2 = self._pop.population[i2].chromosome[:]

                    [new_chromo_1, new_chromo_2] = self._pop.crossover(chromo_1, chromo_2)

                    new_population_chromosomes.append(new_chromo_1[:])
                    new_population_chromosomes.append(new_chromo_2[:])

            # Put the chromosomes obtained by tournament selection and crossover into population before mutation
            self.__updateChromosomesAfterTournamentAndCrossover(new_population_chromosomes)

            # Mutation process
            self._pop.mutate(self._pop.population, self._mut_rate)

            # Obtain the value of the variables, the objective functions, value for limiting
            # variables and check if feasible of the population
            self._pop.decode(self._pop.population, var_range)
            self._pop.nulliffyFeasibility(self._pop.population)
            self._pop.evaluate(self._pop.population, of_function, lim_functions)

            if self._n_lim > 0:
                self._pop.checkFeasibility(self._pop.population, lim_range)

            if self.__found_best:
                self.__introduceElitism(var_range, of_function, lim_functions, lim_range)

            if self.__found_best:
                best_fitness_over_iter.append([generation + 1, self._pop.population[self.__best_index].getOf()[0],
                                               self._pop.population[self.__best_index].getLimVar(),
                                               self._pop.population[self.__best_index].getVar()])

            # Count amount of feasibles
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
        header = 'Generation, '
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

        #TODO put all this into a function
        if self.__found_best:
            self.__selectElitism()
            str_best = '\nThe best found individual:\n\tDesign variables:\n'
            best_var = self._pop.population[self.__best_index].getVar()
            for i in range(self._n_var):
                str_best +='\t\t%s = %.10f\n' % (self._var_names[i], best_var[i])
            if self._n_lim:
                best_lim = self._pop.population[self.__best_index].getLimVar()
                str_best += '\tLimiting variables:\n'
                for i in range(self._n_lim):
                    str_best += '\t\t%s = %.10f\n' % (self._lim_var_names[i], best_lim[i])
            str_best += ('\tFitness value:\n\t\t%s = %.10f\n' % (self._of_names[0], self._pop.population[self.__best_index].getOf()[0]))
            print(str_best)
        else:
            print('\nNo individual that fulfills all constraints has been found!!\n')

        if not self._n_lim:
            return
        else:
            return [[], perc_feasibles_over_iter]


    def __updateChromosomesAfterTournamentAndCrossover(self, chromosomes):
        for i in range(self._pop_size):
            self._pop.population[i].chromosome = chromosomes[i][:]

    def __selectElitism(self):
        self.__found_best = False
        if self._max_min == 'max':
            self.__best_fitness = -float('inf')
            for i in range(self._pop_size):
                if self._pop.population[i].getOf()[0] >= self.__best_fitness and self._pop.population[i].getFeasibility():
                    self.__best_fitness = self._pop.population[i].getOf()[0]
                    self.__best_index = i
                    self.__best_chromosome = self._pop.population[i].chromosome[:]
                    self.__found_best = True

        elif self._max_min == 'min':
            self.__best_fitness = float('inf')
            for i in range(self._pop_size):
                if self._pop.population[i].getOf()[0] <= self.__best_fitness and self._pop.population[i].getFeasibility():
                    self.__best_fitness = self._pop.population[i].getOf()[0]
                    self.__best_index = i
                    self.__best_chromosome = self._pop.population[i].chromosome[:]
                    self.__found_best = True

    def __introduceElitism(self, var_range, of_function, lim_functions, lim_range):
        count = 0
        introduced = False
        while (not introduced) and count < self._pop_size:
            count +=1
            r = random.randint(0,self._pop_size-1)
            if self._max_min == 'max':
                if self._pop.population[r].getOf()[0] < self.__best_fitness or not self._pop.population[r].getFeasibility():
                    self._pop.population[r].chromosome = self.__best_chromosome[:]
                    self.__best_index = r
                    introduced = True
            elif self._max_min == 'min':
                if self._pop.population[r].getOf()[0] > self.__best_fitness or not self._pop.population[r].getFeasibility():
                    self._pop.population[r].chromosome = self.__best_chromosome[:]
                    self.__best_index = r
                    introduced = True
        if introduced:
            self._pop.population[self.__best_index].decodeChromosome(var_range)
            self._pop.population[self.__best_index].evaluate(of_function, lim_functions)
            self._pop.population[self.__best_index].checkFeasibility(lim_range)

    def __checkInputs(self, var_range, range_gen):
        """Check if some of the given inputs need to be corrected. For instance, the size of the population has to
        be an even number."""
        correct_inputs = True
        print("Performing some checks on the inputs...")
        # Check if the length of range variables is equal to n_var
        if self._n_var != len(var_range):
            correct_inputs = False
            sys.exit('\n\nFINISHING RUN!!!\nThe number of variables and len(var_range) does not match!!\n\n')
        # Check if pop_size is an even number
        if self._pop_size % 2 != 0:
            correct_inputs = False
            print('\tpop_size changed from %d to %d, since it must be an even number!' % \
                  (self._pop_size, self._pop_size + 1))
            self._pop_size = self._pop_size + 1

        if correct_inputs:
            print("All the checks were satisfactory!")
        else:
            print("The inputs have been corrected!")

    def _waitbar(self, i, N, toolbar_width=50):
        """Displays a waitbar representing the progress of the EA"""
        perc = float((i + 1) / N)
        perc_bar = int(perc * toolbar_width)
        bar = '[%s>%s] %d%%' % ('=' * (perc_bar - 1), ' ' * (toolbar_width - perc_bar), int(perc * 100))
        sys.stdout.write('\r%s' % (bar))
        sys.stdout.flush()


class NSGA_II(GA):
    def __init__(self, var_names, of_names, lim_var_names, n_var, n_of, n_lim, max_min, any_int_var, int_var_indexes, confEA):

        super().__init__(var_names, of_names, lim_var_names, n_var, n_lim, max_min, any_int_var, int_var_indexes, confEA)
        self.__n_of = n_of

        # Some default settings
        self.__type_dist = 1
        self.__compare_w_data = False
        self.__n_to_select = -1

        self.__perc_rank1 = confEA.perc_rank1
        self.__perc_nf = confEA.perc_nf

        try:
            self.__n_to_select = confEA.n_to_select
        except:
            pass

        if self.__n_to_select > 0:
            self.__type_dist = confEA.type_dist
            self.__compare_w_data = confEA.compare_w_data

    def optimize(self, project_name, var_range, of_functions, var_data, of_data, lim_range_orig, \
                 range_gen, lim_functions, mod_lim_range):
        """Runs the NSGA-II optimization algorithm with the given objective and limiting functions for a given
        number of generations"""

        # Some checks:
        self.__checkInputs(var_range, range_gen)

        # population
        if not self._any_int_var:
            self._pop = populations.PopulationsMOGA(self._pop_size, self._n_var, self._n_gen_var,
                                                            self.__n_of, self._n_lim)
        else:
            self._pop = populations.PopulationsMOGAIntegerVar(self._pop_size, self._n_var, self._n_gen_var,
                                                                      self.__n_of, self._n_lim, self._int_var_indexes)
        # Initialize populationP
        self._pop.initialize()

        # Obtain the value of the variables, the objective functions, value for limiting
        # variables and check if feasible of population
        self._pop.decode(self._pop.population, var_range)
        self._pop.nulliffyFeasibility(self._pop.population)
        self._pop.evaluate(self._pop.population, of_functions, lim_functions)

        if self._n_lim > 0:
            # Check which limitation range has to be used
            if range_gen > 0:
                lim_range = mod_lim_range
            else:
                lim_range = lim_range_orig
            self._pop.checkFeasibility(self._pop.population, lim_range)

        # Assign ranking to individuals by splitting population into feasible and unfeasible
        pop_f = []
        pop_nf = []
        for ind in self._pop.population:
            if ind.getFeasibility():
                pop_f.append(ind)
            else:
                pop_nf.append(ind)

        [pop_fp, rank_list_fp] = self._pop.rankPopulation(pop_f, self._max_min)
        [pop_nfp, rank_list_nfp] = self._pop.rankPopulation(pop_nf, self._max_min)

        self._pop.population = pop_fp + pop_nfp
        for i in range(len(rank_list_nfp)):
            for j in range(len(rank_list_nfp[i])):
                rank_list_nfp[i][j] += len(pop_fp)

        # Assign crowded distance to every individual of the initial population
        self._pop.crowdedDistance(self._pop.population, rank_list_fp, rank_list_nfp)

        perc_feasibles_over_iter = []

        # Beginning of the loop over the generations
        print('Evaluating NSGA_II generations:')
        for generation in range(self._n_gen):
            self._waitbar(generation, self._n_gen)

            if self._n_lim > 0:
                # Check what the range of the limitations is based on range_gen
                if generation + 1 <= self._n_gen * range_gen:
                    lim_range = mod_lim_range
                else:
                    lim_range = lim_range_orig

            # Nullify population Q and PQ
            self._pop.populationQ = []
            self._pop.populationPQ = []

            # Nullify feasibility of population and recheck
            self._pop.nulliffyFeasibility(self._pop.population)
            if self._n_lim > 0:
                self._pop.checkFeasibility(self._pop.population, lim_range)

            for i in range(int(self._pop_size / 2)):
                # Generate populationQ by applying tournament selection, crossover and mutation
                # on pupulationP

                # Tournament selection process (always done on population)
                i1 = self._pop.tournamentSelection(self._tour_sel_param)
                i2 = self._pop.tournamentSelection(self._tour_sel_param)

                # Crossover process
                r = random.random()
                if r > self._cross_rate:
                    self._pop.addIndividualWithChromosomeToPopulationQ(self._pop.population[i1].chromosome)
                    self._pop.addIndividualWithChromosomeToPopulationQ(self._pop.population[i2].chromosome)
                else:
                    chromo_1 = self._pop.population[i1].chromosome[:]
                    chromo_2 = self._pop.population[i2].chromosome[:]

                    [new_chromo_1, new_chromo_2] = self._pop.crossover(chromo_1, chromo_2)

                    self._pop.addIndividualWithChromosomeToPopulationQ(new_chromo_1)
                    self._pop.addIndividualWithChromosomeToPopulationQ(new_chromo_2)

            # Mutation process
            self._pop.mutate(self._pop.populationQ, self._mut_rate)

            # Obtain the value of the variables, the objective functions, value for limiting
            # variables and check if feasible of populationQ
            self._pop.decode(self._pop.populationQ, var_range)
            self._pop.nulliffyFeasibility(self._pop.populationQ)
            self._pop.evaluate(self._pop.populationQ, of_functions, lim_functions)

            if self._n_lim > 0:
                self._pop.checkFeasibility(self._pop.populationQ, lim_range)

            # Combine both population and populationQ to get populationPQ
            self._pop.populationPQ = self._pop.population + self._pop.populationQ
            # Assign ranking to individuals by splitting populationPQ into feasible and unfeasible
            pop_f = []
            pop_nf = []
            for ind in self._pop.populationPQ:
                if ind.getFeasibility():
                    pop_f.append(ind)
                else:
                    pop_nf.append(ind)

            [pop_fpq, rank_list_fpq] = self._pop.rankPopulation(pop_f, self._max_min)
            [pop_nfpq, rank_list_nfpq] = self._pop.rankPopulation(pop_nf, self._max_min)

            self._pop.populationPQ = pop_fpq + pop_nfpq

            for i in range(len(rank_list_nfpq)):
                for j in range(len(rank_list_nfpq[i])):
                    rank_list_nfpq[i][j] += len(pop_fpq)

            self._pop.obtainNewPopulationP(self.__perc_rank1, self.__perc_nf, rank_list_fpq, rank_list_nfpq)

            # Count the number of feasibles
            perc_feasibles_over_iter.append(self._pop.obtainPercentageOfFeasibles())

        ##=========================== Output section ===============================

        if self.__n_to_select > 0:
            # Assign ranking to individuals by splitting population into feasible and unfeasible
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

            # Select the best found individuals along pareto-front
            selected_indexes = self._pop.selectIndividuals(rank_list_fp, self.__n_to_select,
                                                           self.__type_dist, var_data, of_data,
                                                           self.__compare_w_data)

            # Write the four databases of the selected individuals
            self._pop.writeDataBase(project_name, self._of_names, self._var_names, self._lim_var_names, 0,
                                    selected_indexes)
            self._pop.writeDataBase(project_name, self._of_names, self._var_names, self._lim_var_names, 1,
                                    selected_indexes)

        # Write the four databases for final generation
        self._pop.writeDataBase(project_name, self._of_names, self._var_names, self._lim_var_names, 0)
        self._pop.writeDataBase(project_name, self._of_names, self._var_names, self._lim_var_names, 1)

        # Put the selected designs variables in a list for the output
        selected_designs = []

        if self.__n_to_select > 0:
            for i in selected_indexes:
                selected_designs.append(self._pop.population[i].getVar())

        print()
        if not self._n_lim:
            return selected_designs
        else:
            return [selected_designs, perc_feasibles_over_iter]

    def __checkInputs(self, var_range, range_gen):
        """Check if some of the given inputs need to be corrected. For instance, the size of the population has to
        be an even number."""
        correct_inputs = True
        print("Performing some checks on the inputs...")
        # Check if the length of range variables is equal to n_var
        if self._n_var != len(var_range):
            correct_inputs = False
            sys.exit('\n\nFINISHING RUN!!!\nThe number of variables and len(var_range) does not match!!\n\n')
        # Check if range_gen > 1
        if range_gen > 1 and self._n_lim > 0:
            correct_inputs = False
            print('\n\tWARNING!!!\n\trange_gen > 1, only mod_lim_range used!\n')
        # Check if pop_size is an even number
        if self._pop_size % 2 != 0:
            correct_inputs = False
            print('\tpop_size changed from %d to %d, since it must be an even number!' % \
                  (self._pop_size, self._pop_size + 1))
            self._pop_size = self._pop_size + 1

        # Check that perc_rank1 is not greater than 1
        if self.__perc_rank1 > 1:
            correct_inputs = False
            print("\tperc_rank1 > 1 --> perc_rank1 = 1!")
            self.__perc_rank1 = 1

        if self._n_lim == 0 and self.__perc_nf > 0:  # If the number of limitations is zero, the percentage corresponding
            # to the unfeasible is added to the rank1 percentage
            correct_inputs = False
            print("\tn_lim = 0 --> perc_rank1 += perc_nf and perc_nf = 0!")
            self.__perc_rank1 += self.__perc_nf
            self.__perc_nf = 0
            if self.__perc_rank1 > 1.0:
                print("\twith the last correction perc_rank1 > 1 --> perc_rank1 = 1!")
                self.__perc_rank1 = 1
        else:  # check that perc_nf + perc_rank1 <=1
            if self.__perc_nf + self.__perc_rank1 > 1:
                correct_inputs = False
                print("\tSince perc_nf + perc_rank1 > 1 --> perc_nf = 1 - perc_rank1!")
                self.__perc_nf = 1 - self.__perc_rank1

        if self.__n_to_select > self._pop_size:
            correct_inputs = False
            print("\tSince n_to_select > pop_size --> n_to_select = pop_size!")
            self.__n_to_select = self._pop_size
        if correct_inputs:
            print("All the checks were satisfactory!")
        else:
            print("The inputs have been corrected!")
