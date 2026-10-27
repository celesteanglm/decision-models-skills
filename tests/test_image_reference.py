"""Offline image modality contracts for the portable Sage reference runner."""
import base64
import copy
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from unittest.mock import Mock, patch

from decision_models.contracts import DecisionError
from decision_models.use_cases import load_use_case
from scripts.image_reference import (
    SageImageAdapter,
    execute_image,
    load_config,
    prepare_image,
)


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "image_reference.py"
OPTIONS = {
    "visible": "The requested subject is visible in the image.",
    "not_visible": "The requested subject is not visible in the image.",
    "review": "The image does not support a reliable decision.",
}
QUESTION = {
    "name": "decision",
    "kind": "choice",
    "instructions": "Use only the supplied image and caption.",
    "options": OPTIONS,
}
QUESTIONS = [
    {"name": "is_present", "kind": "predicate", "instructions": "Is the marked item present?",
     "criteria": {"true": "Present means visible.", "false": "Absent means not visible."}},
    QUESTION,
    {"name": "severity", "kind": "score", "instructions": "Rate severity.",
     "levels": ["none", "mild", "high"]},
]


def image_config():
    return {
        "schema_version": 2,
        "input_modality": "image",
        "id": "offline-image-review",
        "title": "Review an image",
        "description": "A bounded image decision for offline contract coverage.",
        "source_urls": ["https://example.invalid/image-contract"],
        "inspiration": "Test-only image skill.",
        "limitations": "No action is performed.",
        "required_state_fields": ["content", "image"],
        "question": copy.deepcopy(QUESTION),
        "policy": {"probability_threshold": 0.8, "review_choice": "review"},
    }


def png_bytes(width=2, height=3, *, corrupt_crc=False):
    """Build a small structurally valid PNG using only stdlib CRC support."""
    def chunk(kind, body):
        crc = zlib.crc32(kind + body) & 0xffffffff
        if corrupt_crc and kind == b"IHDR":
            crc ^= 1
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    # A single filtered RGB row; enough to exercise the local structural parser.
    pixels = b"\x00" + b"\x10\x20\x30" * width
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", zlib.compress(pixels)) + chunk(b"IEND", b""))


def jpeg_bytes(width=2, height=3):
    # SOF0 frame header with one component, followed by EOI.
    frame = bytes([8]) + struct.pack(">HH", height, width) + bytes([1, 1, 0x11, 0])
    return b"\xff\xd8\xff\xc0" + struct.pack(">H", len(frame) + 2) + frame + b"\xff\xd9"


def webp_bytes(width=2, height=3):
    # Lossless VP8L header. Packed dimensions are width-1 and height-1.
    packed_width, packed_height = width - 1, height - 1
    b1 = packed_width & 0xff
    b2 = ((packed_width >> 8) & 0x3f) | ((packed_height & 0x3) << 6)
    b3 = (packed_height >> 2) & 0xff
    b4 = 0
    body = bytes([0x2f, b1, b2, b3, b4, 0, 0, 0, 0, 0, 0])
    chunk = b"VP8L" + struct.pack("<I", len(body)) + body
    riff_body = b"WEBP" + chunk
    return b"RIFF" + struct.pack("<I", len(riff_body)) + riff_body


def native_raw(*, choice="visible", probability=0.82, model="levanto-sage-v1.4",
               kind="choice", usage=None):
    choice_dist = [
        {"option": "visible", "probability": probability if choice == "visible" else 0.1},
        {"option": "not_visible", "probability": probability if choice == "not_visible" else 0.1},
        {"option": "review", "probability": probability if choice == "review" else 0.1},
    ]
    # Normalize while retaining the selected probability exactly.
    other = (1 - probability) / 2
    for row in choice_dist:
        if row["option"] == choice:
            row["probability"] = probability
        else:
            row["probability"] = other
    answers = [
        {"ok": True, "result": {"id": "is_present", "kind": "yesno",
         "result": {"answer": "yes", "probability": 0.9}, "meta": {"model": model}}},
        {"ok": True, "result": {"id": "decision", "kind": kind,
         "result": {"chosen": choice, "probability": probability,
                     "probabilities": choice_dist}, "meta": {"model": model}}},
        {"ok": True, "result": {"id": "severity", "kind": "scale",
         "result": {"expectation": 1.25, "confidence": 0.7,
                     "probabilities": [{"level": 0, "probability": 0.1},
                                      {"level": 1, "probability": 0.55},
                                      {"level": 2, "probability": 0.35}]},
         "meta": {"model": model}}},
    ]
    return {"results": [{"answers": answers}],
            "meta": {"model": model, "usage": usage or {"input_tokens": 83, "output_tokens": 12}}}


class ImageReferenceFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.folder = self.root / "skill"
        self.folder.mkdir()
        (self.folder / "image.json").write_text(json.dumps(image_config()), encoding="utf-8")
        self.asset = self.folder / "assets" / "sample.png"
        self.asset.parent.mkdir()
        self.asset.write_bytes(png_bytes())
        self.data = {"permission_granted": True,
                     "state": {"content": "A neutral caption for this image.",
                               "image": "assets/sample.png"}}

    def tearDown(self):
        self.temp.cleanup()

    def assert_code(self, code, fn, *args, **kwargs):
        with self.assertRaises(DecisionError) as raised:
            fn(*args, **kwargs)
        self.assertEqual(raised.exception.code, code)


class SageNativeImageAdapterTests(ImageReferenceFixture):
    def test_exact_native_batch_payload_uses_schema_mapping_and_one_image_group(self):
        image_content = {"kind": "image", "media": "data:image/png;base64,AA==", "text": "caption"}
        payload = SageImageAdapter().build_payload(image_content, QUESTIONS)
        self.assertEqual(payload, {
            "reasoning": "off", "latency_mode": "quality",
            "requests": [{"content": image_content, "questions": [
                {"kind": "yesno", "id": "is_present",
                 "instructions": "Is the marked item present? Interpret yes as: Present means visible. Interpret no as: Absent means not visible."},
                {"kind": "choice", "id": "decision",
                 "instructions": QUESTION["instructions"],
                 "options": [{"option": key, "description": value} for key, value in OPTIONS.items()]},
                {"kind": "scale", "id": "severity", "instructions": "Rate severity.",
                 "levels": [{"level": 0, "description": "none"},
                            {"level": 1, "description": "mild"},
                            {"level": 2, "description": "high"}],
                },
            ]}],
        })
        encoded = json.dumps(payload)
        for forbidden in ("model", "expected", "filename", "sample.png", "oracle"):
            self.assertNotIn(forbidden, encoded)

    def test_sage_refuses_injected_model_field(self):
        with self.assertRaises(DecisionError):
            SageImageAdapter().build_payload({"kind": "image", "media": "data:image/png;base64,AA=="}, QUESTIONS,
                                              model="unrelated-model")

    def test_nested_native_answers_preserve_distributions_usage_and_absent_confidence(self):
        usage = {"input_tokens": 83, "output_tokens": 12, "total_tokens": 95}
        raw = native_raw(usage=usage)
        result = SageImageAdapter().parse_response(raw, QUESTIONS)
        self.assertEqual(result["model"], "levanto-sage-v1.4")
        self.assertEqual(result["usage"], usage)
        self.assertEqual(result["raw_response"], raw)
        self.assertEqual(result["answers"]["decision"]["choice"], "visible")
        self.assertEqual(result["answers"]["decision"]["probability"], 0.82)
        probabilities = result["answers"]["decision"]["probabilities"]
        self.assertEqual(probabilities["visible"], 0.82)
        self.assertAlmostEqual(probabilities["not_visible"], 0.09)
        self.assertAlmostEqual(probabilities["review"], 0.09)
        self.assertIsNone(result["answers"]["decision"]["confidence"])
        self.assertEqual(result["answers"]["severity"]["probabilities"],
                         {"0": 0.1, "1": 0.55, "2": 0.35})
        self.assertEqual(result["answers"]["severity"]["score"], 1.25)
        self.assertEqual(sum(result["answers"]["decision"]["probabilities"].values()), 1)
        weighted = sum(int(level) * p for level, p in result["answers"]["severity"]["probabilities"].items())
        self.assertAlmostEqual(weighted, result["answers"]["severity"]["score"])

    def test_choice_native_probability_must_match_chosen_distribution_probability(self):
        raw = native_raw(probability=0.81)
        native = raw["results"][0]["answers"][1]["result"]["result"]
        native["probabilities"] = [
            {"option": "visible", "probability": 0.79},
            {"option": "not_visible", "probability": 0.105},
            {"option": "review", "probability": 0.105},
        ]
        self.assert_code("invalid_response", SageImageAdapter().parse_response, raw, QUESTIONS)

    def test_missing_choice_confidence_is_not_fabricated_and_confidence_is_not_a_gate(self):
        config = load_config(self.folder)
        raw = native_raw(probability=0.8)
        raw["results"][0]["answers"] = [raw["results"][0]["answers"][1]]
        transport = Mock(return_value=raw)
        with patch.dict(os.environ, {"SAGE_API_KEY": "offline"}, clear=True):
            result = execute_image(self.folder, "sage", self.data, mode="live", transport=transport)
        self.assertIsNone(result["response"]["answers"]["decision"]["confidence"])
        self.assertEqual(result["result"]["action"], "recommend")
        self.assertEqual(result["result"]["selected_probability"], config["policy"]["probability_threshold"])
        self.assertNotIn("confidence", result["result"])

    def test_boundary_probability_is_inclusive_and_lower_probability_reviews(self):
        for probability, expected in ((0.8, "recommend"), (0.799, "review")):
            with self.subTest(probability=probability):
                answers = {"decision": {"choice": "visible", "probabilities": {
                    "visible": probability, "not_visible": (1 - probability) / 2,
                    "review": (1 - probability) / 2}}}
                result = execute_image(self.folder, "sage", self.data, demo_answers=answers)
                self.assertEqual(result["result"]["action"], expected)
                self.assertEqual(result["result"]["selected_probability"], probability)

    def test_review_choice_always_reviews_even_at_probability_one(self):
        result = execute_image(self.folder, "sage", self.data, demo_answers={"decision": {
            "choice": "review", "probabilities": {"visible": 0, "not_visible": 0, "review": 1}}})
        self.assertEqual(result["result"]["action"], "review")
        self.assertIn("model_requested_review", result["result"]["reasons"])

    def test_malformed_non_ok_unknown_kind_model_and_duplicate_answer_ids_fail(self):
        mutations = []
        malformed = native_raw(); malformed["results"][0]["answers"][0]["result"].pop("result")
        mutations.append(("missing nested result", malformed))
        non_ok = native_raw(); non_ok["results"][0]["answers"][0]["ok"] = False
        mutations.append(("non-ok", non_ok))
        wrong_model = native_raw(model="unexpected")
        mutations.append(("model mismatch", wrong_model))
        wrong_kind = native_raw(); wrong_kind["results"][0]["answers"][1]["result"]["kind"] = "scale"
        mutations.append(("wrong kind", wrong_kind))
        duplicate = native_raw(); duplicate["results"][0]["answers"][1]["result"]["id"] = "is_present"
        mutations.append(("duplicate id", duplicate))
        for label, raw in mutations:
            with self.subTest(case=label):
                expected = "model_mismatch" if label == "model mismatch" else "invalid_response"
                self.assert_code(expected, SageImageAdapter().parse_response, raw, QUESTIONS)

    def test_native_abstentions_become_refusals_without_inventing_answer_values(self):
        raw = native_raw()
        yesno = raw["results"][0]["answers"][0]["result"]["result"]
        yesno["answer"] = None
        choice = raw["results"][0]["answers"][1]["result"]["result"]
        choice["chosen"] = None
        choice["abstained"] = True
        scale = raw["results"][0]["answers"][2]["result"]["result"]
        scale.pop("expectation")
        result = SageImageAdapter().parse_response(raw, QUESTIONS)
        for name in ("is_present", "decision", "severity"):
            self.assertEqual(result["answers"][name]["status"], "refusal")


