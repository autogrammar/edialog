"""Tests for the 6-stage process pipeline, DockURI uri() contract, and MCP server."""
from __future__ import annotations

import json
import pytest

from edialog import (
     PROCESS_CATALOG,
    TRUST_PRESETS,
    Dialogue,
    EDialogMCPServer,
    Participant,
    ValidationError,
    build_workflow_dag,
    get_registry_manifest,
    render_uri_call_snippet,
    run_process_pipeline,
    uri,
    uri_jsonl,
)


def _sample_dialogue() -> Dialogue:
    d = Dialogue([
        Participant('tomasz', 'Tomasz'),
        Participant('klaudia', 'Klaudia'),
        Participant('marek', 'Marek'),
    ])
    d.add_turn('marek', 'Prywatna notatka tylko dla Tomasza.', recipients=('tomasz',))
    d.add_turn('klaudia', 'Znamy się z czwartego piętra?', recipients=('tomasz',))
    return d


def test_registry_manifest_and_workflow_dag():
    reg = get_registry_manifest()
    assert reg['schema'] == 'wellmanifest.mcp/registry/v1'
    assert reg['app'] == 'edialog'
    uris = {op['uri'] for op in reg['operations']}
    assert 'proc://edialog/pipeline/run/v1' in uris
    assert 'proc://edialog/nl/parse/v1' in uris
    assert 'proc://edialog/affect/score/v1' in uris

    dag = build_workflow_dag()
    assert dag['$schema'] == 'https://wellmanifest.org/schemas/dockuri-pipeline-v1.json'
    assert len(dag['flow']) == 6
    assert [step['id'] for step in dag['flow']] == [
        'step1_nl_parse',
        'step2_context_filter',
        'step3_candidates_generate',
        'step4_affect_score',
        'step5_dsl_compile',
        'step6_report_emit',
    ]


def test_run_process_pipeline_transparency_and_receipt():
    dlg = _sample_dialogue()
    res = run_process_pipeline(
        dlg,
        actor='tomasz',
        recipients=('klaudia',),
        trust_level='low',
    )
    data = res.to_dict()
    assert data['action_uri'].startswith('proc://edialog/fiction/generate/v1?')
    assert 'trust=low' in data['action_uri']
    assert len(data['steps']) == 6

    # Check step 2 filtered out Marek's private turn
    step2 = data['steps'][1]
    assert step2['uri'] == 'proc://edialog/context/filter/v1'
    assert step2['output_summary']['visible_turn_count'] == 1
    assert step2['output_summary']['hidden_turn_count'] == 1

    # Check step 4 ranking table is populated and sorted by rank_loss
    step4 = data['steps'][3]
    table = step4['output_summary']['ranking_table']
    assert len(table) >= 2
    losses = [row['rank_loss'] for row in table]
    assert losses == sorted(losses)
    assert table[0]['text'] == data['proposal']['text']

    # Check step 5 verified deterministic replay
    step5 = data['steps'][4]
    assert step5['output_summary']['replay_verified'] is True

    # Check CompositeExecutionReceipt and hash-chained logs
    receipt = data['receipt']
    assert receipt['schema'] == 'wellmanifest.wellman/receipt/v1'
    assert receipt['status'] == 'completed'
    assert receipt['executed'] is True
    assert len(receipt['steps']) == 6

    events = data['event_log']
    assert len(events) == 6
    prev = '0' * 64
    for ev in events:
        assert ev['prev_hash'] == prev
        prev = ev['event_hash']
    assert receipt['chain_root_sha256'] == prev


def test_uri_and_uri_jsonl_contracts():
    dlg = _sample_dialogue()

    # Ping
    ping = uri('__ping__')
    assert ping['status'] == 'pong'
    assert ping['executed'] is True

    # Individual stage via uri()
    parsed = uri(
        'proc://edialog/nl/parse/v1?actor=tomasz&to=klaudia&trust=zero',
        {'instruction': 'Neutralna obserwacja bez narzucania się.'},
    )
    assert parsed['trust_level'] == 'zero'
    assert parsed['request']['target'] == TRUST_PRESETS['zero']['target']

    # Batch JSONL stream via uri_jsonl()
    batch = uri_jsonl(
        'proc://edialog/nl/parse/v1',
        [
            json.dumps({'actor': 'tomasz', 'recipients': ['klaudia'], 'trust_level': 'low'}),
            json.dumps({'actor': 'tomasz', 'recipients': ['klaudia'], 'trust_level': 'high'}),
        ],
    )
    assert len(batch) == 2
    assert batch[0]['trust_level'] == 'low'
    assert batch[1]['trust_level'] == 'high'

    # Replay & continue_scene via uri()
    pipe_out = uri(
        'proc://edialog/pipeline/run/v1',
        {'dialogue': dlg.to_dict(), 'actor': 'tomasz', 'recipients': ['klaudia'], 'trust_level': 'low'},
    )
    replayed = uri(
        'proc://edialog/dsl/replay/v1',
        {'dialogue': dlg.to_dict(), 'dsl': pipe_out['proposal']['dsl'], 'continue_scene': True},
    )
    assert replayed['replayed_equal'] is True
    assert len(replayed['continued_dialogue']['turns']) == len(dlg.turns) + 1

    # Unknown URI raises ValidationError with NO_MATCHING_PROCEDURE
    with pytest.raises(ValidationError, match='NO_MATCHING_PROCEDURE'):
        uri('proc://edialog/unknown/action/v1', {})


def test_mcp_server_jsonrpc_and_dockuri_frames():
    dlg = _sample_dialogue()
    server = EDialogMCPServer()

    init_resp = server.handle_rpc({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize'})
    assert init_resp['result']['serverInfo']['name'] == 'edialog-mcp'

    tools_resp = server.handle_rpc({'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list'})
    tool_names = {t['name'] for t in tools_resp['result']['tools']}
    assert {'registry_search', 'task_plan', 'task_execute', 'task_status', 'edialog_pipeline_run', 'edialog_uri_call'} <= tool_names

    exec_resp = server.handle_rpc({
        'jsonrpc': '2.0',
        'id': 3,
        'method': 'tools/call',
        'params': {
            'name': 'task_execute',
            'arguments': {
                'dialogue': dlg.to_dict(),
                'actor': 'tomasz',
                'recipients': ['klaudia'],
                'trust_level': 'rebuilding',
            },
        },
    })
    executed = exec_resp['result']['structuredContent']
    pipeline_id = executed['pipeline_id']

    status_resp = server.handle_rpc({
        'jsonrpc': '2.0',
        'id': 4,
        'method': 'tools/call',
        'params': {'name': 'task_status', 'arguments': {'pipeline_id': pipeline_id}},
    })
    assert status_resp['result']['structuredContent']['status'] == 'completed'
    assert status_resp['result']['structuredContent']['winner_text'] == executed['proposal']['text']

    # DockURI NDJSON IPC frame
    frame_resp = server.handle_dockuri_frame({'id': 'req-42', 'proc': '__ping__', 'args': {}})
    assert frame_resp['ok'] is True
    assert frame_resp['result']['status'] == 'pong'
    assert 'duration_us' in frame_resp['metrics']

    snippet = render_uri_call_snippet('proc://edialog/pipeline/run/v1', lang='python')
    assert 'from edialog import uri' in snippet
