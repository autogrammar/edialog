"""Demonstracja architektury procesowej (POA), MCP oraz kontraktu DockURI (uri()) dla edialog.

Pokazuje krok po kroku wszystkie 6 procesów potoku:
1. proc://edialog/nl/parse/v1          (NL + poziom zaufania -> FictionRequest + Action URI)
2. proc://edialog/context/filter/v1    (Filtrowanie widoczności kwestii + bazowy reader_proxy)
3. proc://edialog/candidates/generate/v1 (Generowanie puli kandydatów z dowodami kontekstu)
4. proc://edialog/affect/score/v1      (Analiza afektu, dystansu i ranking kandydatów)
5. proc://edialog/dsl/compile/v1       (Kompilacja DSL affect-fiction 0.3 + weryfikacja replay)
6. proc://edialog/report/emit/v1       (CompositeExecutionReceipt + łańcuch logów + snippety reużycia)

Uruchomienie:
  PYTHONPATH=src .venv/bin/python examples/mcp_process_pipeline.py
  PYTHONPATH=/home/tom/github/subactor/subllm/src:src .venv/bin/python examples/mcp_process_pipeline.py --live-subllm
"""
from __future__ import annotations

import argparse
import json

from edialog import (
    Dialogue,
    EDialogMCPServer,
    Participant,
    run_process_pipeline,
    uri,
)


def build_sample_dialogue() -> Dialogue:
    d = Dialogue([
        Participant('tomasz', 'Tomasz (40 l., architekt)'),
        Participant('klaudia', 'Klaudia (25 l., projektantka)'),
        Participant('marek', 'Marek (współpracownik z biura)'),
    ])
    # Prywatna uwaga Marka do Tomasza (niewidoczna dla Klaudii)
    d.add_turn(
        'marek',
        'Klaudia z trzeciego piętra znowu stoi pod wiatą bez parasola.',
        recipients=('tomasz',),
    )
    # Widoczna wymiana między Klaudią a Tomaszem
    d.add_turn(
        'klaudia',
        'Wygląda na to, że dzisiejsza ulewa zatrzymała całe miasto. Znamy się chyba z windy na czwartym piętrze?',
        recipients=('tomasz',),
    )
    return d


def print_pipeline_inspection(result_dict: dict, label: str) -> None:
    print('=' * 92)
    print(f'SCENARIUSZ PROCESOWY: {label}')
    print(f"Pipeline ID : {result_dict['pipeline_id']}")
    print(f"Action URI  : {result_dict['action_uri']}")
    print('=' * 92)

    print('\n[1] PRZEJRZYSTY ŚLAD WYKONANIA KOLEJNYCH PROCESÓW (6 ETAPÓW):')
    for step in result_dict['steps']:
        print(f"\n  Krok {step['step_index']}: {step['uri']} [{step['effect']}] ({step['duration_ms']:.3f} ms)")
        print(f"    Tytuł       : {step['title']}")
        print(f"    Wyjaśnienie : {step['explanation']}")
        print(f"    Wejście SHA : {step['input_sha256'][:16]}... | Wyjście SHA: {step['output_sha256'][:16]}... | Stan: {step['state_hash'][:16]}...")
        print(f"    Wejście     : {json.dumps(step['input_summary'], ensure_ascii=False)}")
        if step['step_id'] == 'step4_affect_score':
            print('    Tabela rankingu kandydatów (dlaczego wygrał kandydat #1):')
            for row in step['output_summary']['ranking_table']:
                print(
                    f"      #{row['rank']} [idx={row['candidate_index']}] "
                    f"rank_loss={row['rank_loss']:.4f} (dist={row['distance']:.4f}, rep_pen={row['repetition_penalty']:.4f}): "
                    f"„{row['text']}”"
                )
        else:
            print(f"    Wyjście     : {json.dumps(step['output_summary'], ensure_ascii=False)}")

    print('\n[2] KWIT WYKONANIA POTOKU (CompositeExecutionReceipt - wellmanifest.wellman/receipt/v1):')
    rcpt = result_dict['receipt']
    print(
        f"  receipt_id={rcpt['receipt_id']} | status={rcpt['status']} | "
        f"total_duration_ms={rcpt['total_duration_ms']} | chain_root_sha256={rcpt['chain_root_sha256'][:24]}..."
    )

    print('\n[3] ŁAŃCUCH ZDARZEŃ LOGÓW (wellmanifest.logs/event/v1):')
    for ev in result_dict['event_log']:
        print(
            f"  seq={ev['seq']} | {ev['process_uri']} | "
            f"prev={ev['prev_hash'][:10]}... -> hash={ev['event_hash'][:10]}..."
        )

    print('\n[4] WYBRANA KWESTIA FINALNA:')
    print(f"  >>> „{result_dict['proposal']['text']}”")

    print('\n[5] JAK PROSTO REUŻYĆ TEN PROCES (Gotowe snippety z raportu):')
    print('  --- A. Jednolinijkowe wywołanie DockURI w Pythonie ---')
    for line in result_dict['reuse_snippets']['dockuri_python'].splitlines():
        print(f'    {line}')
    print('  --- B. Wywołanie z linii poleceń (CLI) ---')
    print(f"    {result_dict['reuse_snippets']['dockuri_cli'][:120]}...")


def main() -> None:
    parser = argparse.ArgumentParser(description='Demonstracja procesowego MCP dla edialog.')
    parser.add_argument('--live-subllm', action='store_true', help='Użyj live SubLLMJSON w drugim przebiegu.')
    args = parser.parse_args()

    dialogue = build_sample_dialogue()
    server = EDialogMCPServer()

    # 1. Odkrywanie procesów przez MCP registry_search
    search_resp = server.handle_rpc({
        'jsonrpc': '2.0',
        'id': 1,
        'method': 'tools/call',
        'params': {'name': 'registry_search', 'arguments': {'query': ''}},
    })
    ops = search_resp['result']['structuredContent']['operations']
    print(f"Zarejestrowane procesy URI w MCP ({len(ops)} procedur):")
    for op in ops:
        print(f"  - {op['uri']:38s} ({op['effect']:4s}) : {op['description']}")
    print()

    # 2. Planowanie zadania przez MCP task_plan
    plan_resp = server.handle_rpc({
        'jsonrpc': '2.0',
        'id': 2,
        'method': 'tools/call',
        'params': {
            'name': 'task_plan',
            'arguments': {
                'actor': 'tomasz',
                'recipients': ['klaudia'],
                'trust_level': 'low',
                'instruction': 'Spokojna, intrygująca odpowiedź z poszanowaniem granic.',
            },
        },
    })
    planned = plan_resp['result']['structuredContent']
    print(f"Plan zadania (wellmanifest.nl-plan/v1): Action URI = {planned['action_uri']}")
    print()

    # 3. Wykonanie potoku deterministycznego (z kandydatami autorskimi pokazującymi różnicę w punktacji)
    custom_candidates = [
        'Spokojnie. Zanim przyjedzie następny tramwaj, deszcz zdąży trochę odpuścić — jeśli chcesz, pod zadaszeniem z tej strony mniej wieje.',
        'Nie wsiadaj do tego autobusu. Boję się, że ktoś nas obserwuje od samego wyjścia z biurowca.',
        'Zwyczajnie poczekajmy chwilę; w taką ulewę i tak nikt dzisiaj nigdzie się nie spieszy.',
    ]
    exec_resp = server.handle_rpc({
        'jsonrpc': '2.0',
        'id': 3,
        'method': 'tools/call',
        'params': {
            'name': 'task_execute',
            'arguments': {
                'dialogue': dialogue.to_dict(),
                'actor': 'tomasz',
                'recipients': ['klaudia'],
                'trust_level': 'low',
                'candidates': custom_candidates,
            },
        },
    })
    result_offline = exec_resp['result']['structuredContent']
    print_pipeline_inspection(result_offline, 'TRYB DETERMINISTYCZNY (Niskie zaufanie + poszanowanie granic)')

    # 4. Bezpośrednie wywołanie pojedynczego procesu przez uri() (DOCK-URI-001)
    print('\n' + '=' * 92)
    print('REUŻYCIE POJEDYNCZEGO PROCESU PRZEZ uri("proc://edialog/nl/parse/v1", ...):')
    single_step = uri(
        'proc://edialog/nl/parse/v1',
        {'actor': 'tomasz', 'recipients': ['klaudia'], 'trust_level': 'high'},
    )
    print(json.dumps(single_step, ensure_ascii=False, indent=2))

    # 5. Opcjonalny przebieg live z SubLLMJSON
    if args.live_subllm:
        print('\n' + '=' * 92)
        live_res = run_process_pipeline(
            dialogue,
            actor='tomasz',
            recipients=('klaudia',),
            trust_level='low',
            author_brief={
                'setting': 'Przystanek w ulewie po godzinach pracy.',
                'speaker_profile': 'Tomasz, 40 lat, spokojny, spostrzegawczy, nienachalny.',
                'recipient_profile': 'Klaudia, 25 lat, zna Tomasza tylko z widzenia w biurowcu.',
            },
            backend='subllm',
        )
        print_pipeline_inspection(live_res.to_dict(), 'TRYB LIVE SUBLLM (subactor/subllm)')


if __name__ == '__main__':
    main()
