from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import re

from .core import parse, simulate
from .errors import NeedsClarification, ValidationError
from .models import Dialogue, EMOTIONS, Goal, Request, STRATEGIES, keys
from .nl import CallableJSONBackend, ControlledNL, fold, validate_scope, RISK

VERSION = '0.2.0'
AXES = ('support', 'clarity', 'choice', 'interest', 'pace')
# Deliberate fixtures for software testing, NOT estimated psychological effects.
ACTS = {
    'empathy': {'support': .35, 'choice': .15},
    'clarify': {'clarity': .35, 'choice': .10},
    'explain': {'clarity': .45},
    'invite': {'interest': .40, 'choice': .25},
    'summarize': {'clarity': .30, 'pace': .10},
    'deescalate': {'pace': .40, 'choice': .30, 'support': .20},
}
DRIVERS = {
    'tension': {'support': -.30, 'clarity': -.20, 'pace': -.40},
    'frustration': {'support': -.30, 'choice': -.20},
    'confusion': {'clarity': -.55},
    'curiosity': {'interest': .45, 'clarity': -.15},
    'relief': {'clarity': .45, 'support': .20, 'pace': .30},
    'calm': {'pace': .40, 'support': .20},
}
DEFAULT_STRATEGY = {'tension': 'deescalate', 'frustration': 'empathy', 'confusion': 'clarify',
                    'curiosity': 'invite', 'relief': 'explain', 'calm': 'deescalate'}


@dataclass(frozen=True)
class Proposal:
    text: str
    dsl: str
    core_sources: dict
    simulations: dict
    evidence_turn_ids: tuple[str, ...]
    warnings: tuple[str, ...]
    history_fingerprint: str
    status: str = 'draft'

    def to_dict(self):
        return asdict(self)


def boundary(turn):
    if turn is None:
        return False
    normalized = fold(turn.text).strip()
    return bool(re.match(r'^(?:prosze[,\s]+)?(?:stop(?:[.!\s]|$)|nie chce (?:teraz )?rozmawiac(?: z toba)?(?:[.,!]|$)|'
                         r'nie pisz do mnie|zrobmy przerwe|potrzebuje przerwy|'
                         r"i don.t want to talk|please stop|let.s take a break)", normalized))


def excerpt(value):
    clean = re.sub(r'\s+', ' ', value).strip()
    clean = ''.join(c for c in clean if c.isprintable()).replace('„', '«').replace('”', '»')
    return clean[:180] + ('…' if len(clean) > 180 else '')


def render_local(dialogue, actor, recipients, strategies):
    blocks, evidence = [], []
    sentences = {
        'empathy': 'Chcę dobrze zrozumieć Twój punkt widzenia.',
        'clarify': 'Co w tej sprawie najbardziej wymaga teraz doprecyzowania?',
        'explain': 'Proponuję oddzielić ustalone informacje od tego, co nadal wymaga wyjaśnienia.',
        'invite': 'Który aspekt tej sprawy chcesz lepiej poznać?',
        'summarize': 'Sprawdźmy wspólnie, co jest ustalone, a co pozostaje otwarte.',
        'deescalate': 'Możemy zwolnić i zająć się jedną sprawą naraz. Jeśli wolisz przerwę, uszanujmy to.',
    }
    for pid in recipients:
        p = dialogue.participant(pid)
        t = dialogue.latest(pid, addressed_to=actor, audience=(actor, *recipients))
        parts = [f'{p.address or p.name},']
        if t:
            evidence.append(t.id)
            if not RISK.search(fold(t.text)):
                quote = excerpt(t.text)
                suffix = '' if quote.endswith(('.', '?', '!', '…')) else '.'
                parts.append(f'odnoszę się do Twoich słów: „{quote}”{suffix}')
            else:
                parts.append('odnoszę się do opisanej przez Ciebie sytuacji.')
        else:
            parts.append('chcę zaprosić Cię do rozmowy.')
        for strategy in strategies:
            parts.append(sentences[strategy])
        blocks.append(' '.join(parts))
    return '\n\n'.join(blocks), tuple(evidence)


def compile_recipient(dialogue, pid, request, strategies):
    readings = dialogue.usable_readings(pid)
    goals = [g for g in request.goals if g.participant == pid]
    tracked = set(readings) | {g.emotion for g in goals}
    if 'relief' in tracked:
        tracked.add('tension')
    missing = sorted(tracked - readings.keys())
    if not tracked or missing:
        return None, {'status': 'insufficient_state', 'missing': missing or ['initial_state'],
                      'empirical_validity': 'not_assessed'}
    names = sorted(tracked)
    lines = ['affect 0.1', 'model illustrative', 'seed 0', 'noise 0',
             '# Illustrative strategy effects. Numeric state is explicitly supplied.']
    lines.extend('axis '+axis for axis in AXES)
    for name in names:
        lines.append('concept '+name+' '+json.dumps(EMOTIONS[name], ensure_ascii=False))
    for name in names:
        lines.append(f'state {name} {readings[name].value:.12g} retention 0.85')
        for axis, weight in DRIVERS[name].items():
            lines.append(f'driver {name} {axis} {weight}')
    if 'relief' in tracked:
        lines.append('requires relief drop tension 0.04')
    for strategy in strategies:
        values = ' '.join(f'{axis}={value}' for axis, value in ACTS[strategy].items())
        lines.append(f'event {strategy} {values}')
    lines.extend('explain '+name for name in names)
    lines.append('checkpoint initial')
    for i, strategy in enumerate(strategies):
        lines.append(f'apply {strategy} ticks 1')
        lines.append(f'checkpoint step_{i+1}')
    lines.append('checkpoint final')
    for goal in goals:
        if goal.threshold is None:
            op = '>' if goal.direction == 'increase' else '<'
            threshold = readings[goal.emotion].value
        else:
            op = '>=' if goal.direction == 'increase' else '<='
            threshold = goal.threshold
        lines.append(f'expect final {goal.emotion} {op} {threshold:.12g}')
    source = '\n'.join(lines)+'\n'
    result = simulate(parse(source))
    result['initial_state_provenance'] = {name: asdict(readings[name]) for name in names}
    result['effect_provenance'] = 'fixed_illustrative_strategy_fixture_not_inferred_from_generated_text'
    return source, result


