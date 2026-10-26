import json
import types
import sys
import unittest
from unittest.mock import MagicMock, patch

from edialog import SubLLMJSON, ValidationError, BackendError
from edialog.fiction import CallableFictionBackend, FictionEngine, FictionRequest
from edialog.models import Dialogue, Participant


class TestSubLLMJSON(unittest.TestCase):
    def test_validation(self):
        with self.assertRaises(ValidationError):
            SubLLMJSON(timeout=0)
        with self.assertRaises(ValidationError):
            SubLLMJSON(timeout=500)
        with self.assertRaises(ValidationError):
            SubLLMJSON(application="")

    def test_requires_response_schema(self):
        transport = SubLLMJSON(application="autogrammar-edialog", function="dialogue")
        with self.assertRaises(BackendError):
            transport({"task": "test"})

    def test_missing_subllm_import(self):
        transport = SubLLMJSON()
        with patch.dict(sys.modules, {"subllm": None}):
            with self.assertRaises(BackendError) as ctx:
                transport({"response_schema": {"type": "object"}})
            self.assertIn("subactor-subllm is not installed", str(ctx.exception))

    def test_successful_subllm_call(self):
        fake_response = MagicMock()
        fake_response.content = json.dumps({
            "target": {"scared": 0.8},
            "strategies": ["suspense"]
        })
        fake_response.model = "test-model"

        mock_module = types.ModuleType("subllm")
        mock_module.complete = MagicMock(return_value=fake_response)

        with patch.dict(sys.modules, {"subllm": mock_module}):
            transport = SubLLMJSON(application="autogrammar-edialog", function="dialogue")
            res = transport({
                "task": "parse_fiction_request",
                "response_schema": {"type": "object"}
            })
            self.assertEqual(res["target"], {"scared": 0.8})
            self.assertEqual(res["strategies"], ["suspense"])
            mock_module.complete.assert_called_once()
            args, kwargs = mock_module.complete.call_args
            self.assertEqual(args[0], "autogrammar-edialog")
            self.assertEqual(args[1], "dialogue")
            self.assertEqual(kwargs["response_format"], {"type": "json_object"})

    def test_subllm_with_markdown_fences(self):
        fake_response = MagicMock()
        fake_response.content = "```json\n{\"candidates\": [{\"text\": \"Ktoś idzie!\", \"evidence_turn_ids\": [\"t1\"]}]}\n```"

        mock_module = types.ModuleType("subllm")
        mock_module.complete = MagicMock(return_value=fake_response)

        with patch.dict(sys.modules, {"subllm": mock_module}):
            transport = SubLLMJSON()
            res = transport({
                "task": "generate_fiction_candidates",
                "response_schema": {"type": "object"}
            })
            self.assertEqual(len(res["candidates"]), 1)
            self.assertEqual(res["candidates"][0]["text"], "Ktoś idzie!")

    def test_fiction_engine_with_subllm_backend(self):
        fake_response = MagicMock()
        fake_response.content = json.dumps({
            "candidates": [
                {"text": "Nie otwieraj tych drzwi.", "evidence_turn_ids": ["t1"]},
                {"text": "Słyszałem ten sam dźwięk wczoraj.", "evidence_turn_ids": ["t1"]}
            ]
        })

        mock_module = types.ModuleType("subllm")
        mock_module.complete = MagicMock(return_value=fake_response)

        with patch.dict(sys.modules, {"subllm": mock_module}):
            transport = SubLLMJSON(application="autogrammar-tillm", function="invoke")
            backend = CallableFictionBackend(transport)
            engine = FictionEngine(backend=backend)

            d = Dialogue((Participant("anna", "Anna"), Participant("jan", "Jan")))
            d.add_turn("anna", "Słyszysz te kroki?", turn_id="t1")

            proposal = engine.generate(
                d,
                actor="jan",
                recipients=("anna",),
                request=FictionRequest(strategies=("suspense",))
            )
            self.assertIsNotNone(proposal.text)
            self.assertEqual(len(proposal.candidates), 2)
            self.assertIn("Nie otwieraj", proposal.text)


if __name__ == '__main__':
    unittest.main()
