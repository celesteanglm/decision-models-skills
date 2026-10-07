"""Verify the installed CLI, contracts and portable skills without credentials."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

from decision_models.evaluation import source_hash
from decision_models.runtime import SKILLS, PROVIDERS


def main():
    repo = Path(__file__).resolve().parents[1]
    marker = repo / "reports" / "offline.json"
    marker.parent.mkdir(exist_ok=True)
    marker.unlink(missing_ok=True)
    env = dict(os.environ)
    for name in ("OPENROUTER_API_KEY", "OPENAI_API_KEY", "SAGE_API_KEY", "PYTHONPATH"):
        env.pop(name, None)
    subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(repo / "tests"), "-v"],
                   cwd=repo, env=env, check=True)
    demonstrations = []
    with tempfile.TemporaryDirectory(prefix="decision-models-portable-") as directory:
        project = Path(directory) / "fresh-project"
        elsewhere = Path(directory) / "elsewhere"
        elsewhere.mkdir()
        for skill in SKILLS:
            copied = project / ".agents" / "skills" / skill
            shutil.copytree(repo / "skills" / skill, copied)
            for provider in PROVIDERS:
                command = [sys.executable, "-m", "decision_models", "run", skill,
                           "--provider", provider, "--mode", "demo",
                           "--input", str(copied / "examples" / "input.json"),
                           "--demo-answers", str(copied / "examples" / "demo.json")]
                result = subprocess.run(command, cwd=elsewhere, env=env, check=True,
                                        text=True, capture_output=True)
                receipt = json.loads(result.stdout)
                assert receipt["mode"] == "demo" and receipt["source"] in ("demo", "deterministic")
                assert receipt["executed_action"] is False
                demonstrations.append({"skill": skill, "provider": provider,
                                       "action": receipt["result"]["action"]})
    marker.write_text(json.dumps({"passed": True, "source_hash": source_hash(repo),
        "checked_at": datetime.now(timezone.utc).isoformat(), "python": sys.version.split()[0],
        "checks": ["unittest suite", "18 credential-free copied-skill demos from another cwd"],
        "demos": demonstrations}, indent=2) + "\n")
    print(f"Offline verification passed: {marker}")


if __name__ == "__main__":
    main()
