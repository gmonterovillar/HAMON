import individual
import random
import numpy as np

class Population:
    def __init__(self, pop_size, n_var, n_of, n_lim):
        self._size = pop_size
        self._n_var = n_var
        self._n_lim = n_lim
        self._n_of = n_of
        self.population = []
        if self._n_of > 1:
            self.populationQ = []
            self.populationPQ = []

    def checkFeasibility(self, population, lim_range):
        """Check the feasibility of the individuals of the population"""
        for i in range(self._size):
            population[i].checkFeasibility(lim_range)

    def evaluate(self, population, of_functions, lim_functions):
        """Evaluate both the objective functions and the limiting variables of each individual"""
        for i in range(self._size):
            population[i].evaluate(of_functions, lim_functions)

    def nulliffyFeasibility(self, population):
        """Sets all the individuals of a population to feasible"""
        for i in range(len(population)):
            population[i].feasibility = True


class PopulationGA(Population):
    def __init__(self, pop_size, n_var, n_gen_var, n_of, n_lim):
        super().__init__(pop_size, n_var, n_of, n_lim)
        self._n_gen_var = n_gen_var
        self._n_genes = self._n_gen_var * self._n_var

    def initialize(self):
        """Initialize genes of the population with random genes"""
        for i in range(self._size):
            self.population.append(individual.IndividualGA(self._n_var, self._n_gen_var, self._n_of, self._n_lim))

    def decode(self, population, var_range):
        """Decodes the chromosomes of every individual in the population"""
        for i in range(self._size):
            population[i].decodeChromosome(var_range)

    def mutate(self, population, mut_rate):
        """Mutates all the genes of all the individuals with a probability of mut_rate"""
        for i in range(self._size):
            population[i].mutate(mut_rate)

    def crossover(self, chromo_1, chromo_2):
        """Perform one point crossover of two given chromosomes"""
        cross_point = random.randint(1, self._n_genes)
        new_chromo_1 = self.__zeros(self._n_genes)
        new_chromo_2 = self.__zeros(self._n_genes)
        new_chromo_1[:cross_point] = chromo_1[:cross_point]
        new_chromo_1[cross_point:] = chromo_2[cross_point:]
        new_chromo_2[:cross_point] = chromo_2[:cross_point]
        new_chromo_2[cross_point:] = chromo_1[cross_point:]
        return [new_chromo_1, new_chromo_2]

    def tournamentSelection(self, tour_sel_param, max_min):
        """Select one random individuals of the population using tournament selection of size two"""
        i1 = random.randint(0, self._size - 1)
        i2 = random.randint(0, self._size - 1)
        while i2 == i1:
            i2 = random.randint(0, self._size - 1)
        bool1 = self.population[i1].getFeasibility()
        bool2 = self.population[i2].getFeasibility()
        fit1 = self.population[i1].getOf()[0]
        fit2 = self.population[i2].getOf()[0]
        if bool1 > bool2:
            best = i1
        elif bool2 > bool1:
            best = i2
        else:
            # TODO check how non feasible individuals are compared
            if max_min == 'max':
                if fit1 > fit2:
                    best = i1
                else:
                    best = i2
            else:
                if fit1 < fit2:
                    best = i1
                else:
                    best = i2

        if random.random() > tour_sel_param:
            if best == i1:
                best = i2
            else:
                best = i1
        return best

    def __zeros(self, n):
        """Create a list containing n zeros"""
        list = []
        for i in range(n):
            list.append(0)
        return list


class PopulationGAIntegerVar(PopulationGA):
    """Class that stores the information for the different populations and performs mutation, crossover... on them.
    This class allows for variables that only accept int values. Population of GA."""

    def __init__(self, pop_size, n_var, n_gen_var, n_of, n_lim, int_var_indexes):
        super().__init__(pop_size, n_var, n_gen_var, n_of, n_lim)
        self.__int_var_indexes = int_var_indexes


    def initialize(self):
        """Initialize genes of the population with random genes and integer var individuals"""
        for i in range(self._size):
            self.population.append(individual.IndividualGAIntegerVar(self._n_var, self._n_gen_var, self._n_of, self._n_lim,
                                                                    self.__int_var_indexes))


