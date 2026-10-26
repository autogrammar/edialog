from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
import math
import re

from .errors import ValidationError, UnsupportedObjective

EMOTIONS = {
    'tension': 'Napięcie: szerszy stan afektywny, nie pojedyncza emocja podstawowa.',
    'frustration': 'Frustracja: stan związany z utrudnieniem osiągnięcia celu.',
    'confusion': 'Dezorientacja: stan poznawczy związany z brakiem zrozumienia.',
    'curiosity': 'Ciekawość: zainteresowanie uzyskaniem brakującej informacji.',
    'relief': 'Ulga: przeżycie związane ze zmniejszeniem wcześniejszego napięcia.',
    'calm': 'Spokój: szerszy stan afektywny o niskim napięciu.',
}
ALLOWED_DIRECTIONS = {'tension': 'decrease', 'frustration': 'decrease',
                      'confusion': 'decrease', 'curiosity': 'increase',
                      'relief': 'increase', 'calm': 'increase'}
STRATEGIES = ('empathy', 'clarify', 'explain', 'invite', 'summarize', 'deescalate')
ID = re.compile(r'^[a-z][a-z0-9_]{0,47}$')


def identifier(value):
    if not isinstance(value, str) or not ID.fullmatch(value):
        raise ValidationError(f'Invalid stable identifier: {value!r}')
    return value


def unit(value, label='value'):
    if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 1:
        raise ValidationError(f'{label} must be a finite number in [0,1]')
    return float(value)


def text(value, label, maximum):
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ValidationError(f'{label} must contain 1..{maximum} characters')
    return value


def keys(obj, required, optional=()):
    if not isinstance(obj, dict) or not set(required) <= set(obj) or set(obj) - set(required) - set(optional):
        raise ValidationError(f'Expected fields {sorted(required)}; optional {sorted(optional)}')


@dataclass(frozen=True)
class Participant:
    id: str
    name: str
    aliases: tuple[str, ...] = ()
    address: str | None = None

    def __post_init__(self):
        identifier(self.id)
        text(self.name, 'name', 80)
        if '\n' in self.name or '\r' in self.name:
            raise ValidationError('Name must be one line')
        if not isinstance(self.aliases, (tuple, list)) or len(self.aliases) > 10:
            raise ValidationError('At most 10 name aliases')
        object.__setattr__(self, 'aliases', tuple(self.aliases))
        for alias in self.aliases:
            text(alias, 'alias', 80)
        if self.address is not None:
            text(self.address, 'address', 80)
            if '\n' in self.address or '\r' in self.address:
                raise ValidationError('Address must be one line')


@dataclass(frozen=True)
class Turn:
    id: str
    speaker: str
    text: str
    recipients: tuple[str, ...] = ()
    reply_to: str | None = None
    kind: str = 'observed'


@dataclass(frozen=True)
class Reading:
    value: float
    origin: str
    at_turn_count: int
    source_turn: str | None = None


@dataclass(frozen=True)
class Goal:
    participant: str
    emotion: str
    direction: str
    threshold: float | None = None

    def __post_init__(self):
        identifier(self.participant)
        if not isinstance(self.emotion, str) or self.emotion not in EMOTIONS:
            raise UnsupportedObjective(f'Unsupported construct: {self.emotion!r}')
        if self.direction != ALLOWED_DIRECTIONS[self.emotion]:
            raise UnsupportedObjective(f'{self.emotion} supports only {ALLOWED_DIRECTIONS[self.emotion]}')
        if self.threshold is not None:
            object.__setattr__(self, 'threshold', unit(self.threshold, 'threshold'))


