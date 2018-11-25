import unittest
import sys
import random

sys.path.append('../src')

import individual


class TestIndividual(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        def of1(*vars):
            return vars[0] + vars[2] - vars[3] - vars[1]

        def of2(*vars):
            return vars[1] + vars[2] - 3 * vars[3]

        def l1(*vars):
            return -vars[0] + 2 - vars[1]

        def l2(*vars):
            return (vars[0] - 0.5) * 2 + (vars[1] - 0.5) ** 2 - 0.5

        print('Running tests for Individual class and it\'s derived classes...')
        cls.n_var = 4
        cls.n_gen_var = 5
        cls.n_of = 2
        cls.n_lim = 2
        cls.var_range = [[0., 1.], [-2., 3.5], [-5., -4], [12.1, 15.2]]
        cls.lim_range = [['lower', 2.], [-1., 0.]]
        cls.objective_functions = [of1, of2]
        cls.limiting_functions = [l1, l2]

    def setUp(self):
        random.seed(1)
        self.individual_1 = individual.IndividualGA(self.n_var, self.n_gen_var, self.n_of, self.n_lim)
        self.individual_2 = individual.IndividualGA(self.n_var, self.n_gen_var, self.n_of, self.n_lim)

    def tearDown(self):
        del self.individual_1, self.individual_2

    def test_individual_GA_with_random_generation(self):
        chromosome_1 = [0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0]
        chromosome_2 = [0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0]

        self.assertEqual(self.individual_1.getChromosome(), chromosome_1)
        self.assertEqual(self.individual_2.getChromosome(), chromosome_2)

    def test_chromosome_decoding(self):
        self.individual_1.decodeChromosome(self.var_range)
        self.individual_2.decodeChromosome(self.var_range)

        variables_1 = [0.3870, 0.1290, -4.3548, 14.3]
        variables_2 = [0.3870, -2.000, -5.0000, 13.5]

        for i in range(self.n_var):
            self.assertAlmostEqual(variables_1[i], self.individual_1.getVar()[i], places=3)
            self.assertAlmostEqual(variables_2[i], self.individual_2.getVar()[i], places=3)

    def test_GA_mutation(self):
        mutated_chromosome_1 = [0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 1, 0]
        mutated_chromosome_2 = [1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0]
        mutation_rate_1 = 0.2
        mutation_rate_2 = 0.65

        self.individual_1.mutate(mutation_rate_1)
        self.individual_2.mutate(mutation_rate_2)

        self.assertEqual(self.individual_1.getChromosome(), mutated_chromosome_1)
        self.assertEqual(self.individual_2.getChromosome(), mutated_chromosome_2)

    def test_function_evaluation_and_feasibility(self):
        self.individual_1.decodeChromosome(self.var_range)
        self.individual_2.decodeChromosome(self.var_range)

        self.individual_1.evaluate(self.objective_functions, self.limiting_functions)
        self.individual_2.evaluate(self.objective_functions, self.limiting_functions)

        objectives_1 = [-18.3967, -47.1258]
        limitations_1 = [1.4838, -0.5881]
        objectives_2 = [-16.1129, -47.5]
        limitations_2 = [3.6129, 5.5241]

        for i in range(self.n_of):
            self.assertAlmostEqual(objectives_1[i], self.individual_1.getOf()[i], places=3)
            self.assertAlmostEqual(objectives_2[i], self.individual_2.getOf()[i], places=3)

        for i in range(self.n_of):
            self.assertAlmostEqual(limitations_1[i], self.individual_1.getLimVar()[i], places=3)
            self.assertAlmostEqual(limitations_2[i], self.individual_2.getLimVar()[i], places=3)

        self.individual_1.checkFeasibility(self.lim_range)
        self.individual_2.checkFeasibility(self.lim_range)

        self.assertEqual(self.individual_1.getFeasibility(), True)
        self.assertEqual(self.individual_2.getFeasibility(), False)

    def test_individual_GA_integer_var(self):
        indv_integer_1 = individual.IndividualGAIntegerVar(self.n_var, self.n_gen_var, self.n_of, self.n_lim, [2])
        indv_integer_2 = individual.IndividualGAIntegerVar(self.n_var, self.n_gen_var, self.n_of, self.n_lim, [3])

        indv_integer_1.decodeChromosome(self.var_range)
        indv_integer_2.decodeChromosome(self.var_range)

        variables_1 = [0.8064516129032258, 2.790322580645161, -5, 13.899999999999999]
        variables_2 = [0.45161290322580644, 0.4838709677419355, -4.903225806451613, 14]

        for i in range(self.n_var):
            self.assertAlmostEqual(variables_1[i], indv_integer_1.getVar()[i], places=3)
            self.assertAlmostEqual(variables_2[i], indv_integer_2.getVar()[i], places=3)

    def test_individual_DE_with_random_generation(self):
        individual_de_1 = individual.IndividualDE(self.n_var, self.var_range, self.n_of, self.n_lim)
        individual_de_2 = individual.IndividualDE(self.n_var, self.var_range, self.n_of, self.n_lim)

        variables_1 = [0.9925, 2.7297, -4.8791, 13.1313]
        variables_2 = [0.7214, 1.9115, -4.0635, 13.4085]

        for i in range(self.n_var):
            self.assertAlmostEqual(variables_1[i], individual_de_1.getVar()[i], places=3)
            self.assertAlmostEqual(variables_2[i], individual_de_2.getVar()[i], places=3)

    def test_individual_DE_integer_var(self):
        individual_de_1 = individual.IndividualDEIntegerVar(self.n_var, self.var_range, self.n_of, self.n_lim, [2])
        individual_de_2 = individual.IndividualDEIntegerVar(self.n_var, self.var_range, self.n_of, self.n_lim, [0])

        variables_1 = [0.9925, 2.7297, -5, 13.1313]
        variables_2 = [1, 1.9115, -4.0635, 13.4085]

        for i in range(self.n_var):
            self.assertAlmostEqual(variables_1[i], individual_de_1.getVar()[i], places=3)
            self.assertAlmostEqual(variables_2[i], individual_de_2.getVar()[i], places=3)


if __name__ == '__main__':
    unittest.main()
