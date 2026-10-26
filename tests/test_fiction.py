import base64
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

from edialog import (EMOTION_CODES, EmotionLexicon, TextEmotionAnalyzer, Dialogue,
    Participant, FictionEngine, FictionRequest, CallableFictionBackend,
    CallableVisionBackend, analyze_image, parse_fiction_request, evaluate_annotations,
    OllamaJSON, ValidationError, NeedsClarification, BackendError)

try:
    from PIL import Image
except ImportError:
    Image = None


def scene():
    d = Dialogue((Participant('anna', 'Anna'), Participant('jan', 'Jan'), Participant('piotr', 'Piotr')))
    d.add_turn('anna', 'Ktoś nas śledzi.', recipients=('jan', 'piotr'))
    d.add_turn('piotr', 'Słyszę kroki.', recipients=('jan', 'anna'))
    return d


class LexicalTests(unittest.TestCase):
    def setUp(self):
        self.a = TextEmotionAnalyzer()

    def test_codes_are_exact_identifiers(self):
        self.assertEqual(EMOTION_CODES, dict(scared=0, sad=2, angry=4, nothing=5,
                                           happy=6, **{'h-cited': 7}, excited=8))

    def test_unknown_is_not_neutral(self):
        result = self.a.analyze('Stół ma cztery nogi.')
        self.assertEqual(result.status, 'unknown')
        self.assertEqual(result.scores['nothing'], 0)

    def test_explicit_neutral(self):
        self.assertGreater(self.a.analyze('Zwyczajnie. Bez zmian.').scores['nothing'], .5)

    def test_all_dimensions(self):
        phrases = ['Boję się.', 'Smutny.', 'Gniew.', 'Zwyczajnie.', 'Radość.', 'Thrilled!', 'Ekscytacja.']
        for emotion, phrase in zip(EMOTION_CODES, phrases):
            with self.subTest(emotion=emotion):
                self.assertGreater(self.a.analyze(phrase).scores[emotion], .3)

    def test_negation_attenuates_not_inverts(self):
        yes = self.a.analyze('Boję się.')
        no = self.a.analyze('Nie boję się.')
        self.assertLess(no.scores['scared'], yes.scores['scared'])
        self.assertEqual(no.scores['happy'], 0)
        self.assertIn('negation:0.15', no.evidence[0]['modifiers'])

    def test_negation_does_not_cross_sentence(self):
        self.assertEqual(self.a.analyze('Nie. Boję się.').scores,
                         self.a.analyze('Boję się.').scores)

    def test_intensification_and_dampening(self):
        score = lambda t: self.a.analyze(t).scores['sad']
        self.assertLess(score('Trochę smutny.'), score('Smutny.'))
        self.assertLess(score('Smutny.'), score('Bardzo smutny!'))

    def test_exclamation_not_future_sentence(self):
        self.assertEqual(self.a.analyze('Smutny. Zwyczajnie!').scores['sad'],
                         self.a.analyze('Smutny.').scores['sad'])

    def test_exclamation_boundary(self):
        self.assertEqual(self.a.analyze('Smutny! Zwyczajnie!!!').scores['sad'],
                         self.a.analyze('Smutny!').scores['sad'])

    def test_caps_amplify_in_mixed_text(self):
        self.assertGreater(self.a.analyze('Jestem SMUTNY.').scores['sad'],
                           self.a.analyze('Jestem smutny.').scores['sad'])

    def test_contrast_order(self):
        a = self.a.analyze('Smutny, ale szczęśliwy.')
        b = self.a.analyze('Szczęśliwy, ale smutny.')
        self.assertGreater(b.scores['sad'], a.scores['sad'])
        self.assertGreater(a.scores['happy'], b.scores['happy'])

    def test_mixed_emotions_not_categorical_mean(self):
        r = self.a.analyze('Boję się. Gniew. Radość. Ekscytacja.')
        self.assertGreater(sum(r.scores.values()), 1)
        self.assertEqual(r.scores['nothing'], 0)

    def test_longest_match(self):
        r = self.a.analyze('Nigdy nie wróci.')
        self.assertEqual(len(r.evidence), 1)
        self.assertEqual(r.evidence[0]['surface'], 'Nigdy nie wróci')

    def test_repetition_diminishes(self):
        r = self.a.analyze('strach strach strach')
        v = [e['contribution']['scared'] for e in r.evidence]
        self.assertGreater(v[0], v[1])
        self.assertGreater(v[1], v[2])

    def test_unicode_spans(self):
        s = '— Czuję żal i łzy.'
        for e in self.a.analyze(s).evidence:
            a, b = e['span']
            self.assertEqual(s[a:b], e['surface'])

    def test_same_word_changes_with_history(self):
        neutral = self.a.analyze('Słyszę kroki.')
        danger = self.a.analyze('Słyszę kroki.', history=['Ktoś nas śledzi.'])
        reunion = self.a.analyze('Słyszę kroki.', history=['Cieszę się, że wróciłeś.'])
        self.assertEqual(neutral.status, 'unknown')
        self.assertGreater(danger.scores['scared'], .3)
        self.assertGreater(reunion.scores['happy'], .3)
        self.assertEqual(reunion.scores['scared'], 0)
        self.assertEqual(danger.evidence[0]['origin'], 'context')

    def test_recent_context_decays(self):
        recent = self.a.analyze('Kroki.', history=['Boję się.'])
        older = self.a.analyze('Kroki.', history=['Boję się.', 'Stół.'])
        expired = self.a.analyze('Kroki.', history=['Boję się.']+['Stół.']*4)
        self.assertGreater(recent.scores['scared'], older.scores['scared'])
        self.assertEqual(expired.scores['scared'], 0)

    def test_negated_prior_does_not_trigger_threat(self):
        r = self.a.analyze('Kroki.', history=['Nie boję się.'])
        self.assertEqual(r.scores['scared'], 0)

    def test_weights_edit_is_immutable(self):
        lex = EmotionLexicon()
        before = lex.to_dict()
        edited = lex.with_weights('kroki', {'scared': .9})
        self.assertEqual(lex.to_dict(), before)
        self.assertNotEqual(lex.model_id, edited.model_id)
        self.assertGreater(TextEmotionAnalyzer(edited).analyze('Kroki.').scores['scared'], 0)

    def test_custom_lexicon_roundtrip(self):
        lex = EmotionLexicon().with_weights('ruda wstążka', {'sad': .8})
        clone = EmotionLexicon.from_json(json.dumps(lex.to_dict()))
        self.assertEqual(clone.model_id, lex.model_id)

    def test_bad_weights(self):
        for weights in ({'scared': float('nan')}, {'sad': True}, {'surprised': .5}, {'happy': 5}):
            with self.subTest(weights=weights), self.assertRaises(ValidationError):
                EmotionLexicon().with_weights('x', weights)

    def test_unknown_history_type(self):
        with self.assertRaises(ValidationError):
            self.a.analyze('Happy', history='Sad')

    def test_model_config_changes_identity(self):
        self.assertNotEqual(self.a.model_id, TextEmotionAnalyzer(context_decay=.1).model_id)


