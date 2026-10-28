"""Offline exercise of the real MCP boundary used by opt-in client tests."""
import json
import os
from pathlib import Path
import socket
import tempfile
import threading
import unittest
from unittest.mock import patch

from scripts.agent_e2e import backend, client_environment, prepare
from tests.test_sage_image_model_selection import raw_response


class AgentE2EBoundaryTests(unittest.TestCase):
    def test_clients_receive_no_provider_credentials_or_unrelated_environment(self):
        env = client_environment({"PATH": "/bin", "HOME": "/tmp/home",
                                  "SAGE_API_KEY": "synthetic", "SAGE_KEY": "synthetic",
                                  "API_PASSWORD": "synthetic", "CREDENTIAL": "synthetic",
                                  "PYTHONPATH": "/unsafe", "CLAUDECODE": "nested"})
        self.assertEqual(env, {"PATH": "/bin", "HOME": "/tmp/home"})

    def test_real_mcp_transport_requires_trusted_one_use_approval(self):
        for phase, probability in (("offer", 0.9), ("decline", 0.9),
                                   ("approve", 0.9), ("approve", 0.6)):
            with self.subTest(phase=phase, probability=probability), tempfile.TemporaryDirectory(prefix="dm-e2e-") as tmp:
                project = Path(tmp) / "client"
                prepare(project, "claude", "individual")
                journal = project / "provider.jsonl"
                raw = raw_response("levanto-sage-2")
                selected = raw["results"][0]["answers"][0]["result"]["result"]
                selected["probability"] = probability
                probabilities = selected["probabilities"]
                probabilities[0]["probability"] = probability
                probabilities[1]["probability"] = (1 - probability) / 2
                probabilities.append({"option": "not_visible", "probability": (1 - probability) / 2})
                server_socket, client_socket = socket.socketpair()
                class Listener:
                    def __enter__(self):
                        return self
                    def __exit__(self, *args):
                        server_socket.close()
                    def accept(self):
                        return server_socket, None
                listener = Listener()
                with patch.dict(os.environ, {"SAGE_API_KEY": "synthetic-test-only"}), \
                     patch("decision_models.transport.http_transport", return_value=raw) as transport:
                    worker = threading.Thread(target=backend,
                        args=(listener, project, phase, journal), daemon=True)
                    worker.start()
                    with client_socket as client:
                        client.settimeout(5)
                        reader = client.makefile("rb")
                        def call(number, arguments):
                            message = {"jsonrpc": "2.0", "id": number, "method": "tools/call",
                                       "params": {"name": "sage_image_check", "arguments": arguments}}
                            client.sendall((json.dumps(message) + "\n").encode())
                            return json.loads(reader.readline())["result"]
                        # A model cannot create consent by putting approval in its arguments.
                        self.assertTrue(call(1, {"approved": True})["isError"])
                        first = call(2, {})
                        second = call(3, {})
                        self.assertTrue(second["isError"])
                        if phase == "approve":
                            self.assertNotIn("isError", first)
                            payload = json.loads(first["content"][0]["text"])
                            self.assertEqual(payload["model"], "levanto-sage-2")
                            self.assertEqual(payload["answer"]["choice"], "visible")
                            self.assertEqual(payload["recommendation"]["choice"],
                                             "review" if probability < 0.8 else "visible")
                            self.assertIsNone(payload["answer"]["confidence"])
                            transport.assert_called_once()
                        else:
                            self.assertTrue(first["isError"])
                            transport.assert_not_called()
                        reader.close()
                    worker.join(timeout=5)
                    self.assertFalse(worker.is_alive())
                rows = [json.loads(line) for line in journal.read_text().splitlines()]
                self.assertEqual(sum(row["event"] == "provider_dispatch" for row in rows),
                                 int(phase == "approve"))


if __name__ == "__main__":
    unittest.main()
