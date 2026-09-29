"""Focused mutation checks for the independent E115 finite-pool verifier."""
from copy import deepcopy
from pathlib import Path
import unittest
from unittest.mock import patch

import verify_joined_seed_pricing as verifier


ROOT = Path(__file__).resolve().parents[1]
CERT_PATH = ROOT / 'certificates/joined_seed_pricing.json.gz'
COMPACT_PATH = ROOT / 'certificates/eta_joined_three_compact.json.gz'
CACHE_PATH = ROOT / 'certificates/test-only-joined-seed-cache.json.gz'


class JoinedSeedPricingVerifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # One independent geometry reconstruction supplies the authenticated
        # cache fixture to all mutation cases. The default no-cache CLI path
        # has its own checked-in positive receipt and is exercised separately.
        cls.data, cls.summary = verifier.reconstruct(ROOT)
        cls.cert, cls.cert_raw = verifier.read_json_gzip(CERT_PATH)
        cls.compact, cls.compact_raw = verifier.read_json_gzip(COMPACT_PATH)

    def check_certificate(self, mutate=None):
        cert = deepcopy(self.cert)
        if mutate:
            mutate(cert)

        def fake_read(path):
            path = Path(path)
            if path == CERT_PATH:
                return cert, self.cert_raw
            if path == COMPACT_PATH:
                return self.compact, self.compact_raw
            if path == CACHE_PATH:
                return self.data, b'test-cache'
            raise AssertionError('unexpected verifier input: ' + str(path))

        with patch.object(verifier, 'read_json_gzip', side_effect=fake_read):
            return verifier.verify(ROOT, CACHE_PATH, CERT_PATH, COMPACT_PATH,
                                   rebuild_geometry=False)

    def assert_rejected(self, mutate):
        with self.assertRaises((ValueError, AssertionError)):
            self.check_certificate(mutate)

    def test_valid_finite_pool_certificate(self):
        report = self.check_certificate()
        self.assertEqual(report['status'], 'PASS')
        self.assertEqual(report['experiment'], 'E115')
        self.assertEqual(report['pool_words'], 11)
        self.assertEqual(report['final_pool_status'], 'EXACT_POOL_SEPARATOR')
        self.assertEqual(report['run_status'], 'ROUND_LIMIT_UNKNOWN')
        self.assertFalse(report['all_word_obstruction_certified'])

    def test_rejects_corrupted_pricing_word(self):
        def mutate(cert):
            cert['run']['words'][8] = '0' * len(cert['run']['words'][8])
        self.assert_rejected(mutate)

    def test_rejects_wrong_new_row_count(self):
        def mutate(cert):
            cert['run']['history'][0]['new_row_count'] = 0
        self.assert_rejected(mutate)

    def test_rejects_wrong_price(self):
        def mutate(cert):
            cert['run']['history'][0]['price'] += 1
        self.assert_rejected(mutate)

    def test_rejects_semantic_identity_change(self):
        def mutate(cert):
            cert['input_semantic_sha256'] = '0' * 64
        self.assert_rejected(mutate)

    def test_rejects_round_pool_cut_change(self):
        def mutate(cert):
            cert['run']['history'][0]['pool_values'][0] = 0
        self.assert_rejected(mutate)

    def test_rejects_final_pool_cut_change(self):
        def mutate(cert):
            cert['run']['final_pool_values'][0] = 0
        self.assert_rejected(mutate)

    def test_rejects_seed_word_change(self):
        def mutate(cert):
            cert['seed_words'][0] = '0' * len(cert['seed_words'][0])
        self.assert_rejected(mutate)

    def test_rejects_seed_source_upgrade(self):
        def mutate(cert):
            cert['seed_sources'][0] = 'newly-certified-global-law'
        self.assert_rejected(mutate)

    def test_rejects_global_positive_law_upgrade(self):
        def mutate(cert):
            cert['run']['status'] = 'EXACT_POSITIVE_LAW'
        self.assert_rejected(mutate)

    def test_rejects_final_positive_law_upgrade(self):
        def mutate(cert):
            cert['run']['final_pool_status'] = 'EXACT_POSITIVE_LAW'
            cert['run']['full_law'] = ['1'] + ['0'] * (len(cert['run']['words']) - 1)
            cert['run']['status'] = 'EXACT_POSITIVE_LAW'
        self.assert_rejected(mutate)

    def test_rejects_unsupported_global_obstruction_upgrade(self):
        def mutate(cert):
            cert['run']['status'] = 'ALL_WORDS_OBSTRUCTED'
        self.assert_rejected(mutate)


if __name__ == '__main__':
    unittest.main(verbosity=2)
