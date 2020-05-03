import argparse
from os.path import join
from sys import stdout
from time import time
import numpy as np

import json5

from create_random_circle import create_circle
from solve import solve

parser = argparse.ArgumentParser('Solve sRND for circles with LPs')
parser.add_argument('output', nargs='?', type=argparse.FileType('w'), default=stdout, help='output file (json5)')
parser.add_argument('tries', help='how many instance should be tried', type=int)
parser.add_argument('size', help='size of the circle', type=int)
parser.add_argument('-o', '--output_dir', help='if set, output a conveniently named file to this output', type=str, default=None)
parser.add_argument('-m', '--distance-mean', help='the mean of the distance to 0 for the low and high values', type=float, default=3, dest='v_mean')
parser.add_argument('-d', '--standard-deviation', help='standard deviation of the low and high values', type=float, default=1, dest='v_dev')
parser.add_argument('-c', '--cost-mean', help='standard mean of the cost values', type=float, default=5, dest='c_mean')
parser.add_argument('-s', '--cost-standard-deviation', help='standard deviation of the cost values', type=float, default=1, dest='c_dev')
parser.add_argument('--single-source-demand', help='use single source demand problem variation', dest='singleSourceDemand',
                        action='store_true')
args = parser.parse_args()

worst_declaration = None
worst_value = 1
results = np.zeros(args.tries)

deformed = []

for i in range(args.tries):
    if (i+1) % 1000 == 0:
        print('|')
    elif (i+1) % 100 == 0:
        print('.', end='')

    circle = create_circle(args.size, args.v_mean, args.v_dev, args.c_mean, args.c_dev)
    solution = solve(circle, calc_iterative=True, output_only_results=True, singleSourceDemand=args.singleSourceDemand)
    factor = solution['comparison']['factor']
    results[i] = factor
    if factor > worst_value:
        worst_declaration = circle
        worst_value = factor

    if factor == 0:
        deformed.append(circle)

out = {
    'results': results.astype(float).tolist(),
    'worst_value': worst_value,
    'worst_declaration': worst_declaration,
    'mean': float(results.mean()),
    'std': float(np.std(results)),
    'deformed': deformed
}

if args.output_dir is None:
    json5.dump(out, args.output, indent=2)
else:
    pre = 'ssd' if args.singleSourceDemand else ''
    name = pre + f'tries_{args.tries}_size_{args.size}_vmean_{args.v_mean}_vdev_{args.v_dev}_cmean_{args.c_mean}_cdev_{args.c_dev}_{time()}.json5'
    with open(join(args.output_dir, name), 'w') as file:
        json5.dump(out, file, indent=2)
