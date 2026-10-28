"""Offline tests for the optional application-level consent example."""
import unittest

from examples.scoped_consent import (
    ConsentDenied,
    ConsentGuard,
    ScopedRequest,
    grant_after_human_approval,
)


class ScopedConsentTests(unittest.TestCase):
    def setUp(self):
        self.request = ScopedRequest(
            "task-1", b'{"image":"original-bytes"}', "backend-a", "model-a", "describe")
        self.guard = ConsentGuard(0.10)
        self.calls = []

    def grant(self, request=None, budget=0.08):
        request = request or self.request
        return grant_after_human_approval(
            task=request.task, data=request.data, backend=request.backend,
            model=request.model, operation=request.operation, budget_usd=budget)

    def transport(self, request):
        self.calls.append((request, self.guard.reserved_usd))
        return "sent"

    def test_missing_approval_is_denied_before_transport(self):
        with self.assertRaises(ConsentDenied):
            self.guard.call(None, self.request, 0.01, self.transport)
        self.assertEqual(self.calls, [])
        self.assertEqual(self.guard.reserved_usd, 0)

    def test_exact_scope_mismatch_is_denied_before_transport(self):
        grant = self.grant()
        mismatches = (
            ScopedRequest("task-2", self.request.data, "backend-a", "model-a", "describe"),
            ScopedRequest("task-1", b'{"image":"changed-bytes"}', "backend-a", "model-a", "describe"),
            ScopedRequest("task-1", self.request.data, "backend-b", "model-a", "describe"),
            ScopedRequest("task-1", self.request.data, "backend-a", "model-b", "describe"),
            ScopedRequest("task-1", self.request.data, "backend-a", "model-a", "classify"),
        )
        for request in mismatches:
            with self.subTest(request=request), self.assertRaises(ConsentDenied):
                self.guard.call(grant, request, 0.01, self.transport)
        self.assertEqual(self.calls, [])
        self.assertEqual(self.guard.reserved_usd, 0)

    def test_approval_budget_and_application_cap_are_checked_before_transport(self):
        grant = self.grant(budget=0.04)
        with self.assertRaises(ConsentDenied):
            self.guard.call(grant, self.request, 0.05, self.transport)
        self.assertEqual(self.calls, [])
        self.assertEqual(self.guard.reserved_usd, 0)

        self.guard = ConsentGuard(0.05)
        self.guard.call(self.grant(budget=0.05), self.request, 0.04, self.transport)
        with self.assertRaises(ConsentDenied):
            self.guard.call(self.grant(budget=0.05), self.request, 0.02, self.transport)
        self.assertEqual(len(self.calls), 1)
        self.assertAlmostEqual(self.guard.reserved_usd, 0.04)

    def test_approval_is_one_use_and_reservation_precedes_transport(self):
        grant = self.grant()
        self.assertEqual(self.guard.call(grant, self.request, 0.03, self.transport), "sent")
        self.assertEqual(self.calls, [(self.request, 0.03)])
        with self.assertRaises(ConsentDenied):
            self.guard.call(grant, self.request, 0.03, self.transport)
        self.assertEqual(len(self.calls), 1)
        self.assertAlmostEqual(self.guard.reserved_usd, 0.03)

    def test_transport_error_keeps_reservation_and_consumes_approval_without_retry(self):
        grant = self.grant()
        attempts = []

        def ambiguous_transport(request):
            attempts.append(request)
            self.assertAlmostEqual(self.guard.reserved_usd, 0.03)
            raise TimeoutError("charge status unknown")

        with self.assertRaises(TimeoutError):
            self.guard.call(grant, self.request, 0.03, ambiguous_transport)
        self.assertEqual(len(attempts), 1)
        self.assertAlmostEqual(self.guard.reserved_usd, 0.03)
        with self.assertRaises(ConsentDenied):
            self.guard.call(grant, self.request, 0.03, ambiguous_transport)
        self.assertEqual(len(attempts), 1)


if __name__ == "__main__":
    unittest.main()
