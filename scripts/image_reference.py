"""Local image reference runner for Sage image decisions."""
import argparse
import base64
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys
import time
import zlib

from decision_models.contracts import DecisionError, validate_questions, validate_response
from decision_models.transport import http_transport


class SageImageAdapter:
    name = "sage"
    endpoint = "https://sage.levanto.ai/decide/batch"
    key_env = "SAGE_API_KEY"
    default_model = "levanto-sage-v1.4"

    def build_payload(self, image_content, canonical_questions, model=None):
        if model is not None and model != self.default_model:
            raise DecisionError("model_mismatch", "Sage image endpoint resolves levanto-sage-v1.4 and does not accept a model field")
        if not isinstance(image_content, dict) or image_content.get("kind") != "image":
            raise DecisionError("invalid_request", "image_content must be validated native image content")
        if not isinstance(image_content.get("media"), str) or not image_content["media"].startswith("data:image/"):
            raise DecisionError("invalid_request", "image media must be a base64 image data URI")
        validate_questions(canonical_questions)
        questions = canonical_questions
        native_questions = []
        for question in questions:
            kind = question["kind"]
            native_kind = {"predicate": "yesno", "choice": "choice", "score": "scale"}[kind]
            native = {"kind": native_kind, "id": question["name"],
                      "instructions": question["instructions"]}
            if kind == "predicate":
                criteria = question.get("criteria")
                if criteria:
                    native["instructions"] += (
                        " Interpret yes as: " + criteria["true"] + " Interpret no as: " + criteria["false"]
                    )
            elif kind == "choice":
                if len(question["options"]) > 20:
                    raise DecisionError("invalid_request", "Sage image choice supports at most 20 options")
                native["options"] = [{"option": key, "description": value}
                                     for key, value in question["options"].items()]
            else:
                if len(question["levels"]) > 26:
                    raise DecisionError("invalid_request", "Sage scale supports at most 26 levels")
                native["levels"] = [{"level": index, "description": value}
                                    for index, value in enumerate(question["levels"])]
            native_questions.append(native)
        return {"reasoning": "off", "latency_mode": "quality",
                "requests": [{"content": image_content, "questions": native_questions}]}

    def parse_response(self, raw, questions):
        validate_questions(questions)
        if not isinstance(raw, dict):
            raise DecisionError("invalid_response", "Sage batch response must be an object")
        meta = raw.get("meta")
        model = meta.get("model") if isinstance(meta, dict) else None
        if model != self.default_model:
            raise DecisionError("model_mismatch", "Sage response resolved an unexpected model")
        groups = raw.get("results")
        if not isinstance(groups, list) or len(groups) != 1 or not isinstance(groups[0], dict):
            raise DecisionError("invalid_response", "Sage image response must contain exactly one batch group")
        rows = groups[0].get("answers")
        if not isinstance(rows, list) or len(rows) != len(questions):
            raise DecisionError("invalid_response", "Sage answer count does not match submitted questions")
        by_id = {}
        for row in rows:
            if not isinstance(row, dict) or row.get("ok") is not True:
                raise DecisionError("invalid_response", "Sage returned a non-ok or malformed answer")
            result = row.get("result")
            if not isinstance(result, dict):
                raise DecisionError("invalid_response", "Sage answer is missing its nested result")
            answer_id = result.get("id")
            if not isinstance(answer_id, str) or answer_id in by_id:
                raise DecisionError("invalid_response", "Sage answer IDs must be unique strings")
            by_id[answer_id] = result
        if set(by_id) != {q["name"] for q in questions}:
            raise DecisionError("invalid_response", "Sage answer IDs do not match submitted questions")

        answers = {}
        for question in questions:
            name, kind = question["name"], question["kind"]
            result = by_id[name]
            expected_kind = {"predicate": "yesno", "choice": "choice", "score": "scale"}[kind]
            if result.get("kind") != expected_kind:
                raise DecisionError("invalid_response", f"Sage answer {name!r} has the wrong kind")
            native = result.get("result")
            if not isinstance(native, dict):
                raise DecisionError("invalid_response", f"Sage answer {name!r} has a malformed result")
            per_answer_meta = result.get("meta")
            if not isinstance(per_answer_meta, dict):
                raise DecisionError("invalid_response", f"Sage answer {name!r} is missing metadata")
            if per_answer_meta.get("model") is not None and per_answer_meta["model"] != model:
                raise DecisionError("model_mismatch", f"Sage answer {name!r} resolved an unexpected model")
            answer = {"kind": kind, "status": "answered", "native_result": native,
                      "meta": per_answer_meta}
            if kind == "predicate":
                value, probability = native.get("answer"), native.get("probability")
                if value is None:
                    answer["status"] = "refusal"
                elif value not in ("yes", "no") or not _unit(probability):
                    raise DecisionError("invalid_response", f"Sage predicate {name!r} is malformed")
                else:
                    answer.update(probability_true=probability, answer=value, probability=probability)
            elif kind == "choice":
                chosen, probability, distribution = native.get("chosen"), native.get("probability"), native.get("probabilities")
                if chosen is None or native.get("abstained") is True:
                    answer["status"] = "refusal"
                else:
                    if chosen not in question["options"] or not _unit(probability):
                        raise DecisionError("invalid_response", f"Sage choice {name!r} is malformed")
                    probs = _choice_probabilities(distribution, question["options"])
                    if abs(probability - probs[chosen]) > 0.000001:
                        raise DecisionError("invalid_response", f"Sage choice {name!r} probability disagrees with its distribution")
                    answer.update(choice=chosen, probability=probability, probabilities=probs,
                                  confidence=None)
            else:
                expectation = native.get("expectation")
                distribution = native.get("probabilities")
                confidence = native.get("confidence")
                if expectation is None:
                    answer["status"] = "refusal"
                else:
                    if not _finite(expectation) or not 0 <= expectation <= len(question["levels"]) - 1:
                        raise DecisionError("invalid_response", f"Sage scale {name!r} has an invalid expectation")
                    if not _unit(confidence):
                        raise DecisionError("invalid_response", f"Sage scale {name!r} has invalid confidence")
                    probs = _scale_probabilities(distribution, len(question["levels"]))
                    answer.update(score=expectation, probabilities=probs, confidence=confidence)
            answers[name] = answer
        return validate_response({"model": model, "answers": answers, "usage": meta.get("usage"),
                                  "raw_response": raw}, questions)


