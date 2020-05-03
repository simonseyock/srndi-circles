import argparse
from sys import stdout
import json5
from numpy.random import normal
from numpy import round


def create_circle(size, b_mean, b_dev, c_mean, c_dev):
    def create_vertex():
        values = round([normal(b_mean, b_dev), normal(-b_mean, b_dev)]).astype(int).tolist()
        return {
            'low': min(values),
            'high': max(values)
        }

    def create_cost():
        c = 0
        while c <= 0:
            c = round(normal(c_mean, c_dev, size=1)).astype(int).tolist()[0]
        return c

    return {
        'vertices': [create_vertex() for _ in range(size)],
        'edge_costs': [create_cost() for _ in range(size)]
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Create random sRND circle scenario')
    parser.add_argument('size', help='size of the circle', type=int)
    parser.add_argument('output', nargs='?', type=argparse.FileType('w'), default=stdout, help='output file (json5)')
    parser.add_argument('-m', '--distance-mean', help='the mean of the distance to 0 for the low and high values', type=float, default=3, dest='b_mean')
    parser.add_argument('-d', '--standard-deviation', help='standard deviation of the low and high values', type=float, default=1, dest='b_dev')
    parser.add_argument('-c', '--cost-mean', help='standard mean of the cost values', type=float, default=5, dest='c_mean')
    parser.add_argument('-s', '--cost-standard-deviation', help='standard deviation of the cost values', type=float, default=1, dest='c_dev')
    args = parser.parse_args()

    result = create_circle(args.size, args.b_mean, args.b_dev, args.c_mean, args.c_dev)
    json5.dump(result, args.output, indent=2)