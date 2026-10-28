"""Optional, offline example of a caller-owned consent gate for paid model calls.

This is an application integration pattern, not part of the instruction-only
skills and not a source of trusted consent by itself. Only a trusted caller
(for example, an approval UI) may construct a ConsentGrant after the person
approves the displayed scope. Do not expose grant construction or this guard
to the model as a tool. This small in-process example cannot prove provenance,
persist grants, or coordinate budgets across processes.
"""
from dataclasses import dataclass
import hashlib
import math
from typing import Callable, Optional


class ConsentDenied(Exception):
    """A request did not match unused consent or could not fit its spend cap."""


@dataclass(frozen=True)
class ScopedRequest:
    """Exact request bytes and the human-readable scope sent to a backend."""

    task: str
    data: bytes
    backend: str
    model: str
    operation: str

    @property
    def data_sha256(self) -> str:
        return hashlib.sha256(self.data).hexdigest()


@dataclass(frozen=True, eq=False)
class ConsentGrant:
    """One-use approval scoped to a task, exact bytes, backend, model and action.

    Construct this only in trusted application code after a person approves
    the full scope. The type is deliberately not cryptographic proof of that
    approval; an agent able to construct grants can manufacture consent.
    """

    task: str
    data_sha256: str
    backend: str
    model: str
    operation: str
    budget_usd: float


def grant_after_human_approval(*, task: str, data: bytes, backend: str,
                               model: str, operation: str,
                               budget_usd: float) -> ConsentGrant:
    """Build a grant from the exact scope approved by a trusted caller.

    Keep this function in the trusted caller boundary; never let model output
    choose its arguments or call it. A real application should create the
    grant only after its own approval UI has recorded the user's choice.
    """
    if not isinstance(data, bytes):
        raise ValueError("data must be the exact bytes that will be sent")
    if not all(isinstance(value, str) and value.strip() for value in
               (task, backend, model, operation)):
        raise ValueError("task, backend, model, and operation must be explicit")
    if (isinstance(budget_usd, bool) or not isinstance(budget_usd, (int, float))
            or not math.isfinite(budget_usd) or budget_usd <= 0):
        raise ValueError("approved budget must be a finite positive amount")
    return ConsentGrant(task, hashlib.sha256(data).hexdigest(), backend,
                        model, operation, float(budget_usd))


class ConsentGuard:
    """One-process spend cap; reserve before transport and never auto-retry."""

    def __init__(self, limit_usd: float):
        if (isinstance(limit_usd, bool) or not isinstance(limit_usd, (int, float))
                or not math.isfinite(limit_usd) or limit_usd <= 0):
            raise ValueError("limit must be a finite positive amount")
        self.limit_usd = float(limit_usd)
        self.reserved_usd = 0.0
        self._used: set[ConsentGrant] = set()

    def call(self, grant: Optional[ConsentGrant], request: ScopedRequest,
             estimated_usd: float, transport: Callable[[ScopedRequest], object]):
        """Authorize one call, reserve its estimate, then invoke transport once.

        A timeout or any other transport exception keeps the reservation and
        consumes the grant because charge status may be unknown. The caller
        must not automatically retry this paid operation.
        """
        if grant is None or not isinstance(grant, ConsentGrant):
            raise ConsentDenied("trusted caller approval is required")
        if not isinstance(request, ScopedRequest) or not isinstance(request.data, bytes):
            raise ConsentDenied("request must contain the exact transport bytes")
        expected = (grant.task, grant.data_sha256, grant.backend, grant.model, grant.operation)
        actual = (request.task, request.data_sha256, request.backend, request.model, request.operation)
        if actual != expected:
            raise ConsentDenied("request does not match the approved task, data, backend, model, and operation")
        if grant in self._used:
            raise ConsentDenied("approval has already been used")
        if (isinstance(estimated_usd, bool) or not isinstance(estimated_usd, (int, float))
                or not math.isfinite(estimated_usd) or estimated_usd <= 0):
            raise ConsentDenied("reservation must be a finite positive amount")
        if estimated_usd > grant.budget_usd:
            raise ConsentDenied("reservation exceeds the approved spend")
        if self.reserved_usd + estimated_usd > self.limit_usd:
            raise ConsentDenied("reservation exceeds the remaining application spend cap")

        # Consume and reserve before crossing the paid transport boundary.
        self._used.add(grant)
        self.reserved_usd += float(estimated_usd)
        return transport(request)


def _offline_demo() -> None:
    payload = b'{"prompt":"Describe this image","image":"image-bytes-v1"}'
    request = ScopedRequest("task-42", payload, "example-backend", "example-model",
                            "describe-image")
    calls = []

    def fake_transport(outbound: ScopedRequest):
        calls.append(outbound)
        return {"ok": True, "sent_sha256": outbound.data_sha256}

    guard = ConsentGuard(limit_usd=0.20)
    try:
        guard.call(None, request, 0.08, fake_transport)
    except ConsentDenied as exc:
        print("Denied without trusted approval:", exc)

    approval = grant_after_human_approval(
        task=request.task, data=request.data, backend=request.backend,
        model=request.model, operation=request.operation, budget_usd=0.10)
    print("Approved call:", guard.call(approval, request, 0.08, fake_transport))
    print("Reserved USD:", f"{guard.reserved_usd:.2f}", "transport calls:", len(calls))

    try:
        guard.call(approval, request, 0.08, fake_transport)
    except ConsentDenied as exc:
        print("Denied reuse:", exc)

    changed = ScopedRequest(request.task, b'{"prompt":"Describe this other image"}',
                            request.backend, request.model, request.operation)
    changed_approval = grant_after_human_approval(
        task=request.task, data=request.data, backend=request.backend,
        model=request.model, operation=request.operation, budget_usd=0.10)
    try:
        guard.call(changed_approval, changed, 0.08, fake_transport)
    except ConsentDenied as exc:
        print("Denied changed image bytes:", exc)
    print("Final transport calls:", len(calls))


if __name__ == "__main__":
    _offline_demo()
