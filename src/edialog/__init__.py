"""edialog: explicit NL plans, multi-party drafts, and illustrative simulations."""
from .engine import DialogueEngine, Proposal
from .errors import EDialogError, BackendError, NeedsClarification, UnsupportedObjective, ValidationError
from .models import Dialogue, Goal, Participant, Reading, Request, Turn
from .nl import CallableJSONBackend, ControlledNL
from .affect import EMOTION_CODES, EmotionLexicon, TextAffect, TextEmotionAnalyzer
from .vision import ImageAffect, CallableVisionBackend, analyze_image
from .fiction import (FictionRequest, FictionProposal, FictionEngine, CallableFictionBackend,
                      parse_fiction_request, evaluate_annotations)
from .backends import OllamaJSON, SubLLMJSON
from .pipeline import (
    PROCESS_CATALOG,
    TRUST_PRESETS,
    ProcessPipelineResult,
    ProcessStepTrace,
    analyze_and_respond_turn,
    build_workflow_dag,
    dispatch_probe,
    render_analytical_ascii_diagram,
    render_uri_call_snippet,
    run_process_pipeline,
    uri,
    uri_jsonl,
)
from .mcp import EDialogMCPServer, get_registry_manifest

__version__ = '0.4.5'
__all__ = ['DialogueEngine', 'Proposal', 'Dialogue', 'Participant', 'Goal', 'Request',
           'Turn', 'Reading', 'CallableJSONBackend', 'ControlledNL', 'EDialogError',
           'NeedsClarification', 'UnsupportedObjective', 'ValidationError', 'BackendError',
           'EMOTION_CODES', 'EmotionLexicon', 'TextAffect', 'TextEmotionAnalyzer',
           'ImageAffect', 'CallableVisionBackend', 'analyze_image', 'FictionRequest',
           'FictionProposal', 'FictionEngine', 'CallableFictionBackend',
           'parse_fiction_request', 'evaluate_annotations', 'OllamaJSON', 'SubLLMJSON',
           'PROCESS_CATALOG', 'TRUST_PRESETS', 'ProcessStepTrace', 'ProcessPipelineResult',
           'analyze_and_respond_turn', 'build_workflow_dag', 'dispatch_probe',
           'render_analytical_ascii_diagram', 'run_process_pipeline', 'uri', 'uri_jsonl',
           'render_uri_call_snippet', 'EDialogMCPServer', 'get_registry_manifest']