class PopulationMOEA:

    def crowdedDistance(self, population, ranking_list_f, ranking_list_nf):
        """Assign the crowded distance to every individual to see how crowded it's area in the design space is."""
        for i in range(len(population)):
            population[i].setCrowdedDistance(0.)

        for of in range(self._n_of):
            for num in range(2):
                if num == 0:
                    ranking_list = ranking_list_f
                elif num == 1:
                    ranking_list = ranking_list_nf

                for set in ranking_list:
                    l = len(set)

                    crowded_dist_list = []
                    for i in range(l):
                        crowded_dist_list.append(0)

                    tupple_set = []
                    for i in range(l):
                        tupple_set.append((i, population[set[i]].getOf()[of], set[i]))
                    tupple_sorted = sorted(tupple_set, key=lambda x: x[1])

                    for i in range(l):
                        crowded_dist_list[tupple_sorted[i][0]] = population[tupple_sorted[i][2]].getCrowdedDistance()

                    for i in range(l):
                        if i == 0 or i == l - 1:
                            population[tupple_sorted[i][2]].setCrowdedDistance(float('inf'))
                        else:
                            if not tupple_sorted[0][1] - tupple_sorted[l - 1][1]:
                                population[tupple_sorted[i][2]].setCrowdedDistance(float('inf'))
                            else:
                                population[tupple_sorted[i][2]].setCrowdedDistance(
                                    crowded_dist_list[tupple_sorted[i][0]] + (tupple_sorted[i + 1][1] -
                                    tupple_sorted[i - 1][1]) / abs(tupple_sorted[0][1] -tupple_sorted[l - 1][1]))
                                crowded_dist_list[tupple_sorted[i][0]] = population[tupple_sorted[i][2]].getCrowdedDistance()

    def crowdedDistanceOneSet(self, set, n_of):
        """Compute the crowded distance for every individual in one set"""
        l = len(set)

        crowded_dist_list = []
        for i in range(l):
            crowded_dist_list.append(0)

        for i in range(l):
            set[i].setCrowdedDistance(0.)
        for objFunct in range(n_of):
            tupple_set = []
            for i in range(l):
                tupple_set.append((i, set[i].getOf()[objFunct]))
            tupple_sorted = sorted(tupple_set, key=lambda x: x[1])

            for i in range(l):
                crowded_dist_list[tupple_sorted[i][0]] = set[tupple_sorted[i][0]].getCrowdedDistance()

            for i in range(l):
                if i == 0 or i == l - 1:
                    set[tupple_sorted[i][0]].setCrowdedDistance(float('inf'))
                else:
                    if not tupple_sorted[0][1] - tupple_sorted[l - 1][1]:
                        set[tupple_sorted[i][0]].setCrowdedDistance(float('inf'))
                    else:
                        set[tupple_sorted[i][0]].setCrowdedDistance(crowded_dist_list[tupple_sorted[i][0]] +
                            (tupple_sorted[i + 1][1] - tupple_sorted[i - 1][1]) / abs(tupple_sorted[0][1] -
                            tupple_sorted[l - 1][1]))
                        crowded_dist_list[tupple_sorted[i][0]] = set[tupple_sorted[i][0]].getCrowdedDistance()

        return set

    def rankPopulation(self, population, max_min):
        """Fast-non-dominated-sort --> assigns a rank value to every individual"""
        pop = population[:]
        for i in range(len(pop)):
            pop[i].setRank(0)
        rank = 1
        Fi = []
        rank_list = []
        for p in range(len(pop)):
            pop[p].setCrowdedDistance([[], 0])
            Sp = []
            np = 0
            for q in range(len(pop)):
                if self._dominates(pop[p].getOf(), pop[q].getOf(), max_min):
                    Sp.append(q)
                elif self._dominates(pop[q].getOf(), pop[p].getOf(), max_min):
                    np = np + 1
            if not np:
                population[p].setRank(rank)
                Fi.append(p)
            x = [Sp[:], np]
            pop[p].setCrowdedDistance(x)
        crowded_dist = []
        for i in range(len(pop)):
            crowded_dist.append(pop[i].getCrowdedDistance()[1])

        while len(Fi) > 0:
            rank_list.append(Fi)
            Q = []
            for p in Fi:
                Sp = pop[p].getCrowdedDistance()[0][:]
                for q in Sp:
                    x = pop[q].getCrowdedDistance()
                    x[1] = crowded_dist[q] - 1
                    pop[q].setCrowdedDistance(x)
                    crowded_dist[q] = pop[q].getCrowdedDistance()[1]
                    if not pop[q].getCrowdedDistance()[1]:
                        pop[q].setRank(rank + 1)
                        Q.append(q)
            rank = rank + 1
            Fi = Q[:]
        for i in range(len(pop)):
            population[i] = pop[i]
            population[i].setCrowdedDistance(0.)

        return [population, rank_list]

    # TODO check how non feasible individuals are compared
    def _dominates(self, of_i1, of_i2, max_min):
        """Given two individuals checks if the first one dominates the second"""
        dom = True
        for i in range(len(max_min)):
            if max_min[i] == 'max' and of_i1[i] < of_i2[i]:
                dom = False
                break
            elif max_min[i] == 'min' and of_i1[i] > of_i2[i]:
                dom = False
                break
        if of_i1 == of_i2:
            dom = False
        return dom

    '''
    def selectIndividuals(self, rank_list, n_indiv_to_select, type_dist, var_data, of_data, compare_w_data):
        """Select the individual from the last population according to selected criteria"""
        rank = rank_list[0]
        count = 1
        pop_w_index = []
        selected_index = []
        indiv_check_w = []

        while len(rank) < n_indiv_to_select:
            rank_below = rank
            rank = rank + rank_list[count]
            count = count + 1
        if compare_w_data:
            for i in range(len(var_data)):
                indiv_check_w.append([var_data[i], of_data[i]])
        # If count>1 it means that there are not enough rank 1 individuals in order to satisfy the number of
        # selected required, hence all the necessary ranking except the last one checked are automatically selected
        # and then  rank_list[count - 1] is checked for distances
        if count > 1:
            for i in rank_below:
                indiv_check_w.append([self.population[i].getVar(), self.population[i].getOf()])
                selected_index.append(i)
        for i in rank_list[count - 1]:
            pop_w_index.append([i, self.population[i]])
        while len(selected_index) < n_indiv_to_select:
            dist_index = []
            for j in range(len(pop_w_index)):
                #TODO maybe try summing up all the distances instead of taking just the smallest one?
                min_dist = float('inf')
                for k in indiv_check_w:
                    if not type_dist:
                        dist_to_index = self.__norm(k[0], pop_w_index[j][1].getVar())
                    if type_dist == 1:
                        dist_to_index = self.__norm(k[1], pop_w_index[j][1].getOf())
                    if min_dist > dist_to_index:
                        min_dist = dist_to_index
                dist_index.append([pop_w_index[j][0], min_dist])
            sorted_by_distances = sorted(dist_index, key=lambda x: x[1], reverse=True)
            for i in sorted_by_distances:
                if (i[0] in selected_index) == False:
                    selected_index.append(i[0])
                    indiv_check_w.append([self.population[i[0]].getVar(), self.population[i[0]].getOf()])
                    break
        return selected_index
    '''

    def selectIndividuals(self, rank_list, n_indiv_to_select, type_dist, var_data, of_data, compare_w_data):
        """Select the individual from the last population according to selected criteria"""
        # TODO normalized the distances with the ranges found so that the weight doesnt affect the criteria
        rank = rank_list[0]
        count = 1
        pop_w_index = []
        selected_index = []
        indiv_check_w = []

        while len(rank) < n_indiv_to_select:
            rank_below = rank
            rank = rank + rank_list[count]
            count = count + 1
        if compare_w_data:
            for i in range(len(var_data)):
                indiv_check_w.append([var_data[i], of_data[i]])
        # If count>1 it means that there are not enough rank 1 individuals in order to satisfy the number of
        # selected required, hence all the necessary ranking except the last one checked are automatically selected
        # and then  rank_list[count - 1] is checked for distances
        if count > 1:
            for i in rank_below:
                indiv_check_w.append([self.population[i].getVar(), self.population[i].getOf()])
                selected_index.append(i)
        for i in rank_list[count - 1]:
            pop_w_index.append([i, self.population[i]])
        while len(selected_index) < n_indiv_to_select:
            dist_index = []
            for j in range(len(pop_w_index)):
                #TODO maybe try summing up all the distances instead of taking just the smallest one?

                #dist_to_index = 0.
                dist_to_index = float('inf')

                for k in indiv_check_w:
                    if type_dist == 0:

                        #dist_to_index += self.__norm(k[0], pop_w_index[j][1].getVar())
                        d = self.__norm(k[0], pop_w_index[j][1].getVar())
                        if d<dist_to_index:
                            dist_to_index = d

                    if type_dist == 1:

                        #dist_to_index += self.__norm(k[1], pop_w_index[j][1].getOf())
                        d = self.__norm(k[1], pop_w_index[j][1].getOf())
                        if d<dist_to_index:
                            dist_to_index = d

                dist_index.append([pop_w_index[j][0], dist_to_index])
            sorted_by_distances = sorted(dist_index, key=lambda x: x[1], reverse=True)
            for i in sorted_by_distances:
                if (i[0] in selected_index) == False:
                    selected_index.append(i[0])
                    indiv_check_w.append([self.population[i[0]].getVar(), self.population[i[0]].getOf()])
                    break
        return selected_index

    def obtainNewPopulationP(self, perc_rank1, perc_nf, rank_list_fpq, rank_list_nfpq):
        """From the combined population and populationQ, it generates a new population based on the given
        parameters"""

        self.population = []

        n_nf = int(perc_nf * self._size)
        n_rank1 = int(perc_rank1 * self._size)
        if n_nf + n_rank1 > self._size:
            n_nf = self._size - n_rank1

        # Make sure that there are enough feasible individuals, if not, request more non feasibles
        total_f = 0
        for rank_f in rank_list_fpq:
            total_f += len(rank_f)
        if total_f < self._size - n_nf:
            n_nf = self._size - total_f

        # First select the non feasible ones
        if n_nf > 0:
            for rank_I_list in rank_list_nfpq:
                crowded_set1 = self.crowdedDistanceOneSet(list(self.populationPQ[j] for j in rank_I_list), self._n_of)
                crowded_set_sorted1 = sorted(crowded_set1, key=lambda x: x.getCrowdedDistance(), reverse=True)
                if (len(crowded_set_sorted1) <= n_nf):
                    self.population += crowded_set_sorted1
                    n_nf -= len(crowded_set_sorted1)
                else:
                    crowded_set1_trimed = self.crowdedDistanceOneSet(crowded_set_sorted1[:n_nf], self._n_of)
                    self.population += crowded_set1_trimed
                    n_nf -= len(crowded_set1_trimed)
                if n_nf == 0:
                    break

        # Fill the rest of the population with ranking 1to fill the perc_rank1 criteria if posible
        crowded_set2 = self.crowdedDistanceOneSet(list(self.populationPQ[j] for j in rank_list_fpq[0]), self._n_of)
        crowded_set_sorted2 = sorted(crowded_set2, key=lambda x: x.getCrowdedDistance(), reverse=True)
        if len(crowded_set_sorted2) <= n_rank1:
            self.population += crowded_set_sorted2
        else:
            crowded_set2_trimed = self.crowdedDistanceOneSet(crowded_set_sorted2[:n_rank1], self._n_of)
            self.population += crowded_set2_trimed

        # If needed fill the rest of the population with ranking 2, 3...
        if len(self.population) < self._size:
            for rank_I_list in rank_list_fpq[1:]:
                indv_needed = self._size - len(self.population)
                crowded_set3 = self.crowdedDistanceOneSet(list(self.populationPQ[j] for j in rank_I_list), self._n_of)
                crowded_set_sorted3 = sorted(crowded_set3, key=lambda x: x.getCrowdedDistance(), reverse=True)
                if (len(crowded_set_sorted3) <= indv_needed):
                    self.population += crowded_set_sorted3
                else:
                    crowded_set3_trimed = self.crowdedDistanceOneSet(crowded_set_sorted3[:indv_needed], self._n_of)
                    self.population += crowded_set3_trimed
                if len(self.population) == self._size:
                    break

    def addIndividualWithChromosomeToPopulationQ(self, chromosome):
        """Adds an individual with a specified chromosome"""
        self.populationQ.append(individual.IndividualGA(self._n_var, self._n_gen_var, self._n_of, self._n_lim))
        self.populationQ[-1].chromosome = chromosome[:]

    def __norm(self, x, y):
        """Calculate the norm between two n-dimensional vectors"""
        n = 0
        for i in range(len(x)):
            n += (x[i] - y[i]) ** 2
        return n ** 0.5

    def writeDataBase(self, project_name, of_names, var_names, lim_var_names, summary, indexes=0):
        """ Writes data base of individual based on the following:
        summary = 0 writes complete, summary = 1 writes summary
        if a 0 is passed ad indexes then the entire population is written on the database,
        if a non empty list is passed, the corresponding individuals are written"""

        title = project_name
        if not indexes:
            title += '_fg'
            indexes = range(self._size)
        else:
            title += '_sel'

        if summary == 1:
            title += '_summary'

        output = open(title + '.csv', 'w')
        header_txt = 'indv,  '
        if summary == 1:
            for i in range(self._n_of):
                header_txt += '%s,  ' % (of_names[i])
            for i in range(self._n_lim):
                header_txt += '%s,  ' % (lim_var_names[i])
            header_txt += 'rank,  feasible?'
            output.write(header_txt + '\n')

            for i in indexes:
                indv_line = '%d,  ' % (i)
                for j in range(self._n_of):
                    indv_line += '%s,  ' % (str(self.population[i].getOf()[j]))
                for j in range(self._n_lim):
                    indv_line += '%sf,  ' % (str(self.population[i].getLimVar()[j]))
                indv_line += '%d,  %s' % (self.population[i].getRank(), self.population[i].getFeasibility())
                output.write(indv_line + '\n')

        else:
            for i in range(self._n_var):
                header_txt += '%s,  ' % (var_names[i])
            output.write(header_txt[:-3] + '\n')

            for i in indexes:
                indv_line = '%d,  ' % (i)
                for j in range(self._n_var):
                    indv_line += '%s,  ' % (str(self.population[i].getVar()[j]))
                output.write(indv_line[:-3] + '\n')
        output.close()

