"""Independent infinite H-orbit five-coloring certificates.

This checker never imports the coloring producer or a SAT solver.  It first
replays the complete independent gain-graph checker (including T125's bound
and all orbit equalities), then checks the explicit words and palette actions.
The recorded SAT formula hash, solver statistics and timings are historical
search metadata, not part of this mathematical verification.
"""

from copy import deepcopy
from pathlib import Path
import argparse
import hashlib
import json
import time

from verify_quintic_core_probe import digest
from verify_rotation_orbit_contacts import verify as verify_contacts


IDENTITY = [0, 1, 2, 3, 4]
PALETTE_ACTIONS = [[0, 2, 3, 1, 4], [0, 2, 3, 4, 1]]
RESULT_KEYS = {
    'kind', 'eta_color_permutation', 'u_color_permutation', 'vertices',
    'clauses', 'formula_sha256', 'contact_certificate_sha256',
    'conflict_budget', 'solver', 'scope', 'status', 'stats', 'word', 'seconds',
}


def _order(permutation):
    assert type(permutation) is list
    assert all(type(x) is int for x in permutation)
    assert sorted(permutation) == IDENTITY
    current = IDENTITY[:]
    for order in range(1, 61):
        current = [permutation[x] for x in current]
        if current == IDENTITY:
            return order
    raise AssertionError('No permutation order found')


def _power(permutation, exponent, order):
    assert type(exponent) is int
    current = IDENTITY[:]
    for _ in range(exponent % order):
        current = [permutation[x] for x in current]
    return current


