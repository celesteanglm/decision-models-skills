"""Opt-in real CLI checks; temporary installs, isolated credentials, no retries.

Run offer, decline, then approve for each host/setup in a fresh directory.
The caller supplies approval only on the separate approve invocation. This
synthetic harness exercises the backend boundary, not a client's approval UI.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
import uuid

REPO = Path(__file__).resolve().parents[1]
PROMPTS = {
    "offer": "I need a repeating screenshot QA check across a growing batch. Please assess this first screenshot, example.png: is the CONTINUE button near the lower-right of the checkout panel fully visible and unobstructed? Image processing is permitted for this synthetic screenshot; return a recommendation and do not click anything.",
    "decline": "No, do not send it to Sage or any other external model. Assess this screenshot with your current model instead. Image processing remains permitted. Do not click anything.",
    "approve": "I now explicitly approve one Sage call for this synthetic example.png and the CONTINUE visibility question only, with reasoning and search off, accepting either levanto-sage-v1.4 or levanto-sage-2 as selected by the server. Maximum US$0.06 for this one call. Report the actual model and native answer; do not click anything or retry a failed request.",
}
TOOL = {
    "name": "sage_image_check",
    "description": "External Sage image check. Sends the fixed synthetic example.png and CONTINUE visibility question. Server may select levanto-sage-v1.4 or levanto-sage-2; there is no model selector. One request, no reasoning/search, cap US$0.06. Qualification of THIS MCP integration: Not tested for a compatibility badge; the historical v1.4 reference result does not qualify this integration/model policy. Do not advertise it as Working. Read screenshot-action-check SKILL.md and COMPATIBILITY.md first. Before calling, offer this option and wait for a separate user approval. Tool availability is NOT consent. Backend rejects unapproved calls; never retry or bypass a rejection.",
    "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
}


def bridge(address):
    """Credential-free stdio MCP bridge; no control/approval method exists."""
    with socket.socket(socket.AF_UNIX) as client:
        client.connect(address)
        reader = client.makefile("rb")
        for line in sys.stdin.buffer:
            client.sendall(line)
            request = json.loads(line)
            if "id" in request:
                reply = reader.readline()
                if not reply:
                    raise RuntimeError("backend closed without a response")
                sys.stdout.buffer.write(reply)
                sys.stdout.buffer.flush()


def backend(listener, project, phase, journal):
    # This thread belongs to the trusted runner. Only it inherits SAGE_API_KEY.
    # Client/bridge processes have provider secrets removed from their environment.
    sys.path[:0] = [str(REPO), str(REPO / "src")]
    from examples.scoped_consent import (ConsentGuard, ConsentDenied, ScopedRequest,
                                          grant_after_human_approval)
    from examples.sage_image_model_selection import AllowedSageImageAdapter
    from scripts.image_reference import load_config, prepare_image, execute_image
    from scripts.evaluate_images import ImageBudget
    from decision_models.transport import encode_payload, http_transport

    folder = project / "selected-skill"
    data = {"permission_granted": True, "state": {
        "content": "Is the CONTINUE button near the lower-right of the checkout panel fully visible and unobstructed? Inspect screenshot pixels only; do not infer enabled state, function or safety. Never click anything.",
        "image": "example.png"}}
    adapter = AllowedSageImageAdapter(["levanto-sage-v1.4", "levanto-sage-2"])
    prepared = prepare_image(folder, data, project)
    payload = adapter.build_payload(prepared["content"], [load_config(folder)["question"]])
    request = ScopedRequest(project.name, encode_payload(payload), "sage",
                            "levanto-sage-v1.4|levanto-sage-2", "button-visibility")
    guard = ConsentGuard(0.06)
    reserve = ImageBudget.allowance(payload)
    grant = None
    if phase == "approve":
        grant = grant_after_human_approval(task=request.task, data=request.data,
            backend=request.backend, model=request.model,
            operation=request.operation, budget_usd=0.06)

    def record(row):
        with journal.open("a") as stream:
            stream.write(json.dumps(row, allow_nan=False) + "\n")

    def dispatch(endpoint, outgoing, key, timeout):
        actual = ScopedRequest(request.task, encode_payload(outgoing), request.backend,
                               request.model, request.operation)
        def send(scoped):
            record({"event": "provider_dispatch", "payload_sha256": scoped.data_sha256,
                    "reserved_usd": reserve})
            raw = http_transport(endpoint, outgoing, key, timeout)
            record({"event": "provider_raw", "response": raw})
            return raw
        return guard.call(grant, actual, reserve, send)

    with listener:
        connection, _ = listener.accept()
        with connection, connection.makefile("rb") as incoming:
            for line in incoming:
                message = json.loads(line)
                if "id" not in message:
                    continue
                method = message.get("method")
                record({"event": "mcp_method", "method": method})
                if method == "initialize":
                    result = {"protocolVersion": message.get("params", {}).get("protocolVersion", "2024-11-05"),
                              "capabilities": {"tools": {}}, "serverInfo": {"name": "decision-e2e", "version": "1"}}
                elif method == "tools/list":
                    result = {"tools": [TOOL]}
                elif method == "tools/call":
                    params = message.get("params", {})
                    started = time.monotonic()
                    try:
                        if params.get("name") != TOOL["name"] or params.get("arguments", {}) != {}:
                            raise ValueError("only the fixed scoped image request is supported")
                        value = execute_image(folder, "sage", data, mode="live",
                            asset_root=project, adapter=adapter, model=adapter.default_model,
                            transport=dispatch)
                        record({"event": "provider_result", "result": value})
                        response = value["response"]
                        answer = response["answers"]["decision"]
                        result = {"content": [{"type": "text", "text": json.dumps({
                            "skill": "screenshot-action-check", "model": response["model"],
                            "answer": answer, "recommendation": value["result"],
                            "usage": response["usage"], "executed_action": False})}]}
                    except Exception as exc:
                        # No upstream bodies/keys or exception repr in the client trace.
                        code = "consent_required" if isinstance(exc, ConsentDenied) else getattr(exc, "code", "error")
                        record({"event": "tool_error", "code": code,
                                "latency_ms": round((time.monotonic() - started) * 1000, 3)})
                        result = {"isError": True, "content": [{"type": "text", "text":
                            "No assessment was made. " + ("Separate user approval is required; no provider request was sent. Stop and ask for consent. Do not change client permissions or retry." if code == "consent_required" else "Backend failed; do not retry. Error: " + str(code))}]}
                else:
                    result = {}
                connection.sendall((json.dumps({"jsonrpc": "2.0", "id": message["id"], "result": result}) + "\n").encode())


def prepare(project, host, setup):
    project.mkdir(parents=True, exist_ok=False)
    root = project / (".agents/skills" if host == "codex" else ".claude/skills")
    if setup == "individual":
        target = root / "screenshot-action-check"
        shutil.copytree(REPO / "skills/screenshot-action-check", target)
    else:
        collection = root / "decision-models-skills"
        collection.mkdir(parents=True)
        shutil.copy2(REPO / "SKILL.md", collection)
        shutil.copytree(REPO / "skills", collection / "skills")
        target = collection / "skills/screenshot-action-check"
    # A copied resource, not an import from the source checkout.
    (project / "selected-skill").symlink_to(target.relative_to(project), target_is_directory=True)
    shutil.copy2(target / "images/frame01.png", project / "example.png")
    readme = (REPO / "README.md").read_text()
    rule = re.search(r"<!-- setup: proactive -->\n```text\n(.*?)\n```", readme, re.S)[1]
    (project / ("AGENTS.md" if host == "codex" else "CLAUDE.md")).write_text(rule + "\n")


def client_environment(environ):
    """Forward only CLI runtime settings; provider credentials stay in runner."""
    return {k: v for k, v in environ.items()
            if k in {"PATH", "HOME", "USER", "LOGNAME", "SHELL", "TMPDIR", "LANG", "LC_ALL",
                     "CODEX_HOME", "SSL_CERT_FILE", "SSL_CERT_DIR"}}


def run(args):
    project = args.directory.resolve() / (args.host + "-" + args.setup)
    if args.phase == "offer":
        prepare(project, args.host, args.setup)
    elif not project.is_dir():
        raise ValueError("run offer first in this directory")
    session_file = project / "session.json"
    session = json.loads(session_file.read_text()) if session_file.exists() else str(uuid.uuid4())
    trace = project / (args.phase + ".jsonl")
    if trace.exists():
        raise ValueError("receipts are immutable; use a fresh directory for a new run")
    address = str(project / "mcp.sock")
    listener = socket.socket(socket.AF_UNIX)
    listener.bind(address)
    os.chmod(address, 0o600)
    listener.listen(1)
    worker = threading.Thread(target=backend, args=(listener, project, args.phase,
                              project / (args.phase + "-provider.jsonl")), daemon=True)
    worker.start()
    server = {"command": sys.executable, "args": [str(Path(__file__).resolve()), "bridge", address]}
    config = project / "mcp.json"
    config.write_text(json.dumps({"mcpServers": {"decision_e2e": server}}))
    env = client_environment(os.environ)
    if args.host == "claude":
        command = ["claude", "--print", "--verbose", "--output-format", "stream-json",
                   "--model", "sonnet", "--effort", "low", "--max-budget-usd",
                   str({"offer": 0.13, "decline": 0.08, "approve": 0.06}[args.phase]),
                   "--setting-sources", "project", "--strict-mcp-config", "--mcp-config", str(config),
                   "--tools", "Read,Skill", "--allowedTools", "Read,Skill,mcp__decision_e2e__sage_image_check",
                   "--session-id" if args.phase == "offer" else "--resume", session, PROMPTS[args.phase]]
    else:
        # Use a dedicated client config, retaining only the existing auth file.
        # This keeps unrelated MCP servers/settings out of the test. No global
        # client setting is changed.
        client_home = project / ".codex-test-home"
        client_home.mkdir(exist_ok=True)
        auth = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "auth.json"
        auth_link = client_home / "auth.json"
        if not auth_link.is_symlink() and not auth_link.exists():
            auth_link.symlink_to(auth)
        env["CODEX_HOME"] = str(client_home)
        command = ["codex", "exec"]
        if args.phase != "offer":
            command += ["resume", session]
        command += ["--skip-git-repo-check", "--json", "-m", "gpt-5.6-sol",
                    "-c", 'model_reasoning_effort="low"',
                    "-c", 'sandbox_mode="read-only"', "-c", 'approval_policy="never"',
                    "-c", 'mcp_servers.decision_e2e.command=' + json.dumps(sys.executable),
                    "-c", 'mcp_servers.decision_e2e.args=' + json.dumps(server["args"])]
        if args.phase == "approve":
            # Only this tool, only in the explicitly approved phase. The
            # application guard still owns scope, one-use consent, and budget.
            command += ["-c", 'mcp_servers.decision_e2e.tools.sage_image_check.approval_mode="approve"']
        command += [PROMPTS[args.phase]]
    started = time.monotonic()
    try:
        with trace.open("w") as output, (project / (args.phase + ".stderr")).open("w") as errors:
            completed = subprocess.run(command, cwd=project, env=env, stdin=subprocess.DEVNULL,
                                       stdout=output, stderr=errors, timeout=180)
        rows = [json.loads(line) for line in trace.read_text().splitlines() if line.strip()]
        if args.host == "codex" and args.phase == "offer":
            session = next(row["thread_id"] for row in rows if row.get("type") == "thread.started")
        session_file.write_text(json.dumps(session))
        usage = [row for row in rows if row.get("type") in {"result", "turn.completed"}]
        summary = {"host": args.host, "setup": args.setup, "phase": args.phase,
                   "exit_code": completed.returncode, "elapsed_seconds": round(time.monotonic() - started, 3),
                   "usage": usage, "source_hashes": {
                       path: hashlib.sha256((REPO / path).read_bytes()).hexdigest()
                       for path in ("README.md", "SKILL.md", "skills/screenshot-action-check/SKILL.md")}}
        (project / (args.phase + "-summary.json")).write_text(json.dumps(summary, indent=2))
        print(json.dumps({key: value for key, value in summary.items() if key != "usage"}))
        return completed.returncode
    finally:
        listener.close()
        Path(address).unlink(missing_ok=True)
        auth_link = project / ".codex-test-home/auth.json"
        if args.host == "codex" and auth_link.is_symlink():
            auth_link.unlink()


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "bridge":
        bridge(sys.argv[2])
        return 0
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", choices=("codex", "claude"), required=True)
    parser.add_argument("--setup", choices=("individual", "collection"), required=True)
    parser.add_argument("--phase", choices=tuple(PROMPTS), required=True)
    parser.add_argument("--directory", type=Path, required=True)
    return run(parser.parse_args())


if __name__ == "__main__":
    sys.exit(main())
