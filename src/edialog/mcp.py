"""Model Context Protocol (MCP) server, registry (wellmanifest.mcp/registry/v1), and DockURI IPC handler for edialog."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import socket
import sys
import time
from typing import Any

from .errors import EDialogError, ValidationError
from .pipeline import (
    PROCESS_CATALOG,
    TRUST_PRESETS,
    build_workflow_dag,
    proc_nl_parse,
    render_uri_call_snippet,
    run_process_pipeline,
    uri,
)


def get_registry_manifest() -> dict[str, Any]:
    """Return the wellmanifest.mcp/registry/v1 manifest describing all edialog URI procedures."""
    operations = []
    for canonical, meta in PROCESS_CATALOG.items():
        operations.append({
            'id': meta['id'],
            'uri': canonical,
            'aliases': list(meta.get('aliases', ())),
            'description': meta['description'],
            'owner': meta['owner'],
            'effect': meta['effect'],
            'inputSchema': {'type': 'object'},
            'outputSchema': {'type': 'object'},
        })
    return {
        'schema': 'wellmanifest.mcp/registry/v1',
        'version': '0.4.4',
        'app': 'edialog',
        'operations': operations,
    }


MCP_TOOLS: list[dict[str, Any]] = [
    {
        'name': 'registry_search',
        'description': 'Przeszukuje rejestr procesów URI edialog (wellmanifest.mcp/registry/v1) po słowach kluczowych lub efekcie.',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'query': {'type': 'string', 'description': 'Fraza wyszukiwania (np. "parse", "affect", "pipeline", "replay")'},
                'effect': {'type': 'string', 'enum': ['pure', 'read', 'write']},
            },
        },
    },
    {
        'name': 'task_plan',
        'description': 'Buduje deklaratywny plan wykonania potoku (dockuri/workflow-v1) oraz kanoniczny Action URI na podstawie instrukcji NL lub poziomu zaufania.',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'actor': {'type': 'string'},
                'recipients': {'type': 'array', 'items': {'type': 'string'}},
                'instruction': {'type': 'string'},
                'trust_level': {'type': 'string', 'enum': ['zero', 'low', 'high', 'rebuilding']},
                'author_brief': {'type': 'object'},
                'backend': {'type': 'string'},
            },
            'required': ['actor', 'recipients'],
        },
    },
    {
        'name': 'task_execute',
        'description': 'Wykonuje pełny 6-etapowy potok procesowy edialog z transparentnym śladem każdego kroku, kwitem CompositeExecutionReceipt, logami i raportem.',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'dialogue': {'type': 'object'},
                'actor': {'type': 'string'},
                'recipients': {'type': 'array', 'items': {'type': 'string'}},
                'instruction': {'type': 'string'},
                'request': {'type': 'object'},
                'trust_level': {'type': 'string', 'enum': ['zero', 'low', 'high', 'rebuilding']},
                'author_brief': {'type': 'object'},
                'candidates': {'type': 'array', 'items': {'type': 'string'}},
                'backend': {},
            },
            'required': ['dialogue', 'actor', 'recipients'],
        },
    },
    {
        'name': 'task_status',
        'description': 'Pobiera zapisany status, ślad procesów, kwit i raport dla wykonanego zadania po pipeline_id.',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'pipeline_id': {'type': 'string'},
            },
            'required': ['pipeline_id'],
        },
    },
    {
        'name': 'edialog_pipeline_run',
        'description': 'Bezpośrednie uruchomienie 6-etapowego potoku edialog (NL -> Context -> Candidates -> Affect Score -> DSL -> Report).',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'dialogue': {'type': 'object'},
                'actor': {'type': 'string'},
                'recipients': {'type': 'array', 'items': {'type': 'string'}},
                'instruction': {'type': 'string'},
                'request': {'type': 'object'},
                'trust_level': {'type': 'string', 'enum': ['zero', 'low', 'high', 'rebuilding']},
                'author_brief': {'type': 'object'},
                'candidates': {'type': 'array', 'items': {'type': 'string'}},
                'backend': {},
            },
            'required': ['dialogue', 'actor', 'recipients'],
        },
    },
    {
        'name': 'edialog_uri_call',
        'description': 'Wywołuje dowolny pojedynczy proces URI (np. proc://edialog/nl/parse/v1, proc://edialog/affect/score/v1) zgodnie z kontraktem DOCK-URI-001.',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'uri': {'type': 'string'},
                'payload': {'type': 'object'},
            },
            'required': ['uri'],
        },
    },
    {
        'name': 'edialog_explain_architecture',
        'description': 'Zwraca przejrzysty opis architektury procesowej edialog, listę 6 procesów potoku, presety zaufania oraz wzorce reużycia.',
        'inputSchema': {
            'type': 'object',
            'properties': {},
        },
    },
]


class EDialogMCPServer:
    """In-memory and stdio MCP + DockURI server for edialog."""

    def __init__(self) -> None:
        self._tasks: dict[str, dict[str, Any]] = {}
        self._started_at = time.time()

    def search_registry(self, query: str = '', *, effect: str | None = None) -> dict[str, Any]:
        q = query.strip().lower()
        matches = []
        for op in get_registry_manifest()['operations']:
            if effect and op['effect'] != effect:
                continue
            haystack = f"{op['id']} {op['uri']} {' '.join(op['aliases'])} {op['description']}".lower()
            if not q or q in haystack:
                matches.append(op)
        return {
            'schema': 'wellmanifest.mcp/search-result/v1',
            'query': query,
            'effect_filter': effect,
            'count': len(matches),
            'operations': matches,
        }

    def plan_task(self, arguments: dict[str, Any]) -> dict[str, Any]:
        parsed = proc_nl_parse({
            'actor': arguments['actor'],
            'recipients': arguments['recipients'],
            'instruction': arguments.get('instruction'),
            'request': arguments.get('request'),
            'trust_level': arguments.get('trust_level'),
            'author_brief': arguments.get('author_brief'),
            'backend': arguments.get('backend', 'offline'),
        })
        dag = build_workflow_dag()
        return {
            'schema': 'wellmanifest.nl-plan/v1',
            'status': 'planned',
            'action_uri': parsed['action_uri'],
            'parse_mode': parsed['parse_mode'],
            'resolved_request': parsed['request'],
            'effective_brief': parsed['effective_brief'],
            'workflow_dag': dag,
            'reuse_snippet': render_uri_call_snippet('proc://edialog/pipeline/run/v1', arguments, lang='python'),
        }

    def execute_task(self, arguments: dict[str, Any]) -> dict[str, Any]:
        res = run_process_pipeline(
            arguments['dialogue'],
            actor=arguments['actor'],
            recipients=arguments['recipients'],
            instruction=arguments.get('instruction'),
            request=arguments.get('request'),
            trust_level=arguments.get('trust_level'),
            author_brief=arguments.get('author_brief'),
            candidates=arguments.get('candidates'),
            backend=arguments.get('backend'),
            image=arguments.get('image'),
            retention=float(arguments.get('retention', 0.55)),
            image_weight=float(arguments.get('image_weight', 0.35)),
        )
        data = res.to_dict()
        self._tasks[res.pipeline_id] = data
        return data

    def get_task_status(self, pipeline_id: str) -> dict[str, Any]:
        if pipeline_id not in self._tasks:
            raise ValidationError(f'Unknown pipeline_id: {pipeline_id}')
        stored = self._tasks[pipeline_id]
        return {
            'pipeline_id': pipeline_id,
            'status': stored['receipt']['status'],
            'action_uri': stored['action_uri'],
            'winner_text': stored['proposal']['text'],
            'receipt': stored['receipt'],
            'report': stored['report'],
        }

    def explain_architecture(self) -> dict[str, Any]:
        return {
            'app': 'edialog',
            'version': '0.4.4',
            'architecture': 'Tripartite NL -> Action URI -> Reproducible DSL + 6-Stage Process Pipeline',
            'standards_applied': [
                'wellmanifest/nl-api-llm',
                'wellmanifest/nl-dsl-llm',
                'wellmanifest/nl-uri-dsl-llm',
                'wellmanifest/mcp',
                'wellmanifest/dockuri',
                'wellmanifest/logs',
                'wellmanifest/report',
                'wellmanifest/docs',
                'wellmanifest/wellman',
            ],
            'pipeline_stages': [
                {
                    'step': idx + 1,
                    'id': stage['id'],
                    'uri': stage['uri'],
                    'depends_on': stage.get('depends_on', []),
                    'description': PROCESS_CATALOG[stage['uri']]['description'],
                }
                for idx, stage in enumerate(build_workflow_dag()['flow'])
            ],
            'trust_presets': {
                k: {
                    'label': v['label'],
                    'target': v['target'],
                    'strategies': list(v['strategies']),
                    'boundary_rules': list(v['boundary_rules']),
                }
                for k, v in TRUST_PRESETS.items()
            },
            'reuse_examples': {
                'python_one_liner': render_uri_call_snippet('proc://edialog/pipeline/run/v1', lang='python'),
                'cli_one_liner': render_uri_call_snippet('proc://edialog/pipeline/run/v1', lang='bash'),
                'mcp_rpc_call': json.loads(render_uri_call_snippet('proc://edialog/pipeline/run/v1', lang='mcp')),
            },
        }

    def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        args = dict(arguments or {})
        if name == 'registry_search':
            return self.search_registry(args.get('query', ''), effect=args.get('effect'))
        if name == 'task_plan':
            return self.plan_task(args)
        if name in ('task_execute', 'edialog_pipeline_run'):
            return self.execute_task(args)
        if name == 'task_status':
            return self.get_task_status(args['pipeline_id'])
        if name == 'edialog_uri_call':
            out = uri(args['uri'], args.get('payload'))
            return out if isinstance(out, dict) else {'items': out}
        if name == 'edialog_explain_architecture':
            return self.explain_architecture()
        raise ValidationError(f'Unknown MCP tool: {name}')

    def handle_rpc(self, request: dict[str, Any]) -> dict[str, Any]:
        """Handle a single JSON-RPC 2.0 MCP request."""
        req_id = request.get('id')
        method = request.get('method')
        params = request.get('params') or {}

        try:
            if method == 'initialize':
                result = {
                    'protocolVersion': '2024-11-05',
                    'serverInfo': {'name': 'edialog-mcp', 'version': '0.4.4'},
                    'capabilities': {'tools': {}, 'resources': {}},
                }
            elif method == 'ping':
                result = {'status': 'pong'}
            elif method == 'tools/list':
                result = {'tools': MCP_TOOLS}
            elif method == 'tools/call':
                tool_name = params.get('name', '')
                tool_args = params.get('arguments') or {}
                payload = self.call_tool(tool_name, tool_args)
                result = {
                    'content': [{'type': 'text', 'text': json.dumps(payload, ensure_ascii=False, indent=2)}],
                    'structuredContent': payload,
                    'isError': False,
                }
            elif method == 'resources/list':
                result = {
                    'resources': [
                        {
                            'uri': 'edialog://registry/v1',
                            'name': 'Rejestr procesów URI edialog',
                            'mimeType': 'application/json',
                        },
                        {
                            'uri': 'edialog://workflow/v1',
                            'name': 'Graf przepływu danych dockuri/workflow-v1',
                            'mimeType': 'application/json',
                        },
                    ]
                }
            elif method == 'resources/read':
                res_uri = params.get('uri')
                if res_uri == 'edialog://registry/v1':
                    body = get_registry_manifest()
                elif res_uri == 'edialog://workflow/v1':
                    body = build_workflow_dag()
                else:
                    raise ValidationError(f'Unknown resource URI: {res_uri}')
                result = {
                    'contents': [
                        {
                            'uri': res_uri,
                            'mimeType': 'application/json',
                            'text': json.dumps(body, ensure_ascii=False, indent=2),
                        }
                    ]
                }
            else:
                return {
                    'jsonrpc': '2.0',
                    'id': req_id,
                    'error': {'code': -32601, 'message': f'Method not found: {method}'},
                }
            return {'jsonrpc': '2.0', 'id': req_id, 'result': result}
        except EDialogError as exc:
            return {
                'jsonrpc': '2.0',
                'id': req_id,
                'error': {'code': -32000, 'message': str(exc), 'data': {'type': type(exc).__name__}},
            }

    def handle_dockuri_frame(self, frame: dict[str, Any]) -> dict[str, Any]:
        """Handle a DockURI NDJSON IPC frame (DOCK-IPC-001)."""
        req_id = frame.get('id', 'req-0')
        proc = frame.get('proc', '')
        args = frame.get('args') or {}
        t0 = time.perf_counter()
        try:
            if proc == '__ping__':
                res = {
                    'status': 'pong',
                    'runtime': f'cpython-{sys.version_info.major}.{sys.version_info.minor}',
                    'uptime_s': round(time.time() - self._started_at, 3),
                }
            else:
                res = uri(proc, args)
            duration_us = int((time.perf_counter() - t0) * 1_000_000)
            return {
                'id': req_id,
                'ok': True,
                'result': res,
                'error': None,
                'metrics': {'duration_us': duration_us},
            }
        except Exception as exc:
            duration_us = int((time.perf_counter() - t0) * 1_000_000)
            return {
                'id': req_id,
                'ok': False,
                'result': None,
                'error': {'type': type(exc).__name__, 'message': str(exc)},
                'metrics': {'duration_us': duration_us},
            }

    def serve_uds(self, socket_path: str | Path | None = None, *, max_requests: int | None = None) -> None:
        """Listen on a Unix Domain Socket (DOCK-UDS-001) and process NDJSON IPC frames."""
        if socket_path is None:
            env_sock = os.environ.get('DOCKURI_SOCKET')
            run_dir = os.environ.get('DOCKURI_RUN_DIR')
            if env_sock:
                sock_file = Path(env_sock).expanduser()
            elif run_dir:
                sock_file = Path(run_dir).expanduser() / 'edialog.sock'
            else:
                sock_file = Path.home() / '.dockuri' / 'run' / 'edialog.sock'
        else:
            sock_file = Path(socket_path).expanduser()

        sock_file.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if sock_file.exists():
            sock_file.unlink()

        srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        srv.bind(str(sock_file))
        os.chmod(sock_file, 0o600)
        srv.listen(16)
        handled = 0
        try:
            while max_requests is None or handled < max_requests:
                conn, _ = srv.accept()
                try:
                    raw = conn.recv(65536)
                    if raw:
                        frame = json.loads(raw.decode('utf-8').strip())
                        resp = self.handle_dockuri_frame(frame)
                        conn.sendall((json.dumps(resp, ensure_ascii=False) + '\n').encode('utf-8'))
                        handled += 1
                finally:
                    conn.close()
        finally:
            srv.close()
            if sock_file.exists():
                sock_file.unlink()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog='edialog-mcp',
        description='MCP server and DockURI process CLI for edialog.',
    )
    sub = parser.add_subparsers(dest='command')

    sub.add_parser('serve', help='Uruchom serwer JSON-RPC 2.0 MCP na stdin/stdout.')
    daemon_p = sub.add_parser('daemon', help='Uruchom demona gniazda UDS DockURI (DOCK-UDS-001).')
    daemon_p.add_argument('--socket', default=None, help='Ścieżka do gniazda UDS (domyślnie ~/.dockuri/run/edialog.sock)')
    daemon_p.add_argument('--max-requests', type=int, default=None, help='Opcjonalny limit żądań przed zamknięciem')
    sub.add_parser('registry', help='Wypisz manifest rejestru wellmanifest.mcp/registry/v1.')
    sub.add_parser('explain', help='Wypisz opis 6-etapowej architektury procesowej i wzorce reużycia.')

    uri_p = sub.add_parser('uri', help='Wywołaj dowolny proces URI (DOCK-URI-001).')
    uri_p.add_argument('address', help='Kanoniczny adres URI, np. proc://edialog/pipeline/run/v1')
    uri_p.add_argument('payload', nargs='?', default='{}', help='Ładunek JSON lub "-" dla stdin')

    args = parser.parse_args(argv)
    server = EDialogMCPServer()

    if args.command in (None, 'explain'):
        print(json.dumps(server.explain_architecture(), ensure_ascii=False, indent=2))
        return 0
    if args.command == 'registry':
        print(json.dumps(get_registry_manifest(), ensure_ascii=False, indent=2))
        return 0
    if args.command == 'uri':
        raw = sys.stdin.read() if args.payload == '-' else args.payload
        out = uri(args.address, raw)
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0
    if args.command == 'daemon':
        server.serve_uds(args.socket, max_requests=args.max_requests)
        return 0
    if args.command == 'serve':
        for line in sys.stdin:
            stripped = line.strip()
            if not stripped:
                continue
            req = json.loads(stripped)
            if 'jsonrpc' in req:
                resp = server.handle_rpc(req)
            else:
                resp = server.handle_dockuri_frame(req)
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + '\n')
            sys.stdout.flush()
        return 0
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
