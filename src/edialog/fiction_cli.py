"""Command-line fiction analysis, ranking and reproducible plan replay."""
import argparse
import json
from pathlib import Path
import sys

from .affect import EMOTION_CODES, EmotionLexicon, TextEmotionAnalyzer
from .errors import EDialogError
from .fiction import FictionEngine, FictionRequest, evaluate_annotations
from .models import Dialogue
from .vision import analyze_image


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main(argv=None):
    parser = argparse.ArgumentParser(description='edialog 0.4: fictional emotional tone and arcs')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('map')
    analyze = sub.add_parser('analyze')
    analyze.add_argument('--text', required=True)
    analyze.add_argument('--history', type=Path, help='JSON array of preceding texts')
    analyze.add_argument('--lexicon', type=Path)
    analyze.add_argument('--out', type=Path)
    image = sub.add_parser('image')
    image.add_argument('path', type=Path)
    image.add_argument('--features-only', action='store_true')
    image.add_argument('--out', type=Path)
    for name in ('generate', 'replay', 'timeline'):
        p = sub.add_parser(name)
        p.add_argument('dialogue', type=Path)
        p.add_argument('--out', type=Path)
        if name == 'replay':
            p.add_argument('--plan', required=True, type=Path)
            continue
        p.add_argument('--actor', required=True)
        p.add_argument('--to', required=True, nargs='+', dest='recipients')
        if name == 'generate':
            g = p.add_mutually_exclusive_group(required=True)
            g.add_argument('--instruction')
            g.add_argument('--request', type=Path)
            p.add_argument('--image', type=Path)
            p.add_argument('--candidates', type=Path, help='JSON array of alternative lines')
            p.add_argument('--lexicon', type=Path)
            p.add_argument('--dsl-out', type=Path)
    evaluate = sub.add_parser('evaluate')
    evaluate.add_argument('annotations', type=Path)
    evaluate.add_argument('--out', type=Path)
    args = parser.parse_args(argv)
    try:
        lexicon = EmotionLexicon(load(args.lexicon)) if getattr(args, 'lexicon', None) else None
        analyzer = TextEmotionAnalyzer(lexicon)
        engine = FictionEngine(analyzer)
        if args.command == 'map':
            result = {'codes': EMOTION_CODES, 'semantics': 'categorical identifiers; intensity is a separate vector in [0,1]'}
        elif args.command == 'analyze':
            result = analyzer.analyze(args.text, history=load(args.history) if args.history else ()).to_dict()
        elif args.command == 'image':
            result = analyze_image(args.path, pixel_heuristics=not args.features_only).to_dict()
        elif args.command == 'evaluate':
            result = evaluate_annotations(load(args.annotations))
        else:
            dialogue = Dialogue.from_dict(load(args.dialogue))
            if args.command == 'replay':
                result = engine.replay(args.plan.read_text(encoding='utf-8'), dialogue).to_dict()
            elif args.command == 'timeline':
                result = engine.analyze_dialogue(dialogue, actor=args.actor, recipients=args.recipients)
            else:
                proposal = engine.generate(dialogue, actor=args.actor, recipients=args.recipients,
                    request=FictionRequest.from_dict(load(args.request)) if args.request else None,
                    instruction=args.instruction,
                    image=analyze_image(args.image) if args.image else None,
                    candidates=load(args.candidates) if args.candidates else None)
                result = proposal.to_dict()
                if args.dsl_out:
                    args.dsl_out.write_text(proposal.dsl+'\n', encoding='utf-8')
        encoded = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)
        if getattr(args, 'out', None):
            args.out.write_text(encoded+'\n', encoding='utf-8')
        else:
            print(encoded)
        return 0
    except (EDialogError, OSError, UnicodeError, ValueError) as exc:
        print(f'{type(exc).__name__}: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
