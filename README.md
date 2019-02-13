# HAMON
HAMON is an optimization platform based on Evolutionary Algorithms (EA) written in Python. It can deal with single- and
multi-objective as well as constrained and unconstrained problems. It currently has implemented Genetic Algorithms (GA)
and Differential Evolution (DE) as the core of the optimization as well as meta-modeling based on Radial Basis Functions
(RBF) to help accelerate the process when each evaluation is computationally expensive.

## Methodology used
As previously mentioned HAMON can use GAs and DE together with RBF to solve optimization problems. A detailed 
description of the methods implemented can be found in the following two publications.
1. Montero Villar, G., Lindblad, D., and Andersson, N., “Multi-Objective Optimization of an Counter Rotating Open Rotor 
using Evolutionary Algorithms,” 2018 Multidisciplinary Analysis and Optimization Conference, 2018\
https://research.chalmers.se/en/publication/503802
2. Montero Villar, G., Lindblad, D., and Andersson, N., "Effect of Airfoil Parametrization on the Optimization of 
Counter Rotating Open Rotors", AIAA Scitech 2019 Forum, 2019\
[https://research.chalmers.se/en/publication/508621

## Input files
HAMON requires two input files in order to run, one concerning the optimization process where the inputs related to 
the optimization problem itself are specified, and one where the settings of the evolutionary algorithm are provided.

### Optimzation process input file
A python file containing the following variables needs to be provided.
#### Variables:
* `n_of`: number of objective functions, integer variable
* `n_var`: number of design variables, integer variable
* `var_range`: defines the variable ranges for each of the `n_var` variables. It must be a alist of length `n_var` 
where each item is either a list or a tuple containing two items; the first one is the lower bound and the second the 
upper bound. For example if `n_var = 2` and the first variable is allowed in the range 0 to 1 and the second one in the 
range -1 to 1, the input should be: `var_range = [[0., 1.], [-1., 1.]]`. 
* `n_lim`: number of constraints, integer variable
* `any_int_var`: boolean variable. `True` if some of the design variables are only allowed to have integer values and 
`False` if none.
* `int_var_indexes`: list containing the indixes of those variable that only accept integer values. If 
`any_int_var = False` the list can be left empty as it will not be used.
* `project_name`: name of the project that will be used for writing output files. String variable.
* `var_names`: list of length `n_var` where each item is a string containing the name of the corresponding the design 
variable. This names will be used for output generating purposes. If `var_names = []` default names will be used, these 
being; 'var_1', 'var_2' ...
* `of_names`: same as `var_names` but including the names of the objective functions and of length `n_of`. The default 
naming is 'of_1', 'of_2' ...
* `lim_var_names`: same as `var_names` and `of_names` but for the contraint variables and of length `n_lim`. The 
default naming is 'lim_var_1', 'lim_var_2' ...  
* `lim_range_orig`: true limits of each of the constraints. It must be a list of length `n_lim` where each item is one 
of these three option depending on the type of constraint. For example in a case with three constraints where the first 
one must be lower than zero, the second one greater than 2 and the third one between 1 and 3:\
`lim_range_orig = [('lower', 0.), ('greater', 2.), (1., 2.)]` 
* `mod_lim_range`: exact same definition as `lim_range_orig`. These constraints limits will be applied at the beginning 
of the optimization (in case `range_gen > 0`) with the intention to facilitate the finding of individuals that fullfil 
all constraints to help the optimization process.
* `range_gen`: floating point value between 0 and 1. It represents the fraction of total generations that are run by 
the EA where the constraints will be subjected to `mod_lim_range` instead of `lim_range_orig`.
* `max_min`: list of length `n_of` where each item must be 'min' or 'max' depending if the corresponding objective 
function is to be minimized or maximized during the optimization process.
* `analytical_funcs`: boolean variable. If set to `True` the objective functions and functions defining the constrains 
are evaluated for every individual during every iteration. If set to `False`, meta modeling is used in order to help 
accelerate the process. To get a more detailed description of the process used when RBFs are employed please refer to 
[1] and [2] as mentioned in tne **Methodology used** section. 
* `working_directory`: string containing the working directory relative to the path where the actual command to launch 
HAMON is executed. Absolute paths recommended.
* `plotting`: boolean variable. If `True`, when the EA is done optimizing, HAMON will show a plot of the evolution of 
the objective function of the best found individual in every generation if running single objective, or the population 
of the last generation in case of multi-objective. If there are any constraints, it will also plot the history of 
the percentage of individuals that fulfilled all the constrained over the generations. If set to `False` no plot
will be displayed.



## Examples
Under the `examples` directory, several cases demonstrating how to use HAMON and its capabilities can be found. These 
are separated into single- and mulit-objective problems.
* `test_1`: Single-objective unconstrained, GA, De Jong’s fifth function
* `test_2`: Single-objective contrained, DE, Golinski's speed reducer
* `test_3`: Multi-objective unconstrained, GA (NSGA-II), ZDT 1
* `test_4`: Multi-objective constrained, DE, TNK
* `test_5`: Multi-objective unconstrained, DE, ZDT 1 using meta-modeling (RBFs)

In order to run all the examples execute the following
````
cd examples/
python3 execute_tests.py
````

