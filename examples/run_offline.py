"""Execute examples without an LLM or network. Run after installing edialog."""
import argparse
import json
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--images', action='store_true', help='Also require and exercise Pillow')
    args = parser.parse_args()
    names = ['quickstart.py', 'context_weights.py', 'group_dialogue.py', 'custom_lexicon.py',
             'dsl_roundtrip.py', 'reader_evaluation.py', 'strategy_fixture.py',
             'fiction_demo.py', 'demo.py', 'backend_fixture.py']
    if args.images:
        names.append('image_context.py')
    results = []
    for name in names:
        result = subprocess.run([sys.executable, str(Path(__file__).with_name(name))],
                                capture_output=True, text=True)
        results.append({'example': name, 'passed': result.returncode == 0})
        if result.returncode:
            print(result.stderr or result.stdout, file=sys.stderr)
    print(json.dumps({'network': False, 'examples': results, 'passed': all(r['passed'] for r in results)}, indent=2))
    return 0 if all(r['passed'] for r in results) else 1


if __name__ == '__main__':
    sys.exit(main())