class PopulationsMOGA(PopulationGA, PopulationMOEA):
    """Class that stores the information for the different populations and performs mutation, crossover... on them"""

    def __init__(self, pop_size, n_var, n_gen_var, n_of, n_lim):
        super().__init__(pop_size, n_var, n_gen_var, n_of, n_lim)

    def tournamentSelection(self, tour_sel_param):
        """Select one random individuals of the population using tournament selection of size two"""
        i1 = random.randint(0, self._size - 1)
        i2 = random.randint(0, self._size - 1)
        rank1 = self.population[i1].getRank()
        rank2 = self.population[i2].getRank()
        bool1 = self.population[i1].getFeasibility()
        bool2 = self.population[i2].getFEasibility()
        if bool1 > bool2:
            best = i1
        elif bool2 > bool1:
            best = i2
        elif rank1 < rank2:
            best = i1
        elif rank1 > rank2:
            best = i2
        else:
            # TODO check how non feasible individuals are compared
            crowded_dist1 = self.population[i1].getCrowdedDistance()
            crowded_dist2 = self.population[i2].getCrowdedDistance()
            if crowded_dist2 > crowded_dist1:
                best = i2
            else:
                best = i1
        if random.random() > tour_sel_param:
            if best == i1:
                best = i2
            else:
                best = i1
        return best


