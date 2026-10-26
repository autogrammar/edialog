import copy
import json
from pathlib import Path
import random
import subprocess
import sys
import unittest

from edialog.core import DSLError, parse, simulate, compare_observations

ROOT = Path(__file__).resolve().parents[1]
MINIMAL = '''affect 0.1
model illustrative
axis novelty
concept curiosity "Robocza definicja"
state curiosity 0.2 retention 0.5
driver curiosity novelty 0.5
event event_a novelty=0.8
explain curiosity
apply event_a ticks 1
checkpoint first
expect first curiosity >= 0.5
'''


class ParserTests(unittest.TestCase):
    def assert_invalid(self, text, code):
        with self.assertRaises(DSLError) as ctx:
            parse(text)
        self.assertEqual(ctx.exception.code, code)

    def test_minimal_parses(self):
        self.assertEqual(parse(MINIMAL)['concepts']['curiosity']['definition'], 'Robocza definicja')

    def test_version(self):
        self.assert_invalid(MINIMAL.replace('affect 0.1', 'affect 0.2'), 'E_VERSION')

    def test_requires_model(self):
        self.assert_invalid(MINIMAL.replace('model illustrative\n', ''), 'E_MODEL')

    def test_refuses_calibrated_claim(self):
        self.assert_invalid(MINIMAL.replace('model illustrative', 'model validated'), 'E_MODEL')

    def test_unknown_concept(self):
        self.assert_invalid(MINIMAL.replace('explain curiosity', 'explain confidence'), 'E_REFERENCE')

    def test_unknown_event(self):
        self.assert_invalid(MINIMAL.replace('apply event_a', 'apply missing'), 'E_REFERENCE')

    def test_unknown_axis(self):
        self.assert_invalid(MINIMAL.replace('novelty=0.8', 'certainty=0.8'), 'E_REFERENCE')

    def test_duplicate_concept(self):
        self.assert_invalid(MINIMAL.replace('state curiosity', 'concept curiosity "Duplicate"\nstate curiosity'), 'E_DUPLICATE')

    def test_duplicate_event_axis(self):
        self.assert_invalid(MINIMAL.replace('novelty=0.8', 'novelty=0.8 novelty=0.1'), 'E_DUPLICATE')

    def test_duplicate_driver(self):
        self.assert_invalid(MINIMAL.replace('event event_a', 'driver curiosity novelty 0.1\nevent event_a'), 'E_DUPLICATE')

    def test_missing_state(self):
        self.assert_invalid(MINIMAL.replace('state curiosity 0.2 retention 0.5\n', ''), 'E_STATE')

    def test_invalid_ranges_and_nonfinite(self):
        for value in ['-0.01', '1.01', 'nan', 'inf', '-inf', '1e999']:
            with self.subTest(value=value):
                self.assert_invalid(MINIMAL.replace('retention 0.5', 'retention '+value), 'E_RANGE')

    def test_declaration_after_runtime(self):
        self.assert_invalid(MINIMAL+'axis other\n', 'E_ORDER')

    def test_earlier_checkpoint_required(self):
        self.assert_invalid(MINIMAL.replace('expect first', 'expect future'), 'E_REFERENCE')

    def test_duplicate_checkpoint(self):
        self.assert_invalid(MINIMAL+'checkpoint first\n', 'E_DUPLICATE')

    def test_resource_limit(self):
        self.assert_invalid(MINIMAL.replace('ticks 1', 'ticks 1000')+'wait ticks 1\n', 'E_LIMIT')

    def test_negative_ticks(self):
        self.assert_invalid(MINIMAL.replace('ticks 1', 'ticks -1'), 'E_TICKS')

    def test_invalid_operator(self):
        self.assert_invalid(MINIMAL.replace('>= 0.5', '!= 0.5'), 'E_OPERATOR')

    def test_no_code_execution(self):
        self.assert_invalid(MINIMAL+"__import__('os').system('echo bad')\n", 'E_STATEMENT')

    def test_quote_error(self):
        self.assert_invalid(MINIMAL.replace('"Robocza definicja"', '"unfinished'), 'E_LEXER')

    def test_comments_and_utf8(self):
        text = MINIMAL.replace('"Robocza definicja"', '"Zażółć # to część opisu" # komentarz')
        self.assertIn('#', parse(text)['concepts']['curiosity']['definition'])

    def test_no_self_coupling(self):
        self.assert_invalid(MINIMAL.replace('event event_a', 'couple curiosity curiosity 0.1\nevent event_a'), 'E_COUPLING')


