import unittest
import sys
import random
import os

from src import populations


class TestPopulationGA(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        def of1(*vars):
            return vars[0] + vars[1]

        def l1(*vars):
            return -vars[0] * vars[1]

        print('Running tests for Population class and it\'s derived classes of GAs...')
        cls.pop_size = 5
        cls.n_var = 2
        cls.n_gen_var = 5
        cls.n_of = 1
        cls.n_lim = 1
        cls.var_range = [[0., 1.], [-2., 3.5]]
        cls.lim_range = [['greater', -0.1]]
        cls.max_min = ['min']
        cls.objective_functions = [of1]
        cls.limiting_functions = [l1]

    def setUp(self):
        random.seed(1)
        self.pop = populations.PopulationGA(self.pop_size, self.n_var, self.n_gen_var, self.n_of, self.n_lim)
        self.pop.initialize()

    def tearDown(self):
        del self.pop

    def test_population_GA_with_random_generation(self):
        chromosomes_individuals = [[0, 1, 1, 0, 0, 0, 1, 1, 0, 0],
                                   [1, 0, 1, 0, 0, 1, 0, 1, 1, 0],
                                   [0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 1, 1, 1, 0],
                                   [1, 1, 0, 0, 1, 1, 1, 0, 1, 1]]

        for indv in range(self.pop_size):
            self.assertEqual(self.pop.population[indv].getChromosome(), chromosomes_individuals[indv])

    def test_population_GA_mutate(self):
        mutation_rate = 0.3
        self.pop.mutate(self.pop.population, mutation_rate)

        chromosomes_mutated = [[0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 1, 0, 0, 1, 0, 1, 1, 0],
                               [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                               [0, 0, 0, 1, 0, 0, 1, 1, 0, 0],
                               [1, 0, 0, 0, 1, 1, 1, 0, 1, 1]]

        for indv in range(self.pop_size):
            self.assertEqual(self.pop.population[indv].getChromosome(), chromosomes_mutated[indv])


    def test_population_GA_decode_chromosome(self):
        self.pop.decode(self.pop.population, self.var_range)

        variables = [[0.3870, 0.1290],
                     [0.6451, 1.9032],
                     [0.3870, -2.000],
                     [0.0000, 0.4838],
                     [0.8064, 2.7903]]

        for indv in range(self.pop_size):
            for var in range(self.n_var):
                self.assertAlmostEqual(self.pop.population[indv].getVar()[var], variables[indv][var], places=3)

    def test_population_GA_evaluate_and_feasibility(self):
        self.pop.decode(self.pop.population, self.var_range)
        self.pop.evaluate(self.pop.population, self.objective_functions, self.limiting_functions)

        objective_functions = [0.5161, 2.5483, -1.6129, 0.4838, 3.5967]
        limiting_functions = [-0.0499, -1.2278, 0.7741, 0.000, -2.2502]

        for indv in range(self.pop_size):
            self.assertAlmostEqual(self.pop.population[indv].getOf()[0], objective_functions[indv], places=3)
            self.assertAlmostEqual(self.pop.population[indv].getLimVar()[0], limiting_functions[indv], places=3)

        self.pop.checkFeasibility(self.pop.population, self.lim_range)

        feasibility_individuals = [True, False, True, True, False]

        for indv in range(self.pop_size):
            self.assertEqual(self.pop.population[indv].getFeasibility(), feasibility_individuals[indv])

    def test_population_GA_tournament_selection(self):
        tournament_selection_param = 0.9
        self.pop.decode(self.pop.population, self.var_range)
        self.pop.evaluate(self.pop.population, self.objective_functions, self.limiting_functions)

        winner_1 = 4
        winner_2 = 3

        self.assertEqual(self.pop.tournamentSelection(tournament_selection_param, self.max_min), winner_1)
        self.assertEqual(self.pop.tournamentSelection(tournament_selection_param, self.max_min), winner_2)

    def test_population_GA_crossover(self):
        chromosome_1 = [0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1]
        chromosome_2 = [1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0]
        cross_chromo_1 = [0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0]
        cross_chromo_2 = [1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1]

        [cross_chromo_1_computed, cross_chromo_2_computed] = self.pop.crossover(chromosome_1, chromosome_2)

        self.assertEqual(cross_chromo_1, cross_chromo_1_computed)
        self.assertEqual(cross_chromo_2, cross_chromo_2_computed)


if __name__ == '__main__':
    unittest.main()