class DialogueEngine:
    def __init__(self, *, nl_backend=None, renderer=None):
        if nl_backend is not None and not isinstance(nl_backend, (ControlledNL, CallableJSONBackend)):
            raise ValidationError('Wrap an external NL backend in CallableJSONBackend')
        if renderer is not None and not isinstance(renderer, CallableJSONBackend):
            raise ValidationError('Wrap an external renderer in CallableJSONBackend')
        self.nl_backend = nl_backend or ControlledNL()
        self.renderer = renderer

    def parse_request(self, instruction, dialogue, *, actor, recipients):
        validate_scope(Request(strategies=('clarify',)), dialogue, actor, recipients)
        return self.nl_backend.parse(instruction, dialogue, actor=actor, recipients=recipients)

    def propose(self, dialogue, *, actor, recipients, instruction=None, request=None):
        # Revalidate snapshots rather than trusting mutable public collections.
        dialogue = Dialogue.from_dict(dialogue.to_dict())
        validate_scope(Request(strategies=('clarify',)), dialogue, actor, recipients)
        if (instruction is None) == (request is None):
            raise ValidationError('Provide exactly one of instruction or request')
        if instruction is not None:
            request = self.parse_request(instruction, dialogue, actor=actor, recipients=recipients)
        elif not isinstance(request, Request):
            raise ValidationError('request must be Request')
        validate_scope(request, dialogue, actor, recipients)
        strategies = request.strategies or tuple(dict.fromkeys(DEFAULT_STRATEGY[g.emotion] for g in request.goals))
        if len(strategies) > 3:
            raise NeedsClarification('More than three default strategies; specify a shorter sequence')
        request = Request(request.goals, strategies, request.interpretation)
        history = dialogue.fingerprint()
        evidence = tuple(t.id for pid in recipients if (t := dialogue.latest(pid, addressed_to=actor, audience=(actor, *recipients))))
        plan = {'language': 'affect-dialogue', 'version': '0.2', 'mode': 'simulation',
                'actor': actor, 'recipients': list(recipients), 'request': request.to_dict(),
                'context_turn_ids': list(evidence), 'history_fingerprint': history,
                'evidence_status': 'declared_plan_not_observed_emotional_change'}
        dsl = json.dumps(plan, ensure_ascii=False, indent=2)
        warnings = ['W_UNCALIBRATED: strategy effects are arbitrary fixtures, not psychological predictions',
                    'W_DRAFT: no message is sent and no real emotional state is updated']
        paused = [pid for pid in recipients if boundary(dialogue.latest(pid, addressed_to=actor))]
        if paused:
            return Proposal('Zróbmy przerwę w rozmowie.', dsl, {}, {}, evidence,
                            tuple(warnings+['W_BOUNDARY: scenario paused; numerical goal was not pursued']),
                            history, 'paused')
        draft, evidence = render_local(dialogue, actor, recipients, strategies)
        if self.renderer is not None:
            rendered = self.renderer.render(plan, dialogue, draft)
            draft, evidence = rendered['text'], tuple(rendered['evidence_turn_ids'])
            warnings.append('W_EXTERNAL_TEXT: structure checked; factual fidelity and wording require review')
        if request.interpretation.startswith('external_backend'):
            warnings.append('W_EXTERNAL_NL: structured parse validated; complete semantic fidelity is not established')
        sources, simulations = {}, {}
        for pid in recipients:
            source, result = compile_recipient(dialogue, pid, request, strategies)
            simulations[pid] = result
            if source:
                sources[pid] = source
            else:
                warnings.append(f'W_MISSING_STATE: {pid}; no numeric prediction; missing or stale initial state')
        return Proposal(draft, dsl, sources, simulations, evidence, tuple(warnings), history)

    def validate_dsl(self, source, dialogue):
        if not isinstance(source, str) or len(source.encode()) > 100_000:
            raise ValidationError('Dialogue DSL must be a JSON string of at most 100 KB')
        try:
            obj = json.loads(source)
        except json.JSONDecodeError as exc:
            raise ValidationError(f'Invalid JSON DSL: {exc.msg}') from None
        keys(obj, {'language', 'version', 'mode', 'actor', 'recipients', 'request', 'context_turn_ids',
                   'history_fingerprint', 'evidence_status'})
        if (obj['language'], obj['version'], obj['mode']) != ('affect-dialogue', '0.2', 'simulation'):
            raise ValidationError('Expected affect-dialogue 0.2 in simulation mode')
        if obj['evidence_status'] != 'declared_plan_not_observed_emotional_change':
            raise ValidationError('Cannot promote plan to an observed effect')
        if obj['history_fingerprint'] != dialogue.fingerprint():
            raise ValidationError('Plan belongs to a different dialogue snapshot')
        request = Request.from_dict(obj['request'])
        validate_scope(request, dialogue, obj['actor'], obj['recipients'])
        expected = [t.id for pid in obj['recipients'] if (t := dialogue.latest(pid, addressed_to=obj['actor'], audience=(obj['actor'], *obj['recipients'])))]
        if obj['context_turn_ids'] != expected:
            raise ValidationError('Context references do not match the dialogue snapshot')
        return obj

    def propose_from_dsl(self, source, dialogue):
        plan = self.validate_dsl(source, dialogue)
        return self.propose(dialogue, actor=plan['actor'], recipients=plan['recipients'],
                            request=Request.from_dict(plan['request']))

    def advance_simulation(self, dialogue, proposal):
        """Return a new simulation branch. Never modifies the supplied dialogue."""
        if not isinstance(proposal, Proposal) or proposal.status != 'draft':
            raise ValidationError('Only a non-paused Proposal can advance a simulation')
        if proposal.history_fingerprint != dialogue.fingerprint():
            raise ValidationError('Stale proposal: dialogue changed after generation')
        plan = self.validate_dsl(proposal.dsl, dialogue)
        # Recompute transitions from the validated plan, not caller-edited result dictionaries.
        request = Request.from_dict(plan['request'])
        outcomes = {pid: compile_recipient(dialogue, pid, request, request.strategies)[1]
                    for pid in plan['recipients']}
        branch = Dialogue.from_dict(dialogue.to_dict())
        evidence = plan['context_turn_ids']
        branch.add_turn(plan['actor'], proposal.text, recipients=plan['recipients'],
                        reply_to=evidence[-1] if evidence else None, kind='synthetic')
        for pid, result in outcomes.items():
            if 'final' in result:
                branch.set_state(pid, result['final'], origin='simulation')
        return branch