class PopulationsMOGAIntegerVar(PopulationsMOGA):
    """Class that stores the information for the different populations and performs mutation, crossover... on them.
    This class allows for variables that only accept int values. Population of MOGA."""

    def __init__(self, pop_size, n_var, n_gen_var, n_of, n_lim, int_var_indexes):
        super().__init__(pop_size, n_var, n_gen_var, n_of, n_lim)
        self.__int_var_indexes = int_var_indexes

    def initialize(self):
        """Initialize genes of the population with random genes and integer var individuals"""
        for i in range(self._size):
            self.population.append(individual.IndividualGAIntegerVar(self._n_var, self._n_gen_var, self._n_of, self._n_lim,
                                                                    self.__int_var_indexes))

    def addIndividualWithChromosomeToPopulationQ(self, chromosome):
        """Adds an individual with a specified chromosome"""
        self.populationQ.append(individual.IndividualGAIntegerVar(self._n_var, self._n_gen_var, self._n_of, self._n_lim, self.__int_var_indexes))
        self.populationQ[-1].chromosome = chromosome[:]


class PopulationDE(Population):
    def __init__(self, pop_size, n_var, n_of, n_lim):
        super().__init__(pop_size, n_var, n_of, n_lim)
        self._Y = []
        self._Z = []

    def initialize(self, var_range):
        """Initialize parameter vectors of the population with random values. Also initialize Y and Z individuals"""
        for i in range(self._size):
            self.population.append(individual.IndividualDE(self._n_var, var_range, self._n_of, self._n_lim))
        self._Y = individual.IndividualDE(self._n_var, var_range, self._n_of, self._n_lim)
        self._Z = individual.IndividualDE(self._n_var, var_range, self._n_of, self._n_lim)

    def getCandidateByMutation(self, index, mut_rate, var_range, candidate_indexes):
        random_index = []
        while True:
            r_index = candidate_indexes[random.randint(0, len(candidate_indexes) - 1)]
            if not r_index in random_index:
                random_index.append(r_index)
                if len(random_index) == 3:
                    break

        self._Y.setVars(self.population[random_index[0]].getVar() + mut_rate * (
            self.population[random_index[1]].getVar() - self.population[random_index[2]].getVar()))

        # If any variable has gone out of range, put it equal to the mid point between the old value and the bound
        for i in range(self._n_var):
            if self._Y.getVar()[i] < var_range[i][0]:
                self._Y.setVar((var_range[i][0] + self.population[index].getVar()[i]) / 2., i)
            elif self._Y.getVar()[i] > var_range[i][1]:
                self._Y.setVar((var_range[i][1] + self.population[index].getVar()[i]) / 2., i)
        self._Y.fixIntegerVars(var_range)

    def getCandidateByRecombination(self, index, recomb_rate, var_range):
        ri = random.randint(0, self._n_var - 1)
        for i in range(self._n_var):
            r = random.random()
            if r <= recomb_rate or ri == i:
                self._Z.setVar(self._Y.getVar()[i], i)
            else:
                self._Z.setVar(self.population[index].getVar()[i], i)
        self._Z.fixIntegerVars(var_range)

    def selection(self, index, of_functions, lim_functions, lim_range, max_min):
        feas_X = True
        feas_Z = True
        self._Z.evaluate(of_functions, lim_functions)
        fit_Z = self._Z.getOf()[0]
        fit_X = self.population[index].getOf()[0]

        vars_to_return = np.zeros(self._n_var)

        if self._n_lim>0:
            self._Z.checkFeasibility(lim_range)
            feas_Z = self._Z.getFeasibility()
            feas_X = self.population[index].getFeasibility()

        best_Z = False
        # TODO check how non feasible individuals are compared
        if feas_X == False:
            best_Z = True
        if feas_X == True and feas_Z == True:
            if (max_min == 'min' and fit_Z <= fit_X) or (max_min == 'max' and fit_Z >= fit_X):
                best_Z = True

        if best_Z:
            for i in range(self._n_var):
                vars_to_return[i] = self._Z.getVar()[i]
        else:
            for i in range(self._n_var):
                vars_to_return[i] = self.population[index].getVar()[i]
        return vars_to_return


