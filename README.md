# HAMON
Optimisation platform based on evolutionary algorithms.

Under the examples directory, several different examples on how to use HAMON can be found, these being,
1. Single-objective unconstrained, GA, De Jong’s fifth function
2. Single-objective contrained, DE, Golinski's speed reducer
3. Multi-objective unconstrained, GA (NSGA-II), ZDT 1
4. Multi-objective constrained, DE, TNK
5. Multi-objective unconstrained, DE, ZDT 1 using meta-modeling (RBFs)

In order to run all the examples execute the following
````
cd examples/
python3 execute_tests.py
````