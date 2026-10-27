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

__version__ = '0.4.4'
__all__ = ['DialogueEngine', 'Proposal', 'Dialogue', 'Participant', 'Goal', 'Request',
           'Turn', 'Reading', 'CallableJSONBackend', 'ControlledNL', 'EDialogError',
           'NeedsClarification', 'UnsupportedObjective', 'ValidationError', 'BackendError',
           'EMOTION_CODES', 'EmotionLexicon', 'TextAffect', 'TextEmotionAnalyzer',
           'ImageAffect', 'CallableVisionBackend', 'analyze_image', 'FictionRequest',
           'FictionProposal', 'FictionEngine', 'CallableFictionBackend',
           'parse_fiction_request', 'evaluate_annotations', 'OllamaJSON', 'SubLLMJSON']