def _check(data, context, contact_sha):
    if not __debug__:
        raise RuntimeError('Verification requires assertions; do not use -O.')
    assert type(data) is dict
    assert set(data) == {'schema', 'kind', 'results', 'scope'}
    assert type(data['schema']) is int and data['schema'] == 1
    assert data['kind'] == 'rotation_orbit_five_colorings'
    assert data['scope'] == ('Two exact positive words; infinite conclusion requires '
                             'independent complete contact verification and T125.')
    assert type(data['results']) is list and len(data['results']) == 2
    contacts = context['contacts']
    origin_neighbors = context['origin_neighbors']
    representatives = context['representatives']
    equalities = context['equalities']
    source_edges = context['source_context']['edges']
    assert len(contacts) == 22377 and len(origin_neighbors) == 60
    assert len(representatives) == 4176 and len(source_edges) == 49858
    assert equalities['zero_indices'] == [4641]
    assert equalities['total_nonzero_returns'] == 39580
    repindex = {source: i for i, source in enumerate(representatives)}
    self_contacts = [list(edge) for edge in contacts if edge[0] == edge[1]]
    assert len(self_contacts) == 6
    assert all(h == 0 and n == 2 for i, j, h, n in self_contacts)
    # Each such genuine edge joins r_i and u^2*r_i. A coloring invariant
    # under u^P with P=1 or P=2 would assign it equal colors, for ANY palette.
    # This proves only the period obstruction, never a chromatic obstruction.
    assert all(2 % period == 0 for period in (1, 2))
    reports, lifted_words = [], []
    for position, result in enumerate(data['results']):
        assert type(result) is dict and set(result) == RESULT_KEYS
        assert result['kind'] == 'rotation_graph_palette_equivariant_search'
        assert result['status'] == 'SAT'  # The explicit word, not this tag, is tested below.
        assert result['scope'] == ('Positive witnesses cover all H-orbit points; '
                                   'failure only concerns this fixed global palette action.')
        assert result['contact_certificate_sha256'] == contact_sha
        assert type(result['vertices']) is int and result['vertices'] == len(representatives)
        assert type(result['clauses']) is int
        assert result['clauses'] == 11 * len(representatives) + 5 * len(contacts) + len(origin_neighbors)
        tau, sigma = result['eta_color_permutation'], result['u_color_permutation']
        tau_order, sigma_order = _order(tau), _order(sigma)
        assert tau == IDENTITY and tau_order == 1
        assert sigma == PALETTE_ACTIONS[position]
        assert sigma_order == (3, 4)[position]
        assert tau[0] == sigma[0] == 0
        assert _power(tau, 5, tau_order) == IDENTITY
        assert all(tau[sigma[c]] == sigma[tau[c]] for c in IDENTITY)
        word = result['word']
        assert type(word) is str and len(word) == len(representatives)
        assert set(word) == set('01234')
        colors = list(map(int, word))
        sigma_powers = {n: _power(sigma, n, sigma_order) for n in range(-12, 13)}
        tau_powers = {h: _power(tau, h, tau_order) for h in range(5)}

        def moved(color, h, n):
            assert h in tau_powers and n in sigma_powers
            return tau_powers[h][sigma_powers[n][color]]

        assert all(colors[i] != 0 for i in origin_neighbors)
        for i, j, h, n in contacts:
            assert colors[i] != moved(colors[j], h, n)
        # Commuting permutations lift these finitely many checks to every
        # translated gain edge. Fixing 0 makes the origin's star safe in all
        # layers, including negative n.
        assert all(moved(colors[i], h, n) != 0
                   for i in origin_neighbors for h in range(5)
                   for n in range(sigma_order))
        assert all(_power(sigma, sigma_order, sigma_order)[color] == color
                   for color in colors)
        assert all(any(_power(sigma, period, sigma_order)[color] != color
                       for color in colors)
                   for period in range(1, sigma_order))

        # Pull back to the entire checked source graph Y. This is an extra
        # direct cross-check independent of its normalization into contacts.
        source_colors = []
        for source, coordinate in enumerate(equalities['coordinates']):
            if coordinate is None:
                assert source == 4641
                source_colors.append(0)
            else:
                representative, h, n = coordinate
                source_colors.append(moved(colors[repindex[representative]], h, n))
        assert len(source_colors) == 10077
        assert all(source_colors[i] != source_colors[j] for i, j in source_edges)
        return_checks = 0
        for action in equalities['all_actions']:
            h, n = action['h'], action['n']
            for i, j in action['mapping']:
                assert source_colors[j] == moved(source_colors[i], h, n)
                return_checks += 1
        assert return_checks == 39580
        source_word = ''.join(map(str, source_colors))
        lifted_words.append(source_word)
        reports.append(dict(
            u_palette_permutation=sigma, eta_palette_permutation=tau,
            exact_u_period=sigma_order, representative_word_sha256=digest(word),
            source_word_sha256=digest(source_word), gain_edge_checks=len(contacts),
            origin_representative_checks=len(origin_neighbors),
            all_phase_origin_checks=5 * sigma_order * len(origin_neighbors),
            source_edge_checks=len(source_edges), source_return_checks=return_checks))
    assert reports[0]['exact_u_period'] == 3
    # A two-port boundary test for the OLD tau partial isometry. The point
    # equalities are checked in the exact field, not looked up from a saved
    # motion list. Both new words agree at the source pair and disagree at
    # its image. Equality is invariant under every global color renaming;
    # H shifts of these words are such renamings. Thus ANY probability
    # mixture supported on these two H-shift/renaming families still has
    # source-event probability 1 and image-event probability 0. This only
    # excludes that support family, not the full space of proper words.
    source_pair, image_pair = [32, 36], [6268, 6256]
    source_geometry = context['source_context']
    field_mul = source_geometry['ring']['mul']
    tau_rotation = source_geometry['ring']['tau']
    geometry_points = source_geometry['points']
    assert all(field_mul(tau_rotation, geometry_points[i]) == geometry_points[j]
               for i, j in zip(source_pair, image_pair))
    pair_colors = []
    for word in lifted_words:
        before = [int(word[i]) for i in source_pair]
        after = [int(word[i]) for i in image_pair]
        assert before[0] == before[1] and after[0] != after[1]
        pair_colors.append(dict(source=before, image=after))
    assert pair_colors == [dict(source=[0, 0], image=[4, 1]),
                           dict(source=[3, 3], image=[4, 2])]
    return dict(
        words=reports, self_u_squared_contacts=self_contacts,
        forbidden_u_periods_for_any_palette=[1, 2],
        smallest_possible_positive_u_period=3,
        origin_color=0, colors=5,
        tau_mixture_separator=dict(
            source_pair=source_pair, image_pair=image_pair,
            exact_point_image_checks=2, word_pair_colors=pair_colors,
            equality_event_probability_source=1, equality_event_probability_image=0,
            scope='Only mixtures of these two words and their global color '
                  'renamings/H shifts; not a full proper-word obstruction.'),
        search_metadata_not_replayed=['formula_sha256', 'conflict_budget',
                                      'solver', 'stats', 'seconds'],
        scope='Proper five-colorings of the complete induced H=<eta,u> orbit graph; '
              'no plane coloring, translation closure, NON5, or new original HN bound.'), lifted_words