class FictionTests(unittest.TestCase):
    def setUp(self):
        self.d = scene()
        self.engine = FictionEngine()
        self.kw = dict(actor='jan', recipients=('anna', 'piotr'))

    def test_nl_decimal_and_multiple_goals(self):
        r = parse_fiction_request('Cel: strach=0,85; cel: smutek=0.2; strategia: suspense.')
        self.assertEqual(r.target, {'scared': .85, 'sad': .2})

    def test_nl_english(self):
        self.assertEqual(parse_fiction_request('Target: h-cited=0.8.').target, {'h-cited': .8})

    def test_nl_unmatched_clause_fails(self):
        with self.assertRaises(NeedsClarification):
            parse_fiction_request('Cel: strach=0,8; oraz coś innego')

    def test_nl_duplicate_target_fails(self):
        with self.assertRaises(ValidationError):
            parse_fiction_request('Cel: strach=0,8; cel: strach=0,3')

    def test_strategy_only(self):
        r = FictionRequest(strategies=('loss',))
        self.assertEqual(r.target, {'sad': .8})

    def test_target_only(self):
        self.assertEqual(FictionRequest({'angry': .9}).strategies, ('confrontation',))

    def test_low_fear_target_selects_release(self):
        self.assertEqual(FictionRequest({'scared': .1}).strategies, ('release',))

    def test_invalid_targets(self):
        for value in ({'happy': 6}, {'scared': float('nan')}, [], False):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                FictionRequest(value, ('quiet',))

    def test_fiction_all_seven_targets(self):
        for label in EMOTION_CODES:
            with self.subTest(label=label):
                p = self.engine.generate(self.d, **self.kw, request=FictionRequest({label: .8}))
                self.assertTrue(p.text)
                self.assertEqual(p.status, 'fiction_draft')

    def test_text_controls_scoring(self):
        p = self.engine.generate(self.d, **self.kw, request=FictionRequest({'happy': .75}),
            candidates=['Boję się. Ktoś nas śledzi.', 'Cieszę się! Wróciłeś. Radość.'])
        self.assertTrue(p.text.startswith('Cieszę'))
        self.assertGreater(p.candidates[0]['reader_proxy']['happy'], p.candidates[1]['reader_proxy']['happy'])

    def test_model_target_may_remain_unmet(self):
        p = self.engine.generate(self.d, **self.kw, request=FictionRequest({'happy': 1}, tolerance=.001),
                                 candidates=['Stół.'])
        self.assertFalse(p.candidates[0]['target_met_in_model'])

    def test_unknown_is_not_success_even_zero_target(self):
        d = Dialogue((Participant('a', 'A'), Participant('b', 'B')))
        p = self.engine.generate(d, actor='a', recipients=['b'], request=FictionRequest({'scared': 0}),
                                 candidates=['Stół.'])
        self.assertEqual(p.candidates[0]['status'], 'unknown')
        self.assertFalse(p.candidates[0]['target_met_in_model'])

    def test_no_mixing_characters(self):
        r = self.engine.analyze_dialogue(self.d, **self.kw)
        self.assertEqual(set(r['character_expression_proxies']), {'anna', 'piotr'})
        self.assertNotIn('jan', r['character_expression_proxies'])

    def test_cumulative_arc(self):
        r = self.engine.analyze_dialogue(self.d, **self.kw)
        self.assertGreater(r['reader_proxy']['scared'], r['timeline'][-1]['text_affect']['scores']['scared'])

    def test_replay_is_identical(self):
        p = self.engine.generate(self.d, **self.kw, instruction='Cel: strach=0.8')
        self.assertEqual(self.engine.replay(p.dsl, self.d).to_dict(), p.to_dict())

    def test_replay_uses_snapshot_weights(self):
        custom = FictionEngine(TextEmotionAnalyzer(EmotionLexicon().with_weights('stół', {'sad': .9})))
        p = custom.generate(self.d, **self.kw, request=FictionRequest({'sad': .7}), candidates=['Stół.'])
        self.assertEqual(self.engine.replay(p.dsl, self.d).candidates, p.candidates)

    def test_append_only_synthetic_copy(self):
        p = self.engine.generate(self.d, **self.kw, instruction='Cel: strach=0.8')
        d2 = self.engine.continue_scene(self.d, p)
        self.assertEqual(len(self.d.turns), 2)
        self.assertEqual(len(d2.turns), 3)
        self.assertEqual(d2.turns[-1].kind, 'synthetic')
        self.assertEqual(d2.readings, {})

    def test_stale_plan_fails(self):
        p = self.engine.generate(self.d, **self.kw, instruction='Cel: strach=0.8')
        self.d.add_turn('anna', 'Już po wszystkim.')
        with self.assertRaises(ValidationError):
            self.engine.continue_scene(self.d, p)

    def test_wrong_mode_fails(self):
        p = self.engine.generate(self.d, **self.kw, instruction='Cel: strach=0.8')
        obj = json.loads(p.dsl)
        obj['mode'] = 'real_person_control'
        with self.assertRaises(ValidationError):
            self.engine.replay(json.dumps(obj), self.d)

    def test_history_not_mutated(self):
        before = self.d.to_dict()
        self.engine.generate(self.d, **self.kw, instruction='Cel: strach=0.8')
        self.assertEqual(before, self.d.to_dict())

    def test_recipient_scope(self):
        with self.assertRaises(ValidationError):
            self.engine.generate(self.d, actor='jan', recipients=['jan'], request=FictionRequest({'sad': .8}))

    def test_private_context_never_sent_to_group(self):
        private = self.d.add_turn('anna', 'TAJNE HASŁO', recipients=('jan',))
        calls = []
        def callback(payload):
            calls.append(payload)
            return {'candidates': [{'text': 'Boję się.', 'evidence_turn_ids': ['t1']}]}
        p = FictionEngine(backend=CallableFictionBackend(callback)).generate(
            self.d, **self.kw, request=FictionRequest({'scared': .8}))
        self.assertNotIn('TAJNE HASŁO', json.dumps(calls))
        self.assertNotIn(private.id, p.baseline['context_turn_ids'])

    def test_unknown_evidence_rejected(self):
        backend = CallableFictionBackend(lambda p: {'candidates': [{'text': 'Boję się.', 'evidence_turn_ids': ['invented']}]})
        with self.assertRaises(ValidationError):
            FictionEngine(backend=backend).generate(self.d, **self.kw, request=FictionRequest({'scared': .8}))

    def test_callback_nl_and_generation(self):
        def callback(p):
            if p['task'] == 'parse_fiction_request':
                return {'target': {'sad': .8}, 'strategies': ['loss']}
            return {'candidates': [{'text': 'Nie wróci. Tęsknię.', 'evidence_turn_ids': ['t1']}]}
        p = FictionEngine(backend=CallableFictionBackend(callback)).generate(self.d, **self.kw, instruction='Daj mi przejmujące pożegnanie')
        self.assertEqual(p.target, {'sad': .8})

    def test_repeated_candidates_rejected(self):
        with self.assertRaises(ValidationError):
            self.engine.generate(self.d, **self.kw, request=FictionRequest({'sad': .8}), candidates=['Łzy.', 'Łzy.'])

    def test_annotation_metric_does_not_impute_missing(self):
        r = evaluate_annotations([{'prediction': {'sad': .8, 'scared': .5}, 'rating': {'sad': .6}}])
        self.assertAlmostEqual(r['mae'], .2)
        self.assertEqual(r['rated_dimensions'], 1)
        self.assertNotIn('scared', r['per_emotion'])

    def test_bad_annotations(self):
        with self.assertRaises(ValidationError):
            evaluate_annotations([{'prediction': {'sad': .4}, 'rating': {'scared': .5}}])

    def test_cli_generate_and_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)/'scene.json'
            plan, output = Path(tmp)/'plan.json', Path(tmp)/'result.json'
            d.write_text(json.dumps(self.d.to_dict()), encoding='utf-8')
            a = subprocess.run([sys.executable, '-m', 'edialog.fiction_cli', 'generate', str(d),
                '--actor', 'jan', '--to', 'anna', 'piotr', '--instruction', 'Cel: strach=0,8',
                '--dsl-out', str(plan), '--out', str(output)], capture_output=True, text=True)
            self.assertEqual(a.returncode, 0, a.stderr)
            b = subprocess.run([sys.executable, '-m', 'edialog.fiction_cli', 'replay', str(d),
                                '--plan', str(plan)], capture_output=True, text=True)
            self.assertEqual(b.returncode, 0, b.stderr)
            self.assertEqual(json.loads(b.stdout), json.loads(output.read_text()))