class DynamicsTests(unittest.TestCase):
    def test_relief_requires_prior_tension_drop(self):
        p = parse((ROOT/'examples/puzzle.emo').read_text(encoding='utf-8'))
        p['states']['tension']['initial'] = 0
        result = simulate(p)
        self.assertLessEqual(result['final']['relief'], p['states']['relief']['initial'])
        self.assertTrue(all(not t['requirements']['relief']['passed'] for t in result['trace'] if 'requirements' in t))

    def test_relief_contract_with_prior_tension(self):
        result = simulate(parse((ROOT/'examples/puzzle.emo').read_text(encoding='utf-8')))
        step = next(t for t in result['trace'] if t.get('event') == 'explanation')
        self.assertTrue(step['requirements']['relief']['passed'])
        self.assertTrue(result['checks_passed'])

    def test_guard_dependency_rejected(self):
        source = (ROOT/'examples/puzzle.emo').read_text(encoding='utf-8')
        source = source.replace('requires relief drop tension 0.05', 'requires relief drop tension 0.05\nrequires tension drop curiosity 0.01')
        with self.assertRaises(DSLError) as ctx:
            parse(source)
        self.assertEqual(ctx.exception.code, 'E_REQUIREMENT')

    def test_zero_drop_not_a_valid_requirement(self):
        source = (ROOT/'examples/puzzle.emo').read_text(encoding='utf-8')
        with self.assertRaises(DSLError):
            parse(source.replace('requires relief drop tension 0.05', 'requires relief drop tension 0'))

    def test_exact_one_tick(self):
        # independently calculated: 0.5*0.2 + 0.5*0.8 = 0.5
        self.assertAlmostEqual(simulate(parse(MINIMAL))['final']['curiosity'], .5)

    def test_explaining_has_no_affective_effect(self):
        a = simulate(parse(MINIMAL))
        b = simulate(parse(MINIMAL.replace('explain curiosity\n', '')))
        self.assertEqual(a['final'], b['final'])
        self.assertEqual(a['ticks'], b['ticks'])

    def test_decay_without_input_or_coupling(self):
        text = MINIMAL[:MINIMAL.index('explain')]+'wait ticks 3\ncheckpoint end\n'
        self.assertAlmostEqual(simulate(parse(text))['final']['curiosity'], .025)

    def test_saturation_is_logged(self):
        text = MINIMAL.replace('retention 0.5', 'retention 1').replace('ticks 1', 'ticks 10')
        result = simulate(parse(text))
        self.assertEqual(result['final']['curiosity'], 1)
        self.assertTrue(any(t.get('clamped') for t in result['trace']))

    def test_synchronous_coupling_order_independent(self):
        common = '''affect 0.1
model illustrative
concept a "A"
concept b "B"
'''
        tail = '''couple a b 0.5
couple b a 0.5
wait ticks 1
checkpoint end
'''
        a = common+'state a 0.8 retention 0\nstate b 0.2 retention 0\n'+tail
        b = common+'state b 0.2 retention 0\nstate a 0.8 retention 0\n'+tail
        self.assertEqual(simulate(parse(a))['final'], simulate(parse(b))['final'])
        self.assertEqual(simulate(parse(a))['final'], {'a': .1, 'b': .4})

    def test_sequence_noncommutative(self):
        p = parse(MINIMAL)
        p['events']['b'] = {'appraisal': {'novelty': .2}}
        p['commands'] = [{'op': 'apply', 'event': 'event_a', 'ticks': 1},
                         {'op': 'apply', 'event': 'b', 'ticks': 1}]
        a = simulate(p)['final']['curiosity']
        p['commands'].reverse()
        b = simulate(p)['final']['curiosity']
        self.assertAlmostEqual(a, .35)
        self.assertAlmostEqual(b, .5)

    def test_gate_stops_no_escalation(self):
        result = simulate(parse((ROOT/'examples/stopped.emo').read_text()))
        self.assertEqual(result['status'], 'halted_by_gate')
        self.assertEqual(result['ticks'], 1)
        self.assertNotIn('unreachable', result['checkpoints'])
        self.assertEqual(result['checks'][-1]['status'], 'not_reached')

    def test_expect_does_not_control_state(self):
        a = simulate(parse(MINIMAL))
        b = simulate(parse(MINIMAL.replace('>= 0.5', '>= 0.99')))
        self.assertEqual(a['final'], b['final'])
        self.assertFalse(b['checks_passed'])
        self.assertEqual(b['status'], 'completed')

    def test_seed_reproducibility(self):
        p = parse(MINIMAL.replace('model illustrative', 'model illustrative\nseed 11\nnoise 0.02'))
        a, b = simulate(p), simulate(p)
        self.assertEqual(a, b)
        p['seed'] = 12
        self.assertNotEqual(a['final'], simulate(p)['final'])

    def test_boundedness_random_parameters(self):
        rng = random.Random(2026)
        for _ in range(100):
            p = parse(MINIMAL)
            p['noise'] = rng.random()
            p['states']['curiosity']['retention'] = rng.random()
            p['drivers'][0]['weight'] = rng.uniform(-1, 1)
            p['commands'] = [{'op': 'apply', 'event': 'event_a', 'ticks': 20}]
            self.assertTrue(all(0 <= t['state']['curiosity'] <= 1 for t in simulate(p)['trace']))

    def test_checks_not_empirical_proof(self):
        result = simulate(parse(MINIMAL))
        self.assertTrue(result['checks_passed'])
        self.assertEqual(result['empirical_validity'], 'not_assessed')
        self.assertEqual(result['evidence_status'], 'uncalibrated_simulation')