def load_config(folder):
    try:
        config = json.loads((Path(folder) / "image.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise DecisionError("invalid_request", "cannot read valid image skill JSON") from exc
    return _validate_config(config)


def prepare_image(folder, data, asset_root=None):
    """Return {early_result, content, image}; file access follows permission check."""
    if not isinstance(data, dict):
        raise DecisionError("invalid_request", "skill input must be an object")
    if data.get("permission_granted") is not True:
        return {"early_result": _decision("deny", None, ["permission_not_granted"]),
                "content": None, "image": None}
    state = data.get("state")
    if not isinstance(state, dict):
        return {"early_result": _decision("review", "review", ["missing_evidence"]),
                "content": None, "image": None}
    caption, image_ref = state.get("content"), state.get("image")
    if not isinstance(caption, str) or not caption.strip() or not isinstance(image_ref, str) or not image_ref.strip():
        return {"early_result": _decision("review", "review", ["missing_evidence"]),
                "content": None, "image": None}
    candidate = Path(image_ref)
    if candidate.is_absolute() or "://" in image_ref or image_ref.startswith("data:"):
        raise DecisionError("invalid_request", "image must be a local relative path")
    root = Path(asset_root) if asset_root is not None else Path(folder)
    try:
        resolved_root = root.resolve(strict=True)
        resolved = (resolved_root / candidate).resolve(strict=True)
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise DecisionError("invalid_request", "image path is missing or escapes the allowed asset folder") from exc
    if not resolved.is_file():
        raise DecisionError("invalid_request", "image path must refer to a local file")
    try:
        if resolved.stat().st_size > 4 * 1024 * 1024:
            raise DecisionError("invalid_request", "image exceeds the 4 MiB limit")
        with resolved.open("rb") as image_file:
            raw = image_file.read(4 * 1024 * 1024 + 1)
    except OSError as exc:
        raise DecisionError("invalid_request", "image file cannot be read") from exc
    if len(raw) > 4 * 1024 * 1024:
        raise DecisionError("invalid_request", "image exceeds the 4 MiB limit")
    mime, width, height = _image_dimensions(raw)
    media = "data:" + mime + ";base64," + base64.b64encode(raw).decode("ascii")
    return {"early_result": None,
            "content": {"kind": "image", "media": media, "text": caption},
            "image": {"sha256": hashlib.sha256(raw).hexdigest(), "mime": mime,
                      "width": width, "height": height}}


def execute_image(folder, provider, data, *, mode="demo", demo_answers=None, asset_root=None,
                  transport=http_transport, before_attempt=None, after_attempt=None):
    config = load_config(folder)
    if provider != "sage":
        raise DecisionError("unsupported_modality", "image modality currently supports only Sage")
    if mode not in ("demo", "live"):
        raise DecisionError("invalid_request", "mode must be demo or live")
    out = {"skill": config["id"], "provider": provider, "mode": mode,
           "requested_model": SageImageAdapter.default_model, "executed_action": False}
    prepared = prepare_image(folder, data, asset_root)
    if prepared["early_result"] is not None:
        return dict(out, result=prepared["early_result"], source="deterministic",
                    response=None, latency_ms=0, attempts=0, image=None)
    questions = [config["question"]]
    adapter = SageImageAdapter()
    started = time.perf_counter()
    if mode == "demo":
        response = _demo_response(demo_answers, questions)
    else:
        key = os.environ.get(adapter.key_env)
        if not key:
            raise DecisionError("missing_credentials", f"set {adapter.key_env} for live mode")
        payload = adapter.build_payload(prepared["content"], questions)
        if before_attempt:
            before_attempt(provider, payload)
        raw = transport(adapter.endpoint, payload, key, 20)
        if after_attempt:
            after_attempt(provider, raw)
        response = adapter.parse_response(raw, questions)
    result = _decision_from_response(config, response)
    return dict(out, result=result, source=mode, response=response,
                latency_ms=round((time.perf_counter() - started) * 1000, 3),
                attempts=int(mode == "live"), image=prepared["image"])


def _validate_config(config):
    if not isinstance(config, dict) or type(config.get("schema_version")) is not int or config["schema_version"] != 2:
        raise DecisionError("invalid_request", "image skill schema_version must be 2")
    if config.get("input_modality") != "image":
        raise DecisionError("invalid_request", "skill input_modality must be image")
    if not isinstance(config.get("id"), str) or not config["id"]:
        raise DecisionError("invalid_request", "skill needs an id")
    for field in ("title", "description", "inspiration", "limitations"):
        if not isinstance(config.get(field), str) or not config[field].strip():
            raise DecisionError("invalid_request", f"skill needs {field}")
    urls = config.get("source_urls")
    if not isinstance(urls, list) or not urls or any(not isinstance(x, str) or not x.startswith("https://") for x in urls):
        raise DecisionError("invalid_request", "skill needs HTTPS source_urls")
    if config.get("required_state_fields") != ["content", "image"]:
        raise DecisionError("invalid_request", "image skill required_state_fields must be content and image")
    validate_questions([config.get("question")])
    question = config["question"]
    if question.get("kind") != "choice" or question.get("name") != "decision":
        raise DecisionError("invalid_request", "image skill needs a canonical decision choice")
    if "review" not in question["options"] or len(question["options"]) > 20:
        raise DecisionError("invalid_request", "image skill choice needs review and at most 20 options")
    policy = config.get("policy")
    if (not isinstance(policy, dict) or policy.get("review_choice") != "review" or
            set(policy) != {"probability_threshold", "review_choice"} or
            not _unit(policy.get("probability_threshold"))):
        raise DecisionError("invalid_request", "image policy must contain only probability_threshold and review_choice")
    return config


def _image_dimensions(data):
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        width, height = _png(data)
        mime = "image/png"
    elif data.startswith(b"\xff\xd8"):
        width, height = _jpeg(data)
        mime = "image/jpeg"
    elif data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        width, height = _webp(data)
        mime = "image/webp"
    else:
        raise DecisionError("invalid_request", "image must be PNG, JPEG, or WebP")
    if width < 1 or height < 1 or max(width, height) > 8192 or width * height > 4096 * 4096:
        raise DecisionError("invalid_request", "image dimensions exceed Sage limits")
    return mime, width, height


def _png(data):
    pos, dimensions, ended, saw_idat = 8, None, False, False
    while pos < len(data):
        if pos + 12 > len(data):
            raise DecisionError("invalid_request", "truncated PNG chunk")
        size = struct.unpack(">I", data[pos:pos + 4])[0]
        end = pos + 12 + size
        if end > len(data):
            raise DecisionError("invalid_request", "truncated PNG chunk data")
        kind, chunk = data[pos + 4:pos + 8], data[pos + 8:pos + 8 + size]
        crc = struct.unpack(">I", data[pos + 8 + size:end])[0]
        if zlib.crc32(kind + chunk) & 0xffffffff != crc:
            raise DecisionError("invalid_request", "PNG chunk CRC is invalid")
        if pos == 8:
            if kind != b"IHDR" or size != 13:
                raise DecisionError("invalid_request", "PNG has an invalid IHDR")
            dimensions = struct.unpack(">II", chunk[:8])
        if kind == b"IDAT":
            saw_idat = True
        if kind == b"IEND":
            ended = size == 0
            if not ended or end != len(data):
                raise DecisionError("invalid_request", "PNG has invalid trailing data")
            break
        pos = end
    if dimensions is None or not ended or not saw_idat:
        raise DecisionError("invalid_request", "PNG is incomplete")
    return dimensions


def _jpeg(data):
    pos, dimensions = 2, None
    sof = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
    while pos < len(data):
        while pos < len(data) and data[pos] == 0xff:
            pos += 1
        if pos >= len(data):
            break
        marker = data[pos]
        pos += 1
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7 or marker == 0x01:
            if marker == 0xD9:
                break
            continue
        if pos + 2 > len(data):
            break
        length = struct.unpack(">H", data[pos:pos + 2])[0]
        if length < 2 or pos + length > len(data):
            break
        if marker in sof:
            if length < 7:
                break
            height, width = struct.unpack(">HH", data[pos + 3:pos + 7])
            dimensions = (width, height)
        if marker == 0xDA:
            break
        pos += length
    if dimensions is None or not data.endswith(b"\xff\xd9"):
        raise DecisionError("invalid_request", "JPEG is incomplete or has no valid dimensions")
    return dimensions


def _webp(data):
    if len(data) < 30 or struct.unpack("<I", data[4:8])[0] + 8 != len(data):
        raise DecisionError("invalid_request", "WebP container is truncated")
    pos, dimensions, saw_frame = 12, None, False
    while pos + 8 <= len(data):
        kind, size = data[pos:pos + 4], struct.unpack("<I", data[pos + 4:pos + 8])[0]
        start, end = pos + 8, pos + 8 + size
        if end > len(data):
            raise DecisionError("invalid_request", "WebP chunk is truncated")
        chunk = data[start:end]
        if kind == b"VP8X" and size >= 10:
            dimensions = (1 + int.from_bytes(chunk[4:7], "little"), 1 + int.from_bytes(chunk[7:10], "little"))
        elif kind == b"VP8 " and size >= 10 and chunk[3:6] == b"\x9d\x01\x2a":
            dimensions = (struct.unpack("<H", chunk[6:8])[0] & 0x3fff,
                          struct.unpack("<H", chunk[8:10])[0] & 0x3fff)
            saw_frame = size > 10
        elif kind == b"VP8L" and size >= 5 and chunk[0] == 0x2f:
            b1, b2, b3, b4 = chunk[1:5]
            dimensions = (1 + (((b2 & 0x3f) << 8) | b1),
                          1 + (((b4 & 0x0f) << 10) | (b3 << 2) | ((b2 & 0xc0) >> 6)))
            saw_frame = size > 5
        pos = end + (size & 1)
    if dimensions is None or not saw_frame:
        raise DecisionError("invalid_request", "WebP has no supported image frame")
    return dimensions


def _choice_probabilities(value, options):
    if not isinstance(value, list) or len(value) != len(options):
        raise DecisionError("invalid_response", "Sage choice distribution is incomplete")
    result = {}
    for item in value:
        if not isinstance(item, dict) or item.get("option") not in options or item["option"] in result or not _unit(item.get("probability")):
            raise DecisionError("invalid_response", "Sage choice distribution is malformed")
        result[item["option"]] = item["probability"]
    if set(result) != set(options):
        raise DecisionError("invalid_response", "Sage choice distribution does not match options")
    return result


def _scale_probabilities(value, count):
    if not isinstance(value, list) or len(value) != count:
        raise DecisionError("invalid_response", "Sage scale distribution is incomplete")
    result = {}
    for item in value:
        if not isinstance(item, dict) or type(item.get("level")) is not int or not 0 <= item["level"] < count or item["level"] in result or not _unit(item.get("probability")):
            raise DecisionError("invalid_response", "Sage scale distribution is malformed")
        result[str(item["level"])] = item["probability"]
    if set(result) != {str(index) for index in range(count)}:
        raise DecisionError("invalid_response", "Sage scale distribution does not match levels")
    return result


def _demo_response(demo_answers, questions):
    if not isinstance(demo_answers, dict) or set(demo_answers) != {q["name"] for q in questions}:
        raise DecisionError("invalid_request", "demo requires explicit hand-authored canonical answers")
    answers = {}
    for q in questions:
        value = demo_answers[q["name"]]
        if isinstance(value, str):
            value = {"choice": value}
        if not isinstance(value, dict):
            raise DecisionError("invalid_request", "demo answer must be an explicit object")
        choice = value.get("choice")
        probs = value.get("probabilities")
        if choice not in q["options"] or not isinstance(probs, dict) or set(probs) != set(q["options"]):
            raise DecisionError("invalid_request", "demo choice and probabilities must match the skill options")
        if any(not _unit(v) for v in probs.values()) or abs(sum(probs.values()) - 1) > 0.02:
            raise DecisionError("invalid_request", "demo probabilities must be valid and sum to one")
        answers[q["name"]] = {"kind": "choice", "status": "answered", "choice": choice,
                              "probability": probs[choice], "probabilities": probs,
                              "confidence": None, "native_result": None, "meta": None}
    return validate_response({"model": "DEMO-hand-authored-not-model-output", "answers": answers,
                              "usage": None, "raw_response": None}, questions)


def _decision_from_response(config, response):
    answer = response["answers"]["decision"]
    if answer["status"] == "refusal":
        return _decision("review", "review", ["provider_refusal"], provider_confidence=None)
    choice = answer["choice"]
    probability = answer["probability"]
    reasons = []
    if choice == "review":
        reasons.append("model_requested_review")
    if probability < config["policy"]["probability_threshold"]:
        reasons.append("probability_below_threshold")
    return {"action": "review" if reasons else "recommend", "choice": "review" if reasons else choice,
            "reasons": reasons or ["bounded_recommendation"], "selected_probability": probability,
            "provider_confidence": None}


def _decision(action, choice, reasons, provider_confidence=None):
    return {"action": action, "choice": choice, "reasons": reasons,
            "selected_probability": None, "provider_confidence": provider_confidence}


def _finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _unit(value):
    return _finite(value) and 0 <= value <= 1


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run an attributed image decision skill locally or with Sage.")
    parser.add_argument("--folder", required=True, help="Copied skill folder containing image.json")
    parser.add_argument("--input", required=True, help="JSON input file with permission_granted and state")
    parser.add_argument("--mode", choices=("demo", "live"), default="demo")
    parser.add_argument("--demo-answers", help="JSON object containing explicit canonical demo answers")
    parser.add_argument("--asset-root", help="Optional folder that contains relative image paths")
    args = parser.parse_args(argv)
    try:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
        demo_answers = json.loads(Path(args.demo_answers).read_text(encoding="utf-8")) if args.demo_answers else None
        print(json.dumps(execute_image(args.folder, "sage", data, mode=args.mode,
              demo_answers=demo_answers, asset_root=args.asset_root), ensure_ascii=False, indent=2))
        return 0
    except (DecisionError, OSError, ValueError) as exc:
        detail = exc.as_dict() if isinstance(exc, DecisionError) else {"code": "invalid_request", "message": str(exc)}
        print(json.dumps({"error": detail}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