@unittest.skipUnless(Image is not None, 'Install images extra to run pixel tests')
class ImageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)/'scene.png'
        Image.new('RGB', (32, 20), (10, 10, 20)).save(self.path)

    def test_pixel_features(self):
        r = analyze_image(self.path)
        self.assertLess(r.features['brightness'], .1)
        self.assertEqual(r.features['dimensions'], [32, 20])
        self.assertEqual(r.origin, 'pixel_atmosphere_heuristic_v1')
        self.assertGreater(r.scores['scared'], 0)

    def test_features_only(self):
        r = analyze_image(self.path, pixel_heuristics=False)
        self.assertEqual(sum(r.scores.values()), 0)

    def test_transparency_composited_on_white(self):
        Image.new('RGBA', (2, 2), (0, 0, 0, 0)).save(self.path)
        self.assertEqual(analyze_image(self.path).features['brightness'], 1)

    def test_callback_receives_pixels_and_context(self):
        calls = []
        def callback(p):
            calls.append(p)
            return {'caption': 'Dark doorway.', 'cues': [{'label': 'threat', 'strength': .8}]}
        r = analyze_image(self.path, backend=CallableVisionBackend(callback), context=['Who is there?'])
        self.assertEqual(r.caption, 'Dark doorway.')
        self.assertAlmostEqual(r.scores['scared'], .64)
        self.assertEqual(calls[0]['context'], ['Who is there?'])
        self.assertTrue(base64.b64decode(calls[0]['image']['base64']).startswith(b'\x89PNG'))
        self.assertNotIn(str(self.path), json.dumps(calls))

    def test_bad_callback_cues(self):
        for cue in ({'label': 'face_fear', 'strength': .8}, {'label': 'threat', 'strength': float('nan')}):
            with self.subTest(cue=cue), self.assertRaises(BackendError):
                analyze_image(self.path, backend=CallableVisionBackend(lambda p: {'caption': 'x', 'cues': [cue]}))

    def test_corrupt_input(self):
        self.path.write_bytes(b'not a png')
        with self.assertRaises(ValidationError):
            analyze_image(self.path)

    def test_pixel_limit(self):
        Image.new('L', (4001, 4000)).save(self.path)
        with self.assertRaises(ValidationError):
            analyze_image(self.path)

    def test_image_influences_ranking_state_and_replay(self):
        d, e = scene(), FictionEngine()
        kwargs = dict(actor='jan', recipients=['anna', 'piotr'], request=FictionRequest({'scared': .8}), candidates=['Stół.'])
        plain = e.generate(d, **kwargs)
        visual = e.generate(d, **kwargs, image=analyze_image(self.path))
        self.assertGreater(visual.candidates[0]['reader_proxy']['scared'], plain.candidates[0]['reader_proxy']['scared'])
        self.assertEqual(e.replay(visual.dsl, d).to_dict(), visual.to_dict())


