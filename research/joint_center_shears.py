"""Three unrestricted residue words with mod-11 shear and mod-3 centers.

Positive witnesses give upper bounds after independent checking. All negative
solver returns here are search observations, never actual-host lower bounds.
"""
from itertools import product
from pathlib import Path
import argparse
import json

from parts_core import clauses

ROOT = Path(__file__).resolve().parents[1]
UNIT = {(x, y) for x, y in product(range(11), repeat=2) if (x*x+y*y) % 11 == 1}


def transports():
    result = []
    for m, n in product(range(-3, 4), repeat=2):
        shell = m*m+m*n+n*n
        if shell not in (3, 4):
            continue
        coefficient = 7 if shell == 3 else 9
        for sign in (-1, 1):
            result.append((m, n, -sign*coefficient*5*n*6 % 11,
                           sign*coefficient*(2*m+n)*6 % 11))
    return result


def projected(matrix):
    a, b, c, d = matrix
    return [(m, n, (x+a*m+b*n) % 11, (y+c*m+d*n) % 11)
            for m, n, x, y in transports()]


def edges_for(matrix, joint=True):
    rows = [(0, 0, x, y) for x, y in UNIT]
    rows += [row for row in projected(matrix) if joint or (row[0]-row[1]) % 3 == 0]
    states = range(3) if joint else range(1)
    return sorted({tuple(sorted((121*r+11*x+y,
                                 121*((r+m-n) % 3 if joint else 0)+11*((x+u) % 11)+(y+v) % 11)))
                   for r in states for x, y in product(range(11), repeat=2)
                   for m, n, u, v in rows})


def run(single_budget, joint_budget, maximum, output, generators=18):
    from pysat.solvers import Solver
    matrices = []
    for matrix in product(range(11), repeat=4):
        steps = UNIT | {(x, y) for m, n, x, y in projected(matrix) if (m-n) % 3 == 0}
        if len(steps) == generators and (0, 0) not in steps:
            matrices.append(matrix)
    print(dict(candidate_matrices=len(matrices), N3_generator_count=generators), flush=True)
    counts = dict(single_SAT=0, single_UNSAT_unchecked=0, single_UNKNOWN=0,
                  joint_SAT=0, joint_UNSAT_unchecked=0, joint_UNKNOWN=0)
    observations = []
    anchors = [[5*v+c+1] for c, v in enumerate((0, 11, 74))]
    for matrix in matrices[:maximum]:
        single = edges_for(matrix, joint=False)
        with Solver(name='cadical195', bootstrap_with=clauses(121, single, 5)+anchors) as solver:
            solver.conf_budget(single_budget)
            status = solver.solve_limited()
            if status is not True:
                counts['single_UNKNOWN' if status is None else 'single_UNSAT_unchecked'] += 1
                observations.append(dict(matrix=matrix, single=status))
                continue
            counts['single_SAT'] += 1
            model = set(solver.get_model())
            word = [next(c for c in range(5) if 5*i+c+1 in model) for i in range(121)]
        joint = edges_for(matrix)
        with Solver(name='cadical195', bootstrap_with=clauses(363, joint, 5)+anchors) as solver:
            solver.set_phases([5*(121*r+i)+word[i]+1 for r in range(3) for i in range(121)])
            solver.conf_budget(joint_budget)
            status = solver.solve_limited()
            key = 'joint_UNKNOWN' if status is None else ('joint_SAT' if status else 'joint_UNSAT_unchecked')
            counts[key] += 1
            stats = solver.accum_stats()
            observations.append(dict(matrix=matrix, single=True, joint=status, statistics=stats))
            print(dict(matrix=matrix, edges=len(joint), joint=status, **counts), flush=True)
            if status is True:
                model = set(solver.get_model())
                word = ''.join(str(next(c for c in range(5) if 5*i+c+1 in model)) for i in range(363))
                result = dict(schema=1, matrix=matrix, word=word, vertices=363,
                              edges=len(joint), beta=[40, 169], counts=counts,
                              single_budget=single_budget, joint_budget=joint_budget,
                              observations=observations, scope='Candidate whole-K^2+alphaLambda five-color upper bound; independent verification required')
                if output:
                    Path(output).write_text(json.dumps(result, separators=(',', ':'))+'\n')
                return result
    print(dict(final_counts=counts, tried=len(observations)), flush=True)
    return counts


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--single-budget', type=int, default=10000)
    parser.add_argument('--joint-budget', type=int, default=10000)
    parser.add_argument('--maximum', type=int, default=239)
    parser.add_argument('--generators', type=int, choices=(18, 20, 22, 24), default=18)
    parser.add_argument('--output')
    args = parser.parse_args()
    run(args.single_budget, args.joint_budget, args.maximum, args.output, args.generators)
