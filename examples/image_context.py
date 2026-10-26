"""Pixel analysis by default; optional live vision with --model."""
import argparse
import json
from pathlib import Path
from edialog import (analyze_image, CallableVisionBackend, OllamaJSON,
                     Dialogue, Participant, FictionRequest, FictionEngine)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', type=Path, default=Path(__file__).with_name('palette_fixture.png'))
    parser.add_argument('--model', help='Installed vision-capable Ollama model; enables HTTP calls')
    args = parser.parse_args()
    backend = CallableVisionBackend(OllamaJSON(args.model)) if args.model else None
    visual = analyze_image(args.image, backend=backend, context=['Dwoje bohaterów czeka przed drzwiami.'])
    print(json.dumps(visual.to_dict(), ensure_ascii=False, indent=2))
    d = Dialogue((Participant('anna', 'Anna'), Participant('jan', 'Jan')))
    d.add_turn('anna', 'Słyszę kroki.')
    p = FictionEngine().generate(d, actor='jan', recipients=('anna',), image=visual,
                                 request=FictionRequest({'scared': .7}))
    print(p.text)
    print('Image contribution:', p.candidates[0]['image_contribution'])


if __name__ == '__main__':
    main()