class TransportTests(unittest.TestCase):
    def test_ollama_request_structure(self):
        body = json.dumps({'message': {'content': '{"caption":"ok","cues":[]}'}}).encode()
        seen = []
        def opened(req, timeout):
            seen.append((req, timeout))
            return io.BytesIO(body)
        with patch('urllib.request.urlopen', side_effect=opened):
            result = OllamaJSON('test-model')({'response_schema': {'type': 'object'},
                'task': 'describe_fiction_scene', 'image': {'mime_type': 'image/png', 'base64': 'eA=='}})
        self.assertEqual(result['caption'], 'ok')
        payload = json.loads(seen[0][0].data)
        self.assertFalse(payload['stream'])
        self.assertEqual(payload['messages'][-1]['images'], ['eA=='])
        self.assertNotIn('eA==', payload['messages'][-1]['content'])
        self.assertEqual(seen[0][0].full_url, 'http://localhost:11434/api/chat')

    def test_ollama_failure_wrapped(self):
        with patch('urllib.request.urlopen', side_effect=urllib.error.URLError('offline')):
            with self.assertRaises(BackendError):
                OllamaJSON('test')({'response_schema': {}})

    def test_ollama_invalid_json_wrapped(self):
        with patch('urllib.request.urlopen', return_value=io.BytesIO(b'broken')):
            with self.assertRaises(BackendError):
                OllamaJSON('test')({'response_schema': {}})

    def test_invalid_service_address(self):
        with self.assertRaises(ValidationError):
            OllamaJSON('test', base_url='file:///tmp/model')


if __name__ == '__main__':
    unittest.main()