class ImageInputGuardsTests(ImageReferenceFixture):
    def test_permission_denial_returns_before_image_read_attempt_or_transport(self):
        denied = {"permission_granted": False, "state": {"content": "caption", "image": "missing.png"}}
        transport = Mock(side_effect=AssertionError("transport must not run"))
        before = Mock(side_effect=AssertionError("no attempt should be reserved"))
        with patch("builtins.open", side_effect=AssertionError("must not read an image")):
            result = execute_image(self.folder, "sage", denied, mode="live", transport=transport,
                                   before_attempt=before)
        self.assertEqual(result["result"]["action"], "deny")
        self.assertEqual(result["attempts"], 0)
        transport.assert_not_called()
        before.assert_not_called()

    def test_missing_image_or_caption_is_deterministic_review_without_transport(self):
        samples = [
            {"permission_granted": True, "state": {"content": "caption"}},
            {"permission_granted": True, "state": {"image": "assets/sample.png"}},
            {"permission_granted": True, "state": {"content": " ", "image": "assets/sample.png"}},
        ]
        for data in samples:
            with self.subTest(data=data):
                transport = Mock(side_effect=AssertionError("missing evidence must not call Sage"))
                result = execute_image(self.folder, "sage", data, mode="live", transport=transport)
                self.assertEqual(result["result"]["action"], "review")
                self.assertEqual(result["result"]["reasons"], ["missing_evidence"])
                self.assertEqual(result["attempts"], 0)
                transport.assert_not_called()

    def test_local_relative_path_only_and_symlink_cannot_escape_asset_root(self):
        outside = self.root / "outside.png"
        outside.write_bytes(png_bytes())
        escape_link = self.folder / "escape.png"
        escape_link.symlink_to(outside)
        for reference in ("../outside.png", str(outside), "https://example.invalid/image.png",
                          "data:image/png;base64,AA==", "escape.png"):
            with self.subTest(reference=reference):
                bad = copy.deepcopy(self.data)
                bad["state"]["image"] = reference
                self.assert_code("invalid_request", prepare_image, self.folder, bad)

    def test_missing_oversize_corrupt_or_excessive_dimensions_are_rejected(self):
        bad = copy.deepcopy(self.data)
        bad["state"]["image"] = "assets/absent.png"
        self.assert_code("invalid_request", prepare_image, self.folder, bad)
        too_big = self.folder / "assets" / "large.png"
        too_big.write_bytes(png_bytes() + b"x" * (4 * 1024 * 1024))
        bad["state"]["image"] = "assets/large.png"
        self.assert_code("invalid_request", prepare_image, self.folder, bad)
        corrupt = self.folder / "assets" / "corrupt.png"
        corrupt.write_bytes(png_bytes(corrupt_crc=True))
        bad["state"]["image"] = "assets/corrupt.png"
        self.assert_code("invalid_request", prepare_image, self.folder, bad)
        huge_dimensions = self.folder / "assets" / "dimensions.png"
        huge_dimensions.write_bytes(png_bytes(width=8193, height=1))
        bad["state"]["image"] = "assets/dimensions.png"
        self.assert_code("invalid_request", prepare_image, self.folder, bad)

    def test_png_jpeg_and_webp_headers_are_detected_and_bytes_are_preserved(self):
        for filename, content, mime in (("a.png", png_bytes(), "image/png"),
                                        ("a.jpg", jpeg_bytes(), "image/jpeg"),
                                        ("a.webp", webp_bytes(), "image/webp")):
            with self.subTest(filename=filename):
                path = self.folder / "assets" / filename
                path.write_bytes(content)
                data = copy.deepcopy(self.data)
                data["state"]["image"] = f"assets/{filename}"
                prepared = prepare_image(self.folder, data)
                self.assertEqual(prepared["image"]["mime"], mime)
                self.assertEqual(prepared["content"]["media"],
                                 f"data:{mime};base64,{base64.b64encode(content).decode('ascii')}")

    def test_unsupported_provider_fails_before_credentials_or_transport(self):
        transport = Mock(side_effect=AssertionError("unsupported provider must not call transport"))
        with patch.dict(os.environ, {}, clear=True):
            self.assert_code("unsupported_modality", execute_image, self.folder, "openai", self.data,
                             mode="live", transport=transport)
        transport.assert_not_called()

    def test_live_attempt_is_reserved_before_call_and_raw_response_recorded_before_parse_failure(self):
        events = []
        raw = native_raw()
        raw["results"][0]["answers"][1]["result"]["id"] = "wrong-id"
        def reserve(provider, payload):
            events.append(("reserve", provider, payload))
        def transport(endpoint, payload, key, timeout):
            events.append(("transport", endpoint))
            return raw
        def record(provider, returned):
            events.append(("record", provider, returned))
        with patch.dict(os.environ, {"SAGE_API_KEY": "offline"}, clear=True):
            self.assert_code("invalid_response", execute_image, self.folder, "sage", self.data,
                             mode="live", transport=transport, before_attempt=reserve,
                             after_attempt=record)
        self.assertEqual([event[0] for event in events], ["reserve", "transport", "record"])
        self.assertEqual(events[-1][2], raw)

    def test_image_schema_cannot_be_loaded_by_text_only_use_case_loader(self):
        transport = Mock(side_effect=AssertionError("schema validation must precede paid calls"))
        with self.assertRaises(DecisionError):
            load_use_case(self.folder / "image.json")
        transport.assert_not_called()

    def test_copied_script_cli_runs_from_another_directory_with_demo_answers(self):
        copied = self.root / "copied-skill"
        copied.mkdir()
        shutil.copy2(self.folder / "image.json", copied / "image.json")
        shutil.copy2(self.asset, copied / "sample.png")
        copied_script = copied / "image_reference.py"
        shutil.copy2(SCRIPT, copied_script)
        input_file = self.root / "input.json"
        input_file.write_text(json.dumps({"permission_granted": True,
            "state": {"content": "Portable image caption.", "image": "sample.png"}}), encoding="utf-8")
        demo_file = self.root / "demo.json"
        demo_file.write_text(json.dumps({"decision": {"choice": "visible",
            "probabilities": {"visible": 0.8, "not_visible": 0.1, "review": 0.1}}}), encoding="utf-8")
        env = dict(os.environ)
        env.pop("PYTHONPATH", None)
        completed = subprocess.run(
            [sys.executable, str(copied_script), "--folder", str(copied), "--input", str(input_file),
             "--demo-answers", str(demo_file)],
            cwd=self.root, env=env, text=True, capture_output=True, check=False, timeout=30,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        output = json.loads(completed.stdout)
        self.assertEqual(output["result"]["action"], "recommend")
        self.assertEqual(output["response"]["model"], "DEMO-hand-authored-not-model-output")


if __name__ == "__main__":
    unittest.main()
