"""Opt-in live example. Requires a running local Ollama and installed model.

Use a vision-capable model when --image is supplied. This is not run by tests.
"""
import argparse
from edialog import (OllamaJSON, CallableFictionBackend, CallableVisionBackend,
                          FictionEngine, analyze_image)
from fiction_demo import make_scene


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', required=True, help='Name of an already installed Ollama model')
    parser.add_argument('--image', help='Optional PNG/JPEG/WebP; requires images extra and vision model')
    args = parser.parse_args()
    d = make_scene()
    complete = OllamaJSON(args.model)
    picture = analyze_image(args.image, backend=CallableVisionBackend(complete),
                            context=[t.text for t in d.turns]) if args.image else None
    engine = FictionEngine(backend=CallableFictionBackend(complete))
    proposal = engine.generate(d, actor='jan', recipients=('anna', 'piotr'),
        instruction='Zbuduj w czytelniku silne poczucie grozy, około 0.85 w modelu; zachowaj sens poprzednich kwestii.',
        image=picture)
    print(proposal.text)
    print(proposal.candidates[0]['reader_proxy'])
