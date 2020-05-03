import argparse
from sys import stdout

import json5
from numpy.random import normal, choice
from numpy import round

parser = argparse.ArgumentParser('Create random sRND 0-1 circle scenario')
parser.add_argument('size', help='size of the circle', type=int)
parser.add_argument('output', nargs='?', type=argparse.FileType('w'), default=stdout, help='output file (json5)')
# parser.add_argument('-m', '--distance-mean', help='the mean of the distance to 0 for the low and high values', type=float, default=3, dest='v_mean')
# parser.add_argument('-d', '--standard-deviation', help='standard deviation of the low and high values', type=float, default=1, dest='v_dev')
parser.add_argument('-c', '--cost-mean', help='standard mean of the cost values', type=float, default=5, dest='c_mean')
parser.add_argument('-s', '--cost-standard-deviation', help='standard deviation of the cost values', type=float, default=1, dest='c_dev')
args = parser.parse_args()

def create_vertex():
    # if choice(2) == 0:
    #     return {
    #         'low': -1,
    #         'high': 0
    #     }
    # else:
    #     return {
    #         'low': 0,
    #         'high': 1
    #     }
    # values = choice([-1, 0, 1], 2).astype(int).tolist()
    # return {
    #     'low': min(values),
    #     'high': max(values)
    # }
    a = 0
    b = 0
    # while a == 0 and b == 0:
    while a == b:
        vals = choice([-1, 0, 1], 2).astype(int).tolist()
        a = min(vals)
        b = max(vals)
    return {
        'low': a,
        'high': b
    }


def create_cost():
    c = 0
    while c <= 0:
        c = round(normal(args.c_mean, args.c_dev, size=1)).astype(int).tolist()[0]
    return c


declaration = {
    'vertices': [create_vertex() for _ in range(args.size)],
    'edge_costs': [create_cost() for _ in range(args.size)]
}

json5.dump(declaration, args.output, indent=2)