@dataclass(frozen=True)
class Request:
    goals: tuple[Goal, ...] = ()
    strategies: tuple[str, ...] = ()
    interpretation: str = 'structured'

    def __post_init__(self):
        if not isinstance(self.goals, (tuple, list)) or not isinstance(self.strategies, (tuple, list)):
            raise ValidationError('Goals and strategies must be sequences')
        object.__setattr__(self, 'goals', tuple(self.goals))
        object.__setattr__(self, 'strategies', tuple(self.strategies))
        if not self.goals and not self.strategies:
            raise ValidationError('At least one goal or strategy is required')
        if len(self.goals) > 30 or len(self.strategies) > 3:
            raise ValidationError('Limit: 30 goals and 3 strategies')
        if any(not isinstance(g, Goal) for g in self.goals):
            raise ValidationError('Goals must be Goal objects')
        if any(not isinstance(s, str) or s not in STRATEGIES for s in self.strategies):
            raise UnsupportedObjective('Unknown strategy; use the supported strategy catalog')
        if len(set(self.strategies)) != len(self.strategies):
            raise ValidationError('Repeated strategy')
        pairs = [(g.participant, g.emotion) for g in self.goals]
        if len(pairs) != len(set(pairs)):
            raise ValidationError('Repeated participant/construct goal')
        text(self.interpretation, 'interpretation', 200)

    def to_dict(self):
        return {'goals': [asdict(g) for g in self.goals], 'strategies': list(self.strategies),
                'interpretation': self.interpretation}

    @classmethod
    def from_dict(cls, obj):
        keys(obj, {'goals', 'strategies'}, {'interpretation'})
        if not isinstance(obj['goals'], list) or not isinstance(obj['strategies'], list):
            raise ValidationError('goals and strategies must be arrays')
        goals = []
        for g in obj['goals']:
            keys(g, {'participant', 'emotion', 'direction'}, {'threshold'})
            goals.append(Goal(**g))
        return cls(tuple(goals), tuple(obj['strategies']), obj.get('interpretation', 'structured'))


