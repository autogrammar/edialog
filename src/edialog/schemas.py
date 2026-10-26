"""Provider-neutral JSON schemas. Python validators additionally enforce dialogue scope."""
from .models import EMOTIONS, STRATEGIES

REQUEST_SCHEMA = {
    'type': 'object', 'additionalProperties': False,
    'required': ['goals', 'strategies'],
    'properties': {
        'goals': {'type': 'array', 'maxItems': 30, 'items': {
            'type': 'object', 'additionalProperties': False,
            'required': ['participant', 'emotion', 'direction'],
            'properties': {
                'participant': {'type': 'string', 'pattern': '^[a-z][a-z0-9_]{0,47}$'},
                'emotion': {'type': 'string', 'enum': list(EMOTIONS)},
                'direction': {'type': 'string', 'enum': ['increase', 'decrease']},
                'threshold': {'type': ['number', 'null'], 'minimum': 0, 'maximum': 1},
            }}},
        'strategies': {'type': 'array', 'maxItems': 3, 'uniqueItems': True,
                       'items': {'type': 'string', 'enum': list(STRATEGIES)}},
    },
    'anyOf': [{'properties': {'goals': {'minItems': 1}}}, {'properties': {'strategies': {'minItems': 1}}}],
}
REPLY_SCHEMA = {
    'type': 'object', 'additionalProperties': False, 'required': ['text', 'evidence_turn_ids'],
    'properties': {
        'text': {'type': 'string', 'minLength': 1, 'maxLength': 6000},
        'evidence_turn_ids': {'type': 'array', 'uniqueItems': True, 'items': {'type': 'string'}},
    },
}
