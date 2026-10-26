import argparse
import json
from pathlib import Path
import sys

from .engine import ACTS, DialogueEngine
from .errors import EDialogError
from .models import Dialogue, Request


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main(argv=None):
    parser = argparse.ArgumentParser(description='edialog 0.4: local dialogue drafts and simulation')
    sub = parser.add_subparsers(dest='command', required=True)
    generate = sub.add_parser('generate')
    generate.add_argument('dialogue', type=Path)
    generate.add_argument('--actor', required=True)
    generate.add_argument('--to', nargs='+', required=True, dest='recipients')
    group = generate.add_mutually_exclusive_group(required=True)
    group.add_argument('--instruction')
    group.add_argument('--request', type=Path)
    generate.add_argument('--out', type=Path)
    generate.add_argument('--dsl-out', type=Path)
    for name in ('validate', 'replay'):
        p = sub.add_parser(name)
        p.add_argument('dialogue', type=Path)
        p.add_argument('--plan', type=Path, required=True)
        p.add_argument('--out', type=Path)
    sub.add_parser('strategies')
    args = parser.parse_args(argv)
    try:
        engine = DialogueEngine()
        if args.command == 'strategies':
            result = {'strategies': list(ACTS), 'provenance': 'illustrative fixtures'}
        else:
            dialogue = Dialogue.from_dict(load(args.dialogue))
            if args.command == 'generate':
                request = Request.from_dict(load(args.request)) if args.request else None
                proposal = engine.propose(dialogue, actor=args.actor, recipients=args.recipients,
                                          instruction=args.instruction, request=request)
                result = proposal.to_dict()
                if args.dsl_out:
                    args.dsl_out.write_text(proposal.dsl+'\n', encoding='utf-8')
            elif args.command == 'validate':
                engine.validate_dsl(args.plan.read_text(encoding='utf-8'), dialogue)
                result = {'valid': True, 'empirical_validity': 'not_assessed'}
            else:
                result = engine.propose_from_dsl(args.plan.read_text(encoding='utf-8'), dialogue).to_dict()
        encoded = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)
        if getattr(args, 'out', None):
            args.out.write_text(encoded+'\n', encoding='utf-8')
        else:
            print(encoded)
        return 0
    except (EDialogError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f'{type(exc).__name__}: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
