"""Offline coverage for injected image adapters and safe Sage parsing."""
import copy
import json
import os
from pathlib import Path
import struct
import tempfile
import unittest
import zlib
from unittest.mock import Mock, patch

from decision_models.contracts import DecisionError
from scripts.image_reference import SageImageAdapter, execute_image


REPO = Path(__file__).resolve().parents[1]
OPTIONS = {
    "visible": "The requested subject is visible in the image.",
    "not_visible": "The requested subject is not visible in the image.",
    "review": "The image does not support a reliable decision.",
}
QUESTION = {"name": "decision", "kind": "choice",
            "instructions": "Use only the supplied image and caption.", "options": OPTIONS}


def png_bytes():
    def chunk(kind, body):
        return (struct.pack(">I", len(body)) + kind + body +
                struct.pack(">I", zlib.crc32(kind + body) & 0xffffffff))
    ihdr = struct.pack(">IIBBBBB", 2, 3, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", zlib.compress(b"\x00" + b"\x10\x20\x30" * 2)) +
            chunk(b"IEND", b""))


def image_config():
    return {"schema_version": 2, "input_modality": "image", "id": "offline-image-review",
            "title": "Review an image", "description": "Bounded image decision.",
            "source_urls": ["https://example.invalid/image-contract"],
            "inspiration": "Test-only.", "limitations": "No action is performed.",
            "required_state_fields": ["content", "image"], "question": copy.deepcopy(QUESTION),
            "policy": {"probability_threshold": 0.8, "review_choice": "review"}}


class FakeVisionAdapter:
    name = "fourth-vision"
    endpoint = "https://vision.example.invalid/decide"
    key_env = "VISION_TEST_KEY"
    default_model = "vision-small-v2"

    def __init__(self, answer="visible"):
        self.answer = answer
        self.build_calls = []

    def build_payload(self, content, questions, model):
        self.build_calls.append((content, questions, model))
        return {"model": model, "image": content["media"], "caption": content["text"],
                "question": questions[0]["instructions"]}

    def parse_response(self, raw, questions):
        return {"model": raw["model"], "answers": {"decision": {
            "kind": "choice", "status": "answered", "choice": self.answer,
            "probability": 0.83,
            "probabilities": {"visible": 0.83, "not_visible": 0.1, "review": 0.07},
            "confidence": None}}, "usage": raw["usage"], "raw_response": raw}


class ImageAdapterExtensionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        # Exercise the copied-skill layout used by the standalone runner.
        self.folder = self.root / "copied-skill"
        self.folder.mkdir()
        (self.folder / "image.json").write_text(json.dumps(image_config()), encoding="utf-8")
        assets = self.folder / "assets"
        assets.mkdir()
        (assets / "sample.png").write_bytes(png_bytes())
        self.data = {"permission_granted": True,
                     "state": {"content": "A neutral caption.", "image": "assets/sample.png"}}

    def tearDown(self):
        self.temp.cleanup()

    def assert_code(self, code, fn, *args, **kwargs):
        with self.assertRaises(DecisionError) as raised:
            fn(*args, **kwargs)
        self.assertEqual(raised.exception.code, code)

    def test_custom_vision_adapter_uses_local_preparation_and_shared_policy(self):
        adapter, raw = FakeVisionAdapter(), {"model": "vision-small-v2", "usage": {"input_tokens": 42}}
        transport = Mock(return_value=raw)
        with patch.dict(os.environ, {"VISION_TEST_KEY": "offline"}, clear=True):
            result = execute_image(self.folder, adapter.name, self.data, mode="live", adapter=adapter,
                                   transport=transport)

        self.assertEqual(result["requested_model"], "vision-small-v2")
        self.assertEqual(result["response"]["usage"], raw["usage"])
        self.assertIs(result["response"]["raw_response"], raw)
        self.assertIsNone(result["response"]["answers"]["decision"]["confidence"])
        self.assertEqual(result["result"]["action"], "recommend")
        self.assertNotIn("confidence", result["result"])
        self.assertEqual(adapter.build_calls[0][2], "vision-small-v2")
        self.assertEqual(adapter.build_calls[0][0]["text"], "A neutral caption.")
        self.assertNotIn("sample.png", json.dumps(transport.call_args.args[1]))
        self.assertNotIn("filename", json.dumps(transport.call_args.args[1]).lower())
        transport.assert_called_once_with(adapter.endpoint, transport.call_args.args[1], "offline", 20)

    def test_custom_model_is_forwarded_but_sage_stays_pinned_without_model_wire_field(self):
        adapter = FakeVisionAdapter()
        transport = Mock(return_value={"model": "custom-selected", "usage": None})
        with patch.dict(os.environ, {"VISION_TEST_KEY": "offline"}, clear=True):
            result = execute_image(self.folder, adapter.name, self.data, mode="live", adapter=adapter,
                                   model="custom-selected", transport=transport)
        self.assertEqual(result["requested_model"], "custom-selected")
        self.assertEqual(adapter.build_calls[0][2], "custom-selected")

        sage = SageImageAdapter()
        payload = sage.build_payload({"kind": "image", "media": "data:image/png;base64,AA==", "text": "caption"},
                                     [QUESTION], sage.default_model)
        self.assertNotIn("model", payload)
        self.assert_code("model_mismatch", sage.build_payload,
                         {"kind": "image", "media": "data:image/png;base64,AA==", "text": "caption"},
                         [QUESTION], "other-model")

    def test_permission_is_checked_before_file_read_and_no_attempt_or_transport(self):
        denied = {"permission_granted": False,
                  "state": {"content": "caption", "image": "assets/sample.png"}}
        adapter = FakeVisionAdapter()
        transport = Mock(side_effect=AssertionError("network must not run"))
        before = Mock(side_effect=AssertionError("attempt must not be reserved"))
        original_open = Path.open

        def guarded_open(path, *args, **kwargs):
            if path.name == "sample.png":
                raise AssertionError("image must not be read without permission")
            return original_open(path, *args, **kwargs)

        with patch.object(Path, "open", guarded_open), patch.dict(os.environ, {}, clear=True):
            result = execute_image(self.folder, adapter.name, denied, mode="live", adapter=adapter,
                                   transport=transport, before_attempt=before)
        self.assertEqual(result["result"]["action"], "deny")
        transport.assert_not_called()
        before.assert_not_called()

    def test_non_finite_custom_payload_fails_before_attempt_reservation_or_transport(self):
        class NonFiniteAdapter(FakeVisionAdapter):
            def build_payload(self, content, questions, model):
                return {"model": model, "invalid": float("nan")}

        adapter = NonFiniteAdapter()
        transport = Mock(side_effect=AssertionError("invalid payload must not reach transport"))
        before = Mock(side_effect=AssertionError("invalid payload must not reserve an attempt"))
        with patch.dict(os.environ, {"VISION_TEST_KEY": "offline"}, clear=True):
            self.assert_code("invalid_request", execute_image, self.folder, adapter.name, self.data,
                             mode="live", adapter=adapter, transport=transport,
                             before_attempt=before)
        transport.assert_not_called()
        before.assert_not_called()

    def test_default_still_rejects_non_sage_provider_without_custom_adapter(self):
        self.assert_code("unsupported_modality", execute_image, self.folder, "fourth-vision", self.data)

    def test_malformed_native_choice_arrays_and_objects_return_structured_invalid_response(self):
        for chosen in ([], {}):
            raw = {
                "meta": {"model": "levanto-sage-v1.4"},
                "results": [{"answers": [{"ok": True, "result": {
                    "id": "decision", "kind": "choice", "meta": {},
                    "result": {"chosen": chosen, "probability": 0.8,
                               "probabilities": [{"option": "visible", "probability": 0.8},
                                                 {"option": "not_visible", "probability": 0.1},
                                                 {"option": "review", "probability": 0.1}]}}}]}],
            }
            with self.subTest(chosen=chosen):
                self.assert_code("invalid_response", SageImageAdapter().parse_response, raw, [QUESTION])

    def test_custom_adapter_canonical_output_is_validated_before_policy(self):
        class BadAdapter(FakeVisionAdapter):
            def parse_response(self, raw, questions):
                response = super().parse_response(raw, questions)
                response["answers"]["decision"]["probabilities"] = {"visible": float("nan")}
                return response

        adapter = BadAdapter()
        with patch.dict(os.environ, {"VISION_TEST_KEY": "offline"}, clear=True):
            self.assert_code("invalid_response", execute_image, self.folder, adapter.name, self.data,
                             mode="live", adapter=adapter,
                             transport=Mock(return_value={"model": adapter.default_model, "usage": None}))


if __name__ == "__main__":
    unittest.main()
