"""Opt-in live example using Subactor SubLLM routing and keys.

Requires subactor-subllm and configured credentials (e.g. GEMINI_API_KEY, ZAI_API_KEY, OPENROUTER_API_KEY).
"""
import argparse
import sys

from edialog import (
    Dialogue,
    Participant,
    FictionEngine,
    FictionRequest,
    CallableFictionBackend,
    SubLLMJSON,
)


def main():
    parser = argparse.ArgumentParser(description="Live dialogue generation via subactor/subllm")
    parser.add_argument("--application", default="autogrammar-tillm", help="SubLLM application route")
    parser.add_argument("--function", default="invoke", help="SubLLM function route")
    parser.add_argument("--strategy", choices=["suspense", "release", "confrontation", "reunion"], default="suspense")
    parser.add_argument("--timeout", type=float, default=30.0, help="Request timeout in seconds")
    args = parser.parse_args()

    transport = SubLLMJSON(
        application=args.application,
        function=args.function,
        timeout=args.timeout,
    )

    d = Dialogue((
        Participant("anna", "Anna"),
        Participant("jan", "Jan"),
        Participant("piotr", "Piotr"),
    ))
    d.add_turn("anna", "Słyszę kroki, chociaż wszyscy już wyszli.", recipients=("jan", "piotr"))

    print(f"Connecting to SubLLM ({args.application}/{args.function})...")
    engine = FictionEngine(backend=CallableFictionBackend(transport))
    proposal = engine.generate(
        d,
        actor="jan",
        recipients=("anna", "piotr"),
        request=FictionRequest(strategies=(args.strategy,)),
    )

    print("\n--- Wybrana kwestia ---")
    print(proposal.text)
    print("\n--- Kandydaci i dystans ---")
    for candidate in proposal.candidates:
        print(f"[{candidate['distance']:.4f}] {candidate['text']}")


if __name__ == "__main__":
    main()