def _mutations(data, context, contact_sha):
    rejected = []

    def reject(name, mutate):
        damaged = deepcopy(data)
        mutate(damaged)
        try:
            _check(damaged, context, contact_sha)
        except (AssertionError, KeyError, TypeError, ValueError):
            rejected.append(name)
        else:
            raise AssertionError('Mutation accepted: ' + name)

    def set_color(d, index, color):
        word = d['results'][0]['word']
        d['results'][0]['word'] = word[:index] + str(color) + word[index+1:]

    i, j, _, _ = next(edge for edge in context['contacts']
                      if edge[2:] == [0, 0] or tuple(edge[2:]) == (0, 0))
    reject('ordinary_gain_edge_made_monochromatic',
           lambda d: set_color(d, i, d['results'][0]['word'][j]))
    reject('origin_neighbor_colored_zero',
           lambda d: set_color(d, context['origin_neighbors'][0], 0))
    reject('nonpalette_color', lambda d: set_color(d, 0, 5))
    reject('short_word', lambda d: d['results'][0].__setitem__('word', d['results'][0]['word'][:-1]))
    reject('identity_u_palette_action',
           lambda d: d['results'][0].__setitem__('u_color_permutation', IDENTITY[:]))
    reject('nonbijective_u_palette_action',
           lambda d: d['results'][0]['u_color_permutation'].__setitem__(2, 2))
    reject('origin_not_fixed',
           lambda d: d['results'][0].__setitem__('u_color_permutation', [1, 2, 3, 0, 4]))
    reject('nonidentity_eta_palette_action',
           lambda d: d['results'][0].__setitem__('eta_color_permutation', [1, 2, 3, 4, 0]))
    reject('changed_contact_binding',
           lambda d: d['results'][0].__setitem__('contact_certificate_sha256', '0' * 64))
    reject('missing_positive_word', lambda d: d['results'].pop())
    return rejected


def verify(root, mutation_tests=False, progress=False, geometry_context=False):
    if not __debug__:
        raise RuntimeError('Verification requires assertions; do not use -O.')
    started = time.monotonic()
    root = Path(root)
    path = root / 'certificates/rotation_orbit_colorings.json'
    raw = path.read_bytes()
    data = json.loads(raw)
    contact_report, context = verify_contacts(
        root, progress=progress, geometry_context=True)
    assert contact_report['status'] == 'PASS'
    details, lifted_words = _check(data, context, contact_report['certificate_sha256'])
    mutations = _mutations(data, context, contact_report['certificate_sha256']) if mutation_tests else []
    report = dict(status='PASS', kind=data['kind'], certificate_sha256=hashlib.sha256(raw).hexdigest(),
                  contact_certificate_sha256=contact_report['certificate_sha256'],
                  complete_contact_graph_replayed=True,
                  mutation_rejections=mutations,
                  elapsed_seconds=round(time.monotonic() - started, 3), **details)
    if geometry_context:
        return report, dict(context, source_color_words=lifted_words, coloring_report=details)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mutation-tests', action='store_true')
    parser.add_argument('--progress', action='store_true')
    args = parser.parse_args()
    print(json.dumps(verify(Path(__file__).resolve().parents[1],
                            args.mutation_tests, args.progress), indent=2))
