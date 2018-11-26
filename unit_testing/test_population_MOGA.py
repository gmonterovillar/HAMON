import unittest
import sys
import random
import os

dirname, filename = os.path.split(os.path.abspath(__file__))
sys.path.append(dirname + '/../src')

import populations


class TestPopulationGA(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        def of1(*vars):
            return vars[0] + vars[1] + vars[0]**0.5

        def of2(*vars):
            return -vars[0]*vars[1] + vars[1]**2

        print('Running tests for MOEA Population class...')
        cls.pop_size = 10
        cls.n_var = 2
        cls.n_gen_var = 5
        cls.n_of = 2
        cls.n_lim = 0
        cls.var_range = [[0., 1.], [-2., 3.5]]
        cls.max_min = ['max', 'min']
        cls.objective_functions = [of1, of2]
        cls.limiting_functions = []

    def setUp(self):
        random.seed(1)
        self.pop = populations.PopulationsMOGA(self.pop_size, self.n_var, self.n_gen_var, self.n_of, self.n_lim)
        self.pop.initialize()

    def tearDown(self):
        del self.pop

    def test_ranking_MOEA_population(self):
        self.pop.decode(self.pop.population, self.var_range)
        self.pop.evaluate(self.pop.population, self.objective_functions, self.limiting_functions)
        [self.pop.population, _] = self.pop.rankPopulation(self.pop.population, self.max_min)

        ranks = [1, 1, 3, 2, 1, 1, 1, 2, 1, 1]

        for indv in range(self.pop_size):
            self.assertEqual(self.pop.population[indv].getRank(), ranks[indv])

    def test_crowded_distance_and_crowded_distance_one_set_MOEA(self):
        self.pop.decode(self.pop.population, self.var_range)
        self.pop.evaluate(self.pop.population, self.objective_functions, self.limiting_functions)
        [self.pop.population, rank_list] = self.pop.rankPopulation(self.pop.population, self.max_min)
        self.pop.crowdedDistance(self.pop.population, rank_list, [])

        crowded_distances = [float('inf'), 0.8448, float('inf'), float('inf'), 0.7268, 0.7368, 0.4282, float('inf'),
                             0.6667, float('inf')]

        # Check the crowdedDistance function
        for indv in range(self.pop_size):
            self.assertAlmostEqual(self.pop.population[indv].getCrowdedDistance(), crowded_distances[indv], places=3)

        for rank in rank_list:
            ranked_set=self.pop.crowdedDistanceOneSet(list(self.pop.population[j] for j in rank), self.n_of)
            for indv in range(len(rank)):
                self.pop.population[rank[indv]] = ranked_set[indv]

        # Check the crowdedDistanceOneSet function
        for indv in range(self.pop_size):
            self.assertAlmostEqual(self.pop.population[indv].getCrowdedDistance(), crowded_distances[indv], places=3)



if __name__ == '__main__':
    unittest.main()
