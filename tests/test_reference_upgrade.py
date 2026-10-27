"""Offline compatibility proof for the frozen reference runtime."""
import json
from pathlib import Path
import shutil
import struct
import tempfile
import unittest
import zlib

from scripts.audit_reference_upgrade import (
    BASELINE_COMMIT,
    OLD_RUNTIME_REVISION,
    digest,
    verify_demo_contracts,
)


ROOT = Path(__file__).resolve().parents[1]
GOLDEN_PATH = ROOT / "scripts/reference-contracts.json"


class ReferenceUpgradeTests(unittest.TestCase):
    def setUp(self):
        self.golden = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))

    def test_golden_is_pinned_to_frozen_runtime_and_full_case_coverage(self):
        golden = self.golden
        self.assertEqual(golden["baseline_commit"], BASELINE_COMMIT)
        self.assertEqual(golden["previous_runtime_revision"], OLD_RUNTIME_REVISION)
        self.assertEqual(golden["skill_count"], 27)
        self.assertEqual(golden["payload_and_policy_cases"], 948)
        self.assertEqual(len(golden["contracts"]), 948)
        self.assertEqual(len({(r["skill"], r["provider"], r["case_id"]) for r in golden["contracts"]}), 948)
        self.assertEqual(golden["contract_sha256"], digest(golden["contracts"]))
        self.assertEqual(set(golden["previous_reference_artifacts"]), {
            "scripts/usecase_reference.py",
            "scripts/evaluate_usecases.py",
            "scripts/image_reference.py",
            "scripts/evaluate_images.py",
        })
        self.assertEqual(len(golden["artifacts"]), 27)
        self.assertEqual(len(golden["receipt_sha256"]), 4)

    def test_current_demo_contracts_match_frozen_golden(self):
        current = verify_demo_contracts(ROOT, self.golden)
        self.assertEqual(len(current["contracts"]), 948)
        self.assertEqual(current["skill_count"], 27)

    def test_tampered_golden_is_rejected(self):
        tampered = json.loads(json.dumps(self.golden))
        tampered["contracts"][0]["request_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "golden contract digest is invalid"):
            verify_demo_contracts(ROOT, tampered)

    def test_modified_decision_asset_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix="reference-upgrade-drift-") as temporary:
            checkout = Path(temporary)
            for name in ("src", "scripts", "skills"):
                shutil.copytree(ROOT / name, checkout / name)
            decision = checkout / "skills/ad-funnel-classification/decision.json"
            config = json.loads(decision.read_text(encoding="utf-8"))
            config["policy"]["confidence_threshold"] += 0.01
            decision.write_text(json.dumps(config), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "contracts changed|artifacts changed"):
                verify_demo_contracts(checkout, self.golden)

    def test_modified_local_image_asset_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix="reference-upgrade-image-drift-") as temporary:
            checkout = Path(temporary)
            for name in ("src", "scripts", "skills"):
                shutil.copytree(ROOT / name, checkout / name)
            image = checkout / "skills/screenshot-action-check/images/frame01.png"
            content = image.read_bytes()
            marker = b"\x00\x00\x00\x00IEND"
            offset = content.rfind(marker)
            self.assertGreaterEqual(offset, 0)
            text = b"audit\x00changed"
            chunk_type = b"tEXt"
            chunk = (struct.pack(">I", len(text)) + chunk_type + text +
                     struct.pack(">I", zlib.crc32(chunk_type + text) & 0xFFFFFFFF))
            image.write_bytes(content[:offset] + chunk + content[offset:])
            with self.assertRaisesRegex(ValueError, "contracts changed|artifacts changed"):
                verify_demo_contracts(checkout, self.golden)