@dataclass
class Dialogue:
    participants: tuple[Participant, ...]
    turns: list[Turn] = field(default_factory=list)
    readings: dict[str, dict[str, Reading]] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.participants, (tuple, list)) or not 2 <= len(self.participants) <= 50:
            raise ValidationError('Dialogue requires 2..50 participants')
        self.participants = tuple(self.participants)
        if any(not isinstance(p, Participant) for p in self.participants):
            raise ValidationError('Expected Participant objects')
        if len({p.id for p in self.participants}) != len(self.participants):
            raise ValidationError('Participant IDs must be unique')
        if self.turns or self.readings:
            raise ValidationError('Use add_turn/set_state or Dialogue.from_dict to import history')

    def participant(self, pid):
        for p in self.participants:
            if p.id == pid:
                return p
        raise ValidationError(f'Unknown participant: {pid!r}')

    def add_turn(self, speaker, content, *, recipients=(), turn_id=None, reply_to=None, kind='observed'):
        self.participant(speaker)
        text(content, 'turn', 5000)
        if len(self.turns) >= 200:
            raise ValidationError('Limit: 200 turns')
        if (not isinstance(recipients, (list, tuple)) or any(not isinstance(r, str) for r in recipients)
                or len(set(recipients)) != len(recipients)):
            raise ValidationError('Recipients must be a unique list/tuple')
        for pid in recipients:
            self.participant(pid)
            if pid == speaker:
                raise ValidationError('A turn cannot be addressed to its own speaker')
        if kind not in ('observed', 'synthetic'):
            raise ValidationError('Turn kind must be observed or synthetic')
        if turn_id is None:
            n = len(self.turns)+1
            while any(t.id == f't{n}' for t in self.turns):
                n += 1
            turn_id = f't{n}'
        identifier(turn_id)
        if any(t.id == turn_id for t in self.turns):
            raise ValidationError('Duplicate turn ID')
        if reply_to is not None and not any(t.id == reply_to for t in self.turns):
            raise ValidationError('reply_to must reference an earlier turn')
        turn = Turn(turn_id, speaker, content, tuple(recipients), reply_to, kind)
        self.turns.append(turn)
        return turn

    def set_state(self, participant, values, *, origin='synthetic_fixture', source_turn=None):
        self.participant(participant)
        if origin not in ('synthetic_fixture', 'self_report', 'simulation'):
            raise ValidationError('Unknown state provenance')
        if not isinstance(values, dict) or not values:
            raise ValidationError('State requires a nonempty mapping')
        if source_turn is not None:
            matches = [t for t in self.turns if t.id == source_turn and t.speaker == participant]
            if not matches:
                raise ValidationError('State source must be a turn by the same participant')
        if origin == 'self_report' and source_turn is None:
            raise ValidationError('self_report requires its source_turn')
        if origin == 'self_report' and not any(t.id == source_turn and t.kind == 'observed' for t in self.turns):
            raise ValidationError('A synthetic turn cannot be the source of a self-report')
        pending = {}
        at_count = (next(i+1 for i, t in enumerate(self.turns) if t.id == source_turn)
                    if origin == 'self_report' else len(self.turns))
        for concept, value in values.items():
            if concept not in EMOTIONS:
                raise ValidationError(f'Unknown state construct: {concept}')
            pending[concept] = Reading(unit(value), origin, at_count, source_turn)
        self.readings.setdefault(participant, {}).update(pending)

    def latest(self, participant, addressed_to=None, audience=()):
        for t in reversed(self.turns):
            visible = not t.recipients or set(audience) <= (set(t.recipients) | {t.speaker})
            if visible and t.speaker == participant and (not t.recipients or addressed_to is None or addressed_to in t.recipients):
                return t
        return None

    def usable_readings(self, participant):
        result = {}
        for name, reading in self.readings.get(participant, {}).items():
            subsequent = self.turns[reading.at_turn_count:]
            if not any(t.speaker == participant and t.kind == 'observed' for t in subsequent):
                result[name] = reading
        return result

    def to_dict(self):
        return {'participants': [asdict(p) for p in self.participants],
                'turns': [asdict(t) for t in self.turns],
                'readings': {pid: {name: asdict(r) for name, r in rs.items()} for pid, rs in self.readings.items()}}

    def fingerprint(self):
        canonical = json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=False, allow_nan=False)
        return hashlib.sha256(canonical.encode()).hexdigest()

    @classmethod
    def from_dict(cls, obj):
        keys(obj, {'participants'}, {'turns', 'readings'})
        if not isinstance(obj['participants'], list) or not isinstance(obj.get('turns', []), list):
            raise ValidationError('Participants and turns must be arrays')
        people = []
        for p in obj['participants']:
            keys(p, {'id', 'name'}, {'aliases', 'address'})
            people.append(Participant(**p))
        d = cls(tuple(people))
        for t in obj.get('turns', []):
            keys(t, {'id', 'speaker', 'text'}, {'recipients', 'reply_to', 'kind'})
            d.add_turn(t['speaker'], t['text'], recipients=t.get('recipients', ()), turn_id=t['id'],
                       reply_to=t.get('reply_to'), kind=t.get('kind', 'observed'))
        readings = obj.get('readings', {})
        if not isinstance(readings, dict):
            raise ValidationError('readings must be a mapping')
        for pid, rs in readings.items():
            if not isinstance(rs, dict):
                raise ValidationError('Participant readings must be a mapping')
            for name, r in rs.items():
                keys(r, {'value', 'origin', 'at_turn_count'}, {'source_turn'})
                count = r['at_turn_count']
                if type(count) is not int or not 0 <= count <= len(d.turns):
                    raise ValidationError('Invalid state timestamp')
                if r.get('source_turn') and not any(t.id == r['source_turn'] for t in d.turns[:count]):
                    raise ValidationError('Reading source cannot be in the future')
                if r['origin'] == 'self_report' and r.get('source_turn'):
                    source_count = next(i+1 for i, t in enumerate(d.turns) if t.id == r['source_turn'])
                    if source_count != count:
                        raise ValidationError('Self-report timestamp must match its source turn')
                d.set_state(pid, {name: r['value']}, origin=r['origin'], source_turn=r.get('source_turn'))
                d.readings[pid][name] = Reading(float(r['value']), r['origin'], count, r.get('source_turn'))
        return d
