# srndi-circles
Solving sRND-I instances on circles comparing different approaches

The programs `create_random_circles.py` and `create_01.py` can be used to generate random instances of the single commodity robust network design problem using intervals (sRND-I).

Their output can be fed into `solve.py` which solves the instances with the ILOG CPLEX Solver. An iterative approach can be compared via the switch `--compare-iterative`.

If the switches `--compare-iterative`,`--add-declaration` and optionally `--show-iterative-steps` are used the output can be used to subsequently feed the output to `visualize.py` which uses matplotlib and networkx to visualize the results.

The program `find_bad.py` can be used to generate a certain amount of instances of a given problem and compare their respective solutions with iterative approach. It uses the `create_random_circles.py` and `solve.py` programs. It outputs the approximation factors and the worst instance.

## Requirements
* python3
* the ILOG CPLEX Solver and its python bindings

And the python packages:
* matplotlib
* networkx
* json5
* numpy

## Usage

All of the programs can be used from the commandline and the generation programs and the solving program can also be imported as python functions.

```
$ python3 create_random_circle.py --help
usage: Create random sRND circle scenario [-h] [-m B_MEAN] [-d B_DEV]
                                          [-c C_MEAN] [-s C_DEV]
                                          size [output]

positional arguments:
  size                  size of the circle
  output                output file (json5)

optional arguments:
  -h, --help            show this help message and exit
  -m B_MEAN, --distance-mean B_MEAN
                        the mean of the distance to 0 for the low and high
                        values
  -d B_DEV, --standard-deviation B_DEV
                        standard deviation of the low and high values
  -c C_MEAN, --cost-mean C_MEAN
                        standard mean of the cost values
  -s C_DEV, --cost-standard-deviation C_DEV
                        standard deviation of the cost values
```

```
$ python3 create_01.py --helpusage: Create random sRND 0-1 circle scenario [-h] [-c C_MEAN] [-s C_DEV]
                                              size [output]

positional arguments:
  size                  size of the circle
  output                output file (json5)

optional arguments:
  -h, --help            show this help message and exit
  -c C_MEAN, --cost-mean C_MEAN
                        standard mean of the cost values
  -s C_DEV, --cost-standard-deviation C_DEV
                        standard deviation of the cost values
```

```
$ python3 solve.py --help
usage: Solve sRND for circles with LPs [-h] [--duals] [--show-constraints]
                                       [--compare-iterative]
                                       [--show-iterative-steps]
                                       [--only-results] [--add-declaration]
                                       [--single-source-demand]
                                       [declaration] [output]

positional arguments:
  declaration           circle declaration file (json/json5)
  output                output file (json5)

optional arguments:
  -h, --help            show this help message and exit
  --duals               calculate float LP and display constraints with dual
                        != 0
  --show-constraints    show all main constraints
  --compare-iterative   compare iterative with complete solution
  --show-iterative-steps
                        show the steps of the iterative approach
  --only-results        show only the values of the solution
  --add-declaration     add the circle declaration to output
  --single-source-demand
                        calculate single source demand problem
```

```
$ python3 visualize.py --help
usage: Visualize solutions for sRND in circles [-h] [--show-iterative-steps]
                                               [--add-lines]
                                               [solution]

positional arguments:
  solution              solution file (json/json5)

optional arguments:
  -h, --help            show this help message and exit
  --show-iterative-steps
                        show the steps of the iterative approach
  --add-lines           add lines for all constraints that need to be
                        satisfied
```
