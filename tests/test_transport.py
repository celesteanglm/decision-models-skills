import json
import socket
import unittest
import urllib.error
from unittest.mock import patch

from decision_models.contracts import DecisionError
from decision_models.transport import http_transport


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, size=-1):
        return self.body[:size]


class TransportTests(unittest.TestCase):
    def test_posts_json_with_bearer_auth_and_bounded_timeout(self):
        holder = {}

        class Opener:
            def open(self, request, timeout):
                holder["request"] = request
                holder["timeout"] = timeout
                return FakeResponse(b'{"ok":true}')

        with patch("decision_models.transport.urllib.request.build_opener", return_value=Opener()):
            result = http_transport("https://provider.invalid/path", {"text": "café"}, "secret", 7)
        request = holder["request"]
        self.assertEqual(result, {"ok": True})
        self.assertEqual(request.method, "POST")
        self.assertEqual(request.get_header("Authorization"), "Bearer secret")
        self.assertEqual(request.get_header("Content-type"), "application/json")
        self.assertEqual(json.loads(request.data), {"text": "café"})
        self.assertEqual(holder["timeout"], 7)

    def test_malformed_json_and_oversized_bodies_are_rejected(self):
        for body in (b"not json", b"[]", b"x" * 4_000_001):
            class Opener:
                def open(self, *args, **kwargs):
                    return FakeResponse(body)
            with patch("decision_models.transport.urllib.request.build_opener", return_value=Opener()):
                with self.subTest(size=len(body)), self.assertRaises(DecisionError) as caught:
                    http_transport("https://provider.invalid", {}, "secret")
                self.assertEqual(caught.exception.code, "invalid_response")

    def test_provider_http_failures_are_classified_and_only_429_is_retryable(self):
        expected = {401: ("authentication", False), 403: ("permission", False),
                    402: ("insufficient_credits", False), 404: ("endpoint_unavailable", False),
                    429: ("rate_limited", True), 500: ("upstream_failure", False)}
        for status, (code, retryable) in expected.items():
            error = urllib.error.HTTPError("https://provider.invalid", status, "failed", {}, None)

            class Opener:
                def open(self, *args, **kwargs):
                    raise error
            with patch("decision_models.transport.urllib.request.build_opener", return_value=Opener()):
                with self.subTest(status=status), self.assertRaises(DecisionError) as caught:
                    http_transport("https://provider.invalid", {}, "secret")
            self.assertEqual(caught.exception.code, code)
            self.assertEqual(caught.exception.retryable, retryable)
            self.assertEqual(caught.exception.status, status)

    def test_timeouts_preserve_unknown_charge_status_and_are_not_retryable(self):
        class Opener:
            def open(self, *args, **kwargs):
                raise socket.timeout()
        with patch("decision_models.transport.urllib.request.build_opener", return_value=Opener()):
            with self.assertRaises(DecisionError) as caught:
                http_transport("https://provider.invalid", {}, "secret")
        self.assertEqual(caught.exception.code, "timeout")
        self.assertFalse(caught.exception.retryable)
        self.assertIn("charge status is unknown", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
