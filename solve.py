import json5
import argparse
from sys import stdout, stdin
from docplex.mp.model import Model


def solve(declaration, calc_duals=False, calc_iterative=False, singleSourceDemand=False, output_cts=False, output_steps=False, output_only_results=False, output_declaration=False):
    n = len(declaration['edge_costs'])
    out = {}

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

    def calculate_b(vertices):
        # calculate the right sides of the inequations
        s_low_sum = sum(v['low'] for v in vertices)
        s_high_sum = sum(v['high'] for v in vertices)
        b = []
        for nodes in subset_nodes:
            s_low = sum(vertices[node]['low'] for node in nodes)
            s_high = sum(vertices[node]['high'] for node in nodes)
            left = min(s_high, s_low - s_low_sum)
            right = min(-s_low, s_high_sum - s_high)
            b.append(max(left, right))
        return b

    def simplify_vertices(vertices):
        simplified = []
        for node in vertices:
            other_low = max(max(-v['low'], 0) if v != node else 0 for v in vertices)
            other_high = max(max(v['high'], 0) if v != node else 0 for v in vertices)
            simplified.append(max(min(-node['low'], other_high), min(node['high'], other_low)))
        return simplified

    def calculate_r(s_vertices):
        r = []
        for nodes in subset_nodes:
            r.append(max(s_vertices[node] for node in nodes))
        return r

    b = []
    if not singleSourceDemand:
        b = calculate_b(declaration['vertices'])
    else:
        b = calculate_r(simplify_vertices(declaration['vertices']))

    def calculate_b_min(vertices):
        low = [0 if node['low'] <= 0 else node['low'] for node in vertices]
        high = [0 if node['high'] >= 0 else -node['high'] for node in vertices]
        return max(sum(low), sum(high), 1)

    b_min = calculate_b_min(declaration['vertices'])
    b_max = max(b)

    def scal_prod(a, b):
        return sum([x * y for (x, y) in zip(a, b)])

    # creates a LP for given b and solves it
    def solve_lp(b):
        if b_min > b_max:
           return None, None, [0] * n, None

        model = Model(name='circle')

        if calc_duals:
            capacities = model.continuous_var_list(n)
        else:
            capacities = model.integer_var_list(n)

        # set up constraints
        model.add_constraints([c >= 0 for c in capacities])
        main_cts = [capacities[i] + capacities[j] >= b for ((i, j), b) in zip(subset_edges, b)]
        model.add_constraints(main_cts)

        target_expr = model.scal_prod(capacities, declaration['edge_costs'])
        model.minimize(target_expr)

        sol = model.solve()
        sol_values = [sol[c] for c in capacities]

        if calc_duals:
            # get duals if wanted
            duals = model.dual_values(main_cts)
            return main_cts, target_expr, sol_values, duals
        else:
            return main_cts, target_expr, sol_values, None


    def create_output(main_cts, target_expr, sol_values, duals):
        out = {}
        if output_cts:
            out['program'] = {
                'target': f'{target_expr}',
                'constraints': [f'{ct}' for ct in main_cts]
            }

        out['value'] = sum([u * c for (u, c) in zip(sol_values, declaration['edge_costs'])])

        if not output_only_results:
            if calc_duals:
                out['capacities'] = [sol_values[i] for i in range(n)]
            else:
                out['capacities'] = [int(sol_values[i]) for i in range(n)]

        if calc_duals:
            out['duals'] = {}
            for i in range(n**2):
                if duals[i] > 0:
                    out['duals'][f'S({subset_edges[i][0]}, {subset_edges[i][1]})'] = duals[i]

        return out

    def solve_iteratively(b):
        if output_steps:
            out['steps'] = []

        # last_u represents the accumulated edge capacities for all extensions so far
        last_u = [0] * n
        for i in range(b_min, b_max + 1):
            # b_part is like b but capped at a max flow of i
            b_part = [min(b_i, i) for b_i in b]
            # calculate the right side of the extension problem
            b_ext = [b_part[j] - last_u[left] - last_u[right] for j, (left, right) in enumerate(subset_edges)]
            solution = solve_lp(b_ext)
            if output_steps:
                step_out = create_output(*solution)
                step_out['max_flow'] = i
                out['steps'].append(step_out)

            last_u = [u + e for (u, e) in zip(last_u, solution[2])]
        out['iterative'] = create_output([], [], last_u, [])

        return last_u

    c = declaration['edge_costs']
    solution = solve_lp(b)

    out['optimal'] = create_output(*solution)

    if calc_iterative:
        u = solve_iteratively(b)

        if b_min <= b_max:
            value = scal_prod(solution[2], c)
        else:
            value = 0
        value_it = scal_prod(u, c)

        factor = 9999
        if value == 0:
            if value_it == 0:
                factor = 1
        else:
            factor = value_it / value

        out['comparison'] = {
            'edge_cost_sum': sum(c),
            'difference': value_it - value,
            'factor': factor
        }

    if output_declaration:
        out['declaration'] = declaration

    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Solve sRND for circles with LPs')
    parser.add_argument('declaration', nargs='?', type=argparse.FileType('r'), default=stdin, help='circle declaration file (json/json5)')
    parser.add_argument('output', nargs='?', type=argparse.FileType('w'), default=stdout, help='output file (json5)')
    parser.add_argument('--duals', help='calculate float LP and display constraints with dual != 0', action='store_true')
    parser.add_argument('--show-constraints', help='show all main constraints', dest='cts', action='store_true')
    parser.add_argument('--compare-iterative', help='compare iterative with complete solution', dest='iterative', action='store_true')
    parser.add_argument('--show-iterative-steps', help='show the steps of the iterative approach', dest='show_steps', action='store_true')
    parser.add_argument('--only-results', help='show only the values of the solution', dest='only_results', action='store_true')
    parser.add_argument('--add-declaration', help='add the circle declaration to output', dest='add_declaration', action='store_true')
    parser.add_argument('--single-source-demand', help='calculate single source demand problem', dest='singleSourceDemand',
                        action='store_true')
    args = parser.parse_args()

    declaration = json5.load(args.declaration)

    out = solve(declaration, calc_duals=args.duals, calc_iterative=args.iterative, singleSourceDemand=args.singleSourceDemand, output_cts=args.cts, output_steps=args.show_steps, output_only_results=args.only_results, output_declaration=args.add_declaration)

    json5.dump(out, args.output, indent=2)