class PopulationDEIntegerVar(PopulationDE):
    def __init__(self, pop_size, n_var, n_of, n_lim, int_var_indexes):
        super().__init__(pop_size, n_var, n_of, n_lim)
        self._Y = []
        self._Z = []
        self.__int_var_indexes = int_var_indexes

    def initialize(self, var_range):
        """Initialize parameter vectors of the population with random values. Also initialize Y and Z individuals"""
        for i in range(self._size):
            self.population.append(individual.IndividualDEIntegerVar(self._n_var, var_range, self._n_of, self._n_lim, self.__int_var_indexes))
        self._Y = individual.IndividualDEIntegerVar(self._n_var, var_range, self._n_of, self._n_lim, self.__int_var_indexes)
        self._Z = individual.IndividualDEIntegerVar(self._n_var, var_range, self._n_of, self._n_lim, self.__int_var_indexes)


class PopulationsMODE(PopulationDE, PopulationMOEA):
    """Class that stores the information for the different populations and performs mutation, recombination... on them"""

    def __init__(self, pop_size, n_var, n_of, n_lim):
        super().__init__(pop_size, n_var, n_of, n_lim)

    def addIndividualZToPopulationQ(self, var_range):
        self.populationQ.append(individual.IndividualDE(self._n_var, var_range, self._n_of, self._n_lim))
        self.populationQ[-1].setVars(self._Z.getVar())

