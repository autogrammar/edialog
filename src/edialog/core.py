"""AffectScript 0.1: explicit, uncalibrated affect simulation. Python stdlib only."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import random
import re
import shlex
import sys

VERSION = '0.1'
MAX_TICKS = 1000
OPS = {'>=', '<=', '>', '<', '=='}
IDENT = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


class DSLError(ValueError):
    def __init__(self, code, message, line=None):
        self.code, self.line = code, line
        super().__init__(f'{code}' + (f' at line {line}' if line else '') + ': ' + message)


def number(value, low, high, line):
    try:
        result = float(value)
    except (ValueError, TypeError):
        raise DSLError('E_NUMBER', f'Expected finite number, got {value!r}', line)
    if not math.isfinite(result) or not low <= result <= high:
        raise DSLError('E_RANGE', f'Expected finite number in [{low}, {high}]', line)
    return result


def ident(value, line):
    if not IDENT.fullmatch(value):
        raise DSLError('E_IDENTIFIER', f'Invalid identifier: {value!r}', line)
    return value


def parse(source):
    """Parse and statically validate; no eval, I/O, imports or code execution in DSL."""
    if len(source.encode('utf-8')) > 1_000_000:
        raise DSLError('E_LIMIT', 'Source larger than 1 MB')
    p = {'version': VERSION, 'model': None, 'seed': 0, 'noise': 0.0,
         'axes': {}, 'concepts': {}, 'states': {}, 'drivers': [], 'couplings': [],
         'events': {}, 'requirements': {}, 'commands': [], 'warnings': []}
    seen_header = False
    runtime = False
    options = set()
    checkpoints = set()
    driver_keys, coupling_keys = set(), set()
    total_ticks = 0

    def length(tokens, expected, line):
        if len(tokens) != expected:
            raise DSLError('E_SYNTAX', f'{tokens[0]} expects {expected-1} arguments', line)

    def unique(mapping, key, line):
        ident(key, line)
        if key in mapping:
            raise DSLError('E_DUPLICATE', f'Duplicate declaration: {key}', line)

    def reference(mapping, key, label, line):
        if key not in mapping:
            raise DSLError('E_REFERENCE', f'Unknown {label}: {key}', line)

    for line, raw in enumerate(source.splitlines(), 1):
        try:
            t = shlex.split(raw, comments=True, posix=True)
        except ValueError as exc:
            raise DSLError('E_LEXER', str(exc), line) from None
        if not t:
            continue
        cmd = t[0]
        if not seen_header:
            if t != ['affect', VERSION]:
                raise DSLError('E_VERSION', 'First statement must be: affect 0.1', line)
            seen_header = True
            continue
        declarations = {'model', 'seed', 'noise', 'axis', 'concept', 'state', 'driver', 'couple', 'event', 'requires'}
        if cmd in declarations and runtime:
            raise DSLError('E_ORDER', 'Declarations must precede executable statements', line)
        if cmd in {'model', 'seed', 'noise'}:
            length(t, 2, line)
            if cmd in options:
                raise DSLError('E_DUPLICATE', f'Duplicate option: {cmd}', line)
            options.add(cmd)
            if cmd == 'model':
                if t[1] != 'illustrative':
                    raise DSLError('E_MODEL', 'Only model illustrative is implemented', line)
                p['model'] = t[1]
            elif cmd == 'seed':
                if not t[1].isdigit() or int(t[1]) > 2**32-1:
                    raise DSLError('E_SEED', 'Seed must be integer in [0, 2^32-1]', line)
                p['seed'] = int(t[1])
            else:
                p['noise'] = number(t[1], 0, 1, line)
        elif cmd == 'axis':
            length(t, 2, line)
            unique(p['axes'], t[1], line)
            p['axes'][t[1]] = {'line': line}
        elif cmd == 'concept':
            length(t, 3, line)
            unique(p['concepts'], t[1], line)
            if not t[2].strip():
                raise DSLError('E_CONCEPT', 'Definition cannot be empty', line)
            p['concepts'][t[1]] = {'definition': t[2], 'line': line}
        elif cmd == 'state':
            length(t, 5, line)
            if t[3] != 'retention':
                raise DSLError('E_SYNTAX', 'Use: state ID NUMBER retention NUMBER', line)
            unique(p['states'], t[1], line)
            reference(p['concepts'], t[1], 'concept', line)
            p['states'][t[1]] = {'initial': number(t[2], 0, 1, line),
                               'retention': number(t[4], 0, 1, line), 'line': line}
        elif cmd in {'driver', 'couple'}:
            length(t, 4, line)
            reference(p['concepts'], t[1], 'concept', line)
            reference(p['axes'] if cmd == 'driver' else p['concepts'], t[2],
                      'axis' if cmd == 'driver' else 'concept', line)
            key = (t[1], t[2])
            keys = driver_keys if cmd == 'driver' else coupling_keys
            if key in keys:
                raise DSLError('E_DUPLICATE', f'Duplicate {cmd}: {key}', line)
            if cmd == 'couple' and t[1] == t[2]:
                raise DSLError('E_COUPLING', 'Self-coupling belongs in retention', line)
            keys.add(key)
            p['drivers' if cmd == 'driver' else 'couplings'].append({
                'source': t[1], 'target': t[2], 'weight': number(t[3], -1, 1, line), 'line': line})
        elif cmd == 'requires':
            length(t, 5, line)
            if t[2] != 'drop':
                raise DSLError('E_SYNTAX', 'Use: requires CONCEPT drop SIGNAL MINIMUM', line)
            unique(p['requirements'], t[1], line)
            reference(p['concepts'], t[1], 'concept', line)
            reference(p['concepts'], t[3], 'concept', line)
            minimum = number(t[4], 0, 1, line)
            if minimum == 0 or t[1] == t[3]:
                raise DSLError('E_REQUIREMENT', 'Drop must be positive and signal distinct', line)
            p['requirements'][t[1]] = {'signal': t[3], 'minimum': minimum, 'line': line}
        elif cmd == 'event':
            if len(t) < 3:
                raise DSLError('E_SYNTAX', 'Use: event ID AXIS=NUMBER ...', line)
            unique(p['events'], t[1], line)
            values = {}
            for pair in t[2:]:
                if pair.count('=') != 1:
                    raise DSLError('E_SYNTAX', 'Expected AXIS=NUMBER', line)
                axis, value = pair.split('=')
                reference(p['axes'], axis, 'axis', line)
                if axis in values:
                    raise DSLError('E_DUPLICATE', f'Duplicate event axis: {axis}', line)
                values[axis] = number(value, -1, 1, line)
            p['events'][t[1]] = {'appraisal': values, 'line': line}
        elif cmd in {'explain', 'apply', 'wait', 'checkpoint', 'expect', 'gate'}:
            runtime = True
            action = {'op': cmd, 'line': line}
            if cmd == 'explain':
                length(t, 2, line)
                reference(p['concepts'], t[1], 'concept', line)
                action['concept'] = t[1]
            elif cmd in {'apply', 'wait'}:
                length(t, 4 if cmd == 'apply' else 3, line)
                idx = 2 if cmd == 'apply' else 1
                if t[idx] != 'ticks' or not t[idx+1].isdigit() or not 1 <= int(t[idx+1]) <= MAX_TICKS:
                    raise DSLError('E_TICKS', 'Expected ticks followed by integer in [1,1000]', line)
                action['ticks'] = int(t[idx+1])
                total_ticks += action['ticks']
                if cmd == 'apply':
                    reference(p['events'], t[1], 'event', line)
                    action['event'] = t[1]
            elif cmd == 'checkpoint':
                length(t, 2, line)
                ident(t[1], line)
                if t[1] in checkpoints:
                    raise DSLError('E_DUPLICATE', f'Duplicate checkpoint: {t[1]}', line)
                checkpoints.add(t[1])
                action['name'] = t[1]
            else:
                length(t, 5, line)
                if t[1] not in checkpoints:
                    raise DSLError('E_REFERENCE', f'Checkpoint must occur earlier: {t[1]}', line)
                reference(p['concepts'], t[2], 'concept', line)
                if t[3] not in OPS:
                    raise DSLError('E_OPERATOR', f'Unknown comparator: {t[3]}', line)
                action.update(checkpoint=t[1], concept=t[2], comparator=t[3],
                              threshold=number(t[4], 0, 1, line))
            p['commands'].append(action)
        else:
            raise DSLError('E_STATEMENT', f'Unknown statement: {cmd}', line)
    if not seen_header or p['model'] != 'illustrative':
        raise DSLError('E_MODEL', 'Required: affect 0.1 and model illustrative')
    if not p['concepts'] or set(p['states']) != set(p['concepts']):
        raise DSLError('E_STATE', 'Every concept requires exactly one initial state')
    if len(p['concepts']) > 100 or len(p['commands']) > 5000 or total_ticks > MAX_TICKS:
        raise DSLError('E_LIMIT', 'Limit: 100 concepts, 5000 commands and 1000 ticks')
    if not p['commands']:
        raise DSLError('E_EMPTY', 'Program needs an executable statement')
    for req in p['requirements'].values():
        if req['signal'] in p['requirements']:
            raise DSLError('E_REQUIREMENT', 'A drop signal must be unguarded; no implicit dependency solver', req['line'])
    p['warnings'].append('W_UNCALIBRATED: weights and tick duration have no empirical calibration')
    for name, state in p['states'].items():
        bound = state['retention'] + sum(abs(c['weight']) for c in p['couplings'] if c['target'] == name)
        if bound >= 1:
            p['warnings'].append(f'W_PERSISTENCE: {name}: decay to zero is not guaranteed with current couplings')
    return p


def condition(value, op, threshold):
    if op == '==':
        return abs(value - threshold) <= 1e-9
    return {'>=': value >= threshold, '<=': value <= threshold,
            '>': value > threshold, '<': value < threshold}[op]


def simulate(program):
    """Synchronous bounded state update. Returns predictions, never observed human emotions."""
    p = program
    rng = random.Random(p['seed'])
    state = {k: v['initial'] for k, v in p['states'].items()}
    result = {'language': f'AffectScript {VERSION}', 'model': 'illustrative',
              'evidence_status': 'uncalibrated_simulation', 'seed': p['seed'],
              'noise_sd': p['noise'], 'warnings': list(p['warnings']),
              'trace': [], 'checkpoints': {}, 'checks': [], 'status': 'completed'}
    tick = 0
    stopped = False
    for command in p['commands']:
        op = command['op']
        if stopped:
            if op in {'expect', 'gate'}:
                result['checks'].append({**command, 'status': 'not_reached', 'value': None})
            continue
        if op == 'explain':
            name = command['concept']
            result['trace'].append({'tick': tick, 'op': op, 'concept': name,
                                    'definition': p['concepts'][name]['definition'],
                                    'state_changed': False, 'state': dict(state)})
        elif op in {'apply', 'wait'}:
            appraisal = p['events'][command['event']]['appraisal'] if op == 'apply' else {}
            for _ in range(command['ticks']):
                prev = dict(state)
                raw, clamped = {}, []
                for name in state:
                    drive = sum(d['weight'] * appraisal.get(d['target'], 0)
                                for d in p['drivers'] if d['source'] == name)
                    interaction = sum(c['weight'] * prev[c['source']]
                                      for c in p['couplings'] if c['target'] == name)
                    noise = rng.gauss(0, p['noise']) if p['noise'] else 0.0
                    raw[name] = p['states'][name]['retention'] * prev[name] + drive + interaction + noise
                candidate = {name: min(1.0, max(0.0, value)) for name, value in raw.items()}
                admitted = dict(raw)
                requirement_log = {}
                for name, req in p['requirements'].items():
                    drop = prev[req['signal']] - candidate[req['signal']]
                    passed = drop + 1e-12 >= req['minimum']
                    requirement_log[name] = {'signal': req['signal'], 'drop': drop,
                                             'minimum': req['minimum'], 'passed': passed}
                    if not passed:
                        admitted[name] = min(admitted[name], p['states'][name]['retention'] * prev[name])
                for name in state:
                    state[name] = min(1.0, max(0.0, admitted[name]))
                    if admitted[name] != state[name]:
                        clamped.append(name)
                tick += 1
                result['trace'].append({'tick': tick, 'op': op, 'event': command.get('event'),
                                        'appraisal': dict(appraisal), 'raw': raw,
                                        'requirements': requirement_log, 'admitted': admitted,
                                        'clamped': clamped, 'state': dict(state)})
        elif op == 'checkpoint':
            result['checkpoints'][command['name']] = {'tick': tick, 'kind': 'prediction', 'state': dict(state)}
        else:
            value = result['checkpoints'][command['checkpoint']]['state'][command['concept']]
            passed = condition(value, command['comparator'], command['threshold'])
            result['checks'].append({**command, 'status': 'passed' if passed else 'failed', 'value': value})
            if op == 'gate' and not passed:
                stopped = True
                result['status'] = 'halted_by_gate'
    result['final'] = dict(state)
    result['ticks'] = tick
    result['checks_passed'] = (all(c['status'] == 'passed' for c in result['checks'])
                              if result['checks'] else None)
    result['empirical_validity'] = 'not_assessed'
    return result


def compare_observations(result, payload):
    """Descriptive error only; supplied provenance is declared, not independently verified."""
    if not isinstance(payload, dict) or set(payload) != {'kind', 'source', 'records'}:
        raise DSLError('E_OBSERVATION', 'Expected exactly kind, source, records')
    if not isinstance(payload['kind'], str) or payload['kind'] not in {'synthetic_fixture', 'empirical_declared'}:
        raise DSLError('E_OBSERVATION', 'Unknown observation kind')
    if not isinstance(payload['source'], str) or not payload['source'].strip():
        raise DSLError('E_OBSERVATION', 'Source description required')
    if not isinstance(payload['records'], list) or not payload['records']:
        raise DSLError('E_OBSERVATION', 'At least one observation required')
    rows, seen = [], set()
    for r in payload['records']:
        if not isinstance(r, dict) or set(r) != {'checkpoint', 'concept', 'value'}:
            raise DSLError('E_OBSERVATION', 'Expected checkpoint, concept, value per observation')
        if not isinstance(r['checkpoint'], str) or not isinstance(r['concept'], str):
            raise DSLError('E_OBSERVATION', 'Checkpoint and concept must be strings')
        key = (r['checkpoint'], r['concept'])
        if key in seen:
            raise DSLError('E_OBSERVATION', 'Duplicate checkpoint/concept observation')
        seen.add(key)
        if type(r['value']) not in {int, float}:
            raise DSLError('E_OBSERVATION', 'Value must be a JSON number')
        observed = number(r['value'], 0, 1, None)
        try:
            predicted = result['checkpoints'][key[0]]['state'][key[1]]
        except KeyError:
            raise DSLError('E_OBSERVATION', 'Unknown or unreached checkpoint/concept') from None
        rows.append({**r, 'predicted': predicted, 'absolute_error': abs(predicted-observed)})
    return {'kind': payload['kind'], 'source': payload['source'], 'provenance_verified': False,
            'n': len(rows), 'mae': sum(r['absolute_error'] for r in rows)/len(rows),
            'rows': rows, 'empirical_validity': 'not_assessed',
            'interpretation': 'Synthetic fixture: software check only' if payload['kind'] == 'synthetic_fixture'
            else 'Descriptive comparison of user-declared data; not causal or external validation'}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('command', choices=['validate', 'run', 'compare'])
    ap.add_argument('program', type=Path)
    ap.add_argument('--observations', type=Path)
    ap.add_argument('--out', type=Path)
    args = ap.parse_args(argv)
    try:
        p = parse(args.program.read_text(encoding='utf-8'))
        if args.command == 'validate':
            result = {'valid': True, 'warnings': p['warnings'], 'concepts': list(p['concepts'])}
        else:
            result = simulate(p)
            if args.command == 'compare':
                if args.observations is None:
                    raise DSLError('E_ARGUMENT', 'compare requires --observations')
                result = compare_observations(result, json.loads(args.observations.read_text(encoding='utf-8')))
        text = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)
        if args.out:
            args.out.write_text(text+'\n', encoding='utf-8')
        else:
            print(text)
        return 2 if result.get('checks_passed') is False else 0
    except (DSLError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