class ObservationAndCLITests(unittest.TestCase):
    def setUp(self):
        self.run = simulate(parse(MINIMAL))
        self.data = {'kind': 'synthetic_fixture', 'source': 'Unit-test data',
                     'records': [{'checkpoint': 'first', 'concept': 'curiosity', 'value': .4}]}

    def test_descriptive_error(self):
        result = compare_observations(self.run, self.data)
        self.assertAlmostEqual(result['mae'], .1)
        self.assertEqual(result['empirical_validity'], 'not_assessed')

    def test_no_provenance_promotion(self):
        self.data['kind'] = 'empirical_declared'
        result = compare_observations(self.run, self.data)
        self.assertFalse(result['provenance_verified'])
        self.assertEqual(result['empirical_validity'], 'not_assessed')

    def test_unknown_observation(self):
        self.data['records'][0]['checkpoint'] = 'missing'
        with self.assertRaises(DSLError):
            compare_observations(self.run, self.data)

    def test_invalid_observation_shapes(self):
        for value in [True, '0.3', None, [], float('nan')]:
            with self.subTest(value=value):
                self.data['records'][0]['value'] = value
                with self.assertRaises(DSLError):
                    compare_observations(self.run, self.data)

    def test_duplicate_observation_rejected(self):
        self.data['records'] *= 2
        with self.assertRaises(DSLError):
            compare_observations(self.run, self.data)

    def test_invalid_kind_type(self):
        self.data['kind'] = []
        with self.assertRaises(DSLError):
            compare_observations(self.run, self.data)

    def test_cli_success_and_goal_failure(self):
        for filename, expected in [('puzzle.emo', 0), ('stopped.emo', 2)]:
            result = subprocess.run([sys.executable, str(ROOT/'src/edialog/core.py'), 'run',
                                     str(ROOT/'examples'/filename)], capture_output=True, text=True)
            self.assertEqual(result.returncode, expected, result.stderr)
            self.assertEqual(json.loads(result.stdout)['empirical_validity'], 'not_assessed')

    def test_cli_static_error(self):
        result = subprocess.run([sys.executable, str(ROOT/'src/edialog/core.py'), 'validate', '/no/such/file.emo'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertTrue(result.stderr)


if __name__ == '__main__':
    unittest.main()