class PopulationsMODEIntegerVar(PopulationsMODE):
    """This class allows for variables that only accept int values. Population of MODE."""

    def __init__(self, pop_size, n_var, var_range, n_of, n_lim, int_var_indexes):
        super().__init__(pop_size, n_var, n_of, n_lim)
        self.__int_var_indexes = int_var_indexes

    def initialize(self, var_range):
        """Initialize parameter vectors of the population with random values. Also initialize Y and Z individuals. All as integer vars individuals"""
        for i in range(self._size):
            self.population.append(individual.IndividualDEIntegerVar(self._n_var, var_range, self._n_of, self._n_lim, self.__int_var_indexes))
        self._Y = individual.IndividualDEIntegerVar(self._n_var, var_range, self._n_of, self._n_lim, self.__int_var_indexes)
        self._Z = individual.IndividualDEIntegerVar(self._n_var, var_range, self._n_of, self._n_lim, self.__int_var_indexes)

    def addIndividualZToPopulationQ(self, var_range):
        self.populationQ.append(individual.IndividualDEIntegerVar(self._n_var, var_range, self._n_of, self._n_lim, self.__int_var_indexes))
        self.populationQ[-1].setVars(self._Z.getVar())

class PopulationPostMOEA(Population, PopulationMOEA):

    def __init__(self, data_base_file, n_var, n_of, n_lim):
        self.population = []
        self._n_var = n_var
        self._n_of = n_of
        self._n_lim = n_lim
        self._size = 0
        self._n_gen_var = 1
        self.initializeFromDataBase(data_base_file)

    def initializeFromDataBase(self, data_base_file):
        data_base = np.genfromtxt(data_base_file, skip_header=1, delimiter=',')
        self._size = len(data_base)
        print(self._size)
        print(data_base.shape)
        for i in range(self._size):
            if self._n_lim>0:
                lim_var = data_base[i, -self._n_lim:].tolist()
            else:
                lim_var = 0
            ofs = data_base[i, -self._n_lim-self._n_of:].tolist()
            vars = data_base[i,1: -self._n_lim-self._n_of].tolist()
            self.population.append(individual.IndividualGA(self._n_var, self._n_gen_var, self._n_of, self._n_lim))
            self.population[i].setOf(ofs)
            self.population[i].setVars(vars)
            self.population[i].setLimVar(lim_var)
