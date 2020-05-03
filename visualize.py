from math import ceil

import json5
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import lines as mpl_lines
import argparse
from sys import stdout, stdin
import numpy as np

parser = argparse.ArgumentParser('Visualize solutions for sRND in circles')
parser.add_argument('solution', nargs='?', type=argparse.FileType('r'), default=stdin,
                    help='solution file (json/json5)')
parser.add_argument('--show-iterative-steps', help='show the steps of the iterative approach', dest='show_steps',
                    action='store_true')
parser.add_argument('--add-lines', help='add lines for all constraints that need to be satisfied', dest='show_lines',
                    action='store_true')

args = parser.parse_args()


def slope_from_points(point1, point2):
    return (point2[1] - point1[1])/(point2[0] - point1[0])


def plot_secant(point1, point2, ax):
    # plot the secant
    slope = slope_from_points(point1, point2)
    intercept = point1[1] - slope*point1[0]
    # update the points to be on the axes limits
    x = ax.get_xlim()
    y = ax.get_ylim()
    data_y = [x[0]*slope+intercept, x[1]*slope+intercept]
    line = mpl_lines.Line2D(x, data_y, color='red', alpha=0.3)
    ax.add_line(line)
    # return ax.figure()


def create_graph(capacities):
    G = nx.Graph()
    n = len(capacities)
    for (i, c) in enumerate(capacities):
        G.add_edge(i, (i + 1) % n, capacity=c)
    return G


def draw_initial_graph(circle, ax):
    G = nx.Graph()
    n = len(circle['vertices'])
    node_labels = {}
    edge_labels = {}
    for (i, (v, c)) in enumerate(zip(circle['vertices'], circle['edge_costs'])):
        G.add_edge(i, (i + 1) % n)
        edge_labels[(i, (i + 1) % n)] = c
        node_labels[i] = f'[{v["low"]}, {v["high"]}]'
    pos = nx.circular_layout(G)
    nx.draw(G, pos=pos, ax=ax, alpha=0.3)
    nx.draw_networkx_labels(G, pos, labels=node_labels)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)


def draw_graph(capacities, ax):
    G = create_graph(capacities)
    pos = nx.circular_layout(G)
    nx.draw(G, pos=pos, ax=ax, alpha=0.3)
    edge_labels = nx.get_edge_attributes(G, 'capacity')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    return pos


solution = json5.load(args.solution)
fig = plt.figure()

ax1 = fig.add_subplot(1, 3, 1)
ax1.margins(0.25, 0.25)
ax1.title.set_text('Bedarf und Kosten')
draw_initial_graph(solution['declaration'], ax1)

ax2 = fig.add_subplot(1, 3, 2)
ax2.margins(0.25, 0.25)
ax2.title.set_text('Optimale Lösung')
draw_graph(solution['optimal']['capacities'], ax2)

ax3 = fig.add_subplot(1, 3, 3)
ax3.margins(0.25, 0.25)
ax3.title.set_text('Iterative Lösung')
draw_graph(solution['iterative']['capacities'], ax3)

plt.show()

if args.show_steps:
    circle = solution['declaration']
    n = len(circle['vertices'])

    # find the nodes of all relevant subsets
    subset_nodes = []
    for i in range(n):
        subset = []
        for j in range(n - 1):
            subset.append((i + j) % n)
            subset_nodes.append(subset.copy())

    # find the outgoing edges of each subset
    subset_edges = []
    for subset in subset_nodes:
        left = (subset[0] - 1) % n
        right = subset[-1]
        subset_edges.append((left, right))

    # calculate the right sides of the inequations
    b = []
    s_low_sum = sum(v['low'] for v in circle['vertices'])
    s_high_sum = sum(v['high'] for v in circle['vertices'])
    for nodes in subset_nodes:
        s_low = sum(circle['vertices'][node]['low'] for node in nodes)
        s_high = sum(circle['vertices'][node]['high'] for node in nodes)
        b.append(max(min(s_high, s_low - s_low_sum), min(-s_low, s_high_sum - s_high)))

    fig = plt.figure()
    fig.suptitle('Schritte der iterativen Lösung')
    cols = 4
    rows = ceil(len(solution['steps']) / cols)

    u = np.zeros(n)
    for (i, step) in enumerate(solution['steps']):
        ax = fig.add_subplot(rows, cols, i + 1)
        ax.title.set_text(f'max flow {i+1}')
        ax.margins(0.25, 0.25)
        pos = draw_graph(step['capacities'], ax)
        if args.show_lines:
            for (set_b, nodes, edges) in zip(b, subset_nodes, subset_edges):
                if min(set_b, i + 1) > u[edges[0]] + u[edges[1]]:
                    a = (pos[edges[0]] + pos[(edges[0] + 1) % n]) / 2
                    c = (pos[edges[1]] + pos[(edges[1] + 1) % n]) / 2
                    plot_secant(a, c, ax)
        u = u + step['capacities']
    plt.show()
