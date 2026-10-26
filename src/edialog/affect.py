"""Auditable word associations for fictional prose; scores are not probabilities."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from importlib.resources import files
import hashlib
import json
import math
import re

from .errors import ValidationError
from .models import keys, text as check_text, unit
from .nl import fold

EMOTION_CODES = {'scared': 0, 'sad': 2, 'angry': 4, 'nothing': 5,
                 'happy': 6, 'h-cited': 7, 'excited': 8}
TOKEN = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)?|[.!?,;:]", re.UNICODE)
BOUNDARIES = {'.', '!', '?', ',', ';', ':'}
CONTRAST = {'ale', 'lecz', 'jednak', 'but', 'however'}
NEGATIONS = {'nie', 'bez', 'nigdy', 'not', 'never', 'no', "isn't", "wasn't", "don't", "didn't"}
BOOSTERS = {'bardzo': 1.5, 'strasznie': 1.6, 'ogromnie': 1.6,
            'niesamowicie': 1.7, 'very': 1.5, 'extremely': 1.7,
            'troche': .6, 'nieco': .6, 'slightly': .6, 'barely': .4}


def tokens(value):
    return [fold(m.group()) for m in TOKEN.finditer(value)]


def vector(value, *, partial=False):
    if not isinstance(value, dict) or set(value) - set(EMOTION_CODES):
        raise ValidationError('Emotion weights must use the seven named labels')
    result = {k: unit(v, k) for k, v in value.items()}
    return result if partial else {k: result.get(k, 0.0) for k in EMOTION_CODES}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True)
class TextAffect:
    scores: dict
    evidence: tuple
    coverage: float
    status: str
    model_id: str
    warnings: tuple = ('Scores describe lexical tone, not a person or a measured reader response.',)

    def to_dict(self):
        return asdict(self)


class EmotionLexicon:
    """Explicit editable configuration. Never learns silently from generated prose."""
    def __init__(self, config=None):
        if config is None:
            config = json.loads(files('edialog').joinpath('data/lexicon.json').read_text(encoding='utf-8'))
        keys(config, {'version', 'provenance', 'entries', 'context_rules'})
        check_text(config['version'], 'lexicon version', 80)
        check_text(config['provenance'], 'provenance', 500)
        if not isinstance(config['entries'], dict) or not 1 <= len(config['entries']) <= 10000:
            raise ValidationError('Lexicon requires 1..10000 entries')
        if not isinstance(config['context_rules'], list) or len(config['context_rules']) > 200:
            raise ValidationError('At most 200 context rules')
        entries = {}
        for phrase, weights in config['entries'].items():
            check_text(phrase, 'phrase', 100)
            normalized = ' '.join(tokens(phrase))
            if not normalized or any(p in BOUNDARIES for p in normalized.split()) or len(normalized.split()) > 8:
                raise ValidationError('Lexicon phrases contain 1..8 words and no punctuation')
            if normalized in entries:
                raise ValidationError('Duplicate normalized phrase')
            if not weights:
                raise ValidationError('Empty word weights')
            entries[normalized] = vector(weights, partial=True)
        rules = []
        for rule in config['context_rules']:
            keys(rule, {'phrase', 'requires', 'threshold', 'weights'})
            check_text(rule['phrase'], 'context phrase', 100)
            phrase = ' '.join(tokens(rule['phrase']))
            if not phrase or any(t in BOUNDARIES for t in phrase.split()) or len(phrase.split()) > 8:
                raise ValidationError('Invalid context phrase')
            if not isinstance(rule['requires'], str) or rule['requires'] not in EMOTION_CODES or not rule['weights']:
                raise ValidationError('Invalid context condition')
            rules.append({'phrase': phrase, 'requires': rule['requires'],
                          'threshold': unit(rule['threshold']),
                          'weights': vector(rule['weights'], partial=True)})
        self._config = {'version': config['version'], 'provenance': config['provenance'],
                        'entries': entries, 'context_rules': rules}
        self.model_id = digest(self._config)
        self._entries = {tuple(k.split()): v for k, v in entries.items()}
        self._max_words = max(map(len, self._entries))

    def to_dict(self):
        return json.loads(json.dumps(self._config))

    @classmethod
    def from_json(cls, source):
        try:
            return cls(json.loads(source))
        except (ValueError, TypeError) as exc:
            raise ValidationError(f'Invalid lexicon JSON: {exc}') from exc

    def with_weights(self, phrase, weights):
        config = self.to_dict()
        config['entries'][' '.join(tokens(phrase))] = weights
        config['version'] += '+edit'
        return EmotionLexicon(config)


class TextEmotionAnalyzer:
    def __init__(self, lexicon=None, *, context_window=4, context_decay=.75):
        self.lexicon = lexicon if lexicon is not None else EmotionLexicon()
        if not isinstance(self.lexicon, EmotionLexicon):
            raise ValidationError('Expected EmotionLexicon')
        if type(context_window) is not int or not 1 <= context_window <= 20:
            raise ValidationError('context_window must be 1..20')
        self.context_window = context_window
        self.context_decay = unit(context_decay, 'context_decay')

    @property
    def config(self):
        return {'lexicon': self.lexicon.to_dict(), 'context_window': self.context_window,
                'context_decay': self.context_decay}

    @property
    def model_id(self):
        return digest(self.config)

    def analyze(self, text, *, history=()):
        check_text(text, 'text', 5000)
        if not isinstance(history, (list, tuple)) or len(history) > 200:
            raise ValidationError('history must be a sequence of at most 200 texts')
        for previous in history:
            check_text(previous, 'history text', 5000)
        prior = vector({})
        for age, previous in enumerate(reversed(history[-self.context_window:])):
            scores = self._analyze(previous, vector({})).scores
            for label, score in scores.items():
                prior[label] = max(prior[label], score * self.context_decay ** age)
        return self._analyze(text, prior)

    def _analyze(self, text, prior):
        matches = list(TOKEN.finditer(text))
        ts = tokens(text)
        total = vector({})
        evidence, covered = [], set()
        contrast_at = [i for i, word in enumerate(ts) if word in CONTRAST]
        word_count = sum(t not in BOUNDARIES for t in ts)
        mixed_case = any(any(c.islower() for c in m.group()) for m in matches)

        def add(start, end, weights, origin, condition=None):
            left = start
            while left > 0 and start-left < 3 and ts[left-1] not in BOUNDARIES | CONTRAST:
                left -= 1
            preceding = ts[left:start]
            multiplier, modifiers = 1.0, []
            if any(t in NEGATIONS for t in preceding):
                multiplier *= .15  # attenuate; do not invent an opposite emotion
                modifiers.append('negation:0.15')
            for t in preceding:
                if t in BOOSTERS:
                    multiplier *= BOOSTERS[t]
                    modifiers.append(f'intensifier:{t}:{BOOSTERS[t]}')
            if contrast_at:
                factor = 1.25 if start > contrast_at[-1] else .75
                multiplier *= factor
                modifiers.append(f'contrast:{factor}')
            surface = text[matches[start].start():matches[end-1].end()]
            if surface.isupper() and mixed_case:
                multiplier *= 1.2
                modifiers.append('capitals:1.2')
            # Only sentence-local exclamation marks affect this match.
            right = end
            while right < len(ts) and ts[right] not in {'.', '?', '!', ';'}:
                right += 1
            n = 0
            while right+n < len(ts) and ts[right+n] == '!' and n < 3:
                n += 1
            if n:
                multiplier *= 1 + .1*n
                modifiers.append(f'exclamations:{n}')
            multiplier = min(multiplier, 3.0)
            contribution = {k: round(v*multiplier, 8) for k, v in weights.items()}
            for k, value in contribution.items():
                total[k] += value
            covered.update(range(start, end))
            evidence.append({'surface': surface, 'span': [matches[start].start(), matches[end-1].end()],
                             'origin': origin, 'base_weights': dict(weights),
                             'multiplier': multiplier, 'modifiers': modifiers,
                             'contribution': contribution, 'context_condition': condition})

        # Longest match first prevents double-counting phrases and their words.
        i = 0
        occurrences = {}
        while i < len(ts):
            found = False
            for size in range(min(self.lexicon._max_words, len(ts)-i), 0, -1):
                phrase = tuple(ts[i:i+size])
                weights = self.lexicon._entries.get(phrase)
                if weights:
                    # Repeating one keyword has diminishing returns within a turn.
                    count = occurrences.get(phrase, 0)
                    occurrences[phrase] = count + 1
                    add(i, i+size, {k: v/(count+1) for k, v in weights.items()}, 'lexicon')
                    i += size
                    found = True
                    break
            if not found:
                i += 1
        for rule in self.lexicon._config['context_rules']:
            score = prior[rule['requires']]
            if score < rule['threshold']:
                continue
            phrase = tuple(rule['phrase'].split())
            for i in range(len(ts)-len(phrase)+1):
                if tuple(ts[i:i+len(phrase)]) == phrase:
                    add(i, i+len(phrase), {k: v*score for k, v in rule['weights'].items()},
                        'context', {'emotion': rule['requires'], 'prior_score': score,
                                    'threshold': rule['threshold']})
                    break
        scores = {k: round(-math.expm1(-v), 8) for k, v in total.items()}
        return TextAffect(scores, tuple(evidence), len(covered)/max(1, word_count),
                          'estimated' if evidence else 'unknown', self.model_id)
