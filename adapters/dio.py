"""Act One adapter: Vesper / DIO Presence.

This adapter deliberately talks to the existing local Presence Bridge rather
than reimplementing Vesper. It defaults to read-only health inspection and a
bounded ingress call only when the caller explicitly supplies a signed request.
"""
from __future__ import annotations
import hashlib, hmac, json, time, uuid
from urllib import request, error
from demo_contract import DemoEnvelope

SOURCE = {
    "repository": "Byron2306/DIO-Full-Audit",
    "ref": "snapshot/dio-spine-2026-09-17",
    "paths": "README_PRESENCE.md;scripts/serve_presence_bridge.py;presence_core/engine.py;presence_core/customer_quotes.py",
}

class DIOAdapter:
    def __init__(self, base_url: str = "http://127.0.0.1:8787", timeout: float = 8.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _json(self, method: str, path: str, body: bytes | None = None, headers: dict[str,str] | None = None):
        req = request.Request(self.base_url + path, data=body, method=method, headers=headers or {})
        with request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def health(self) -> DemoEnvelope:
        trace = f"dio-health-{uuid.uuid4().hex[:12]}"
        try:
            data = self._json("GET", "/api/presence/health")
            ready = bool(data.get("ok")) and data.get("presence_identity") == "Vesper"
            return DemoEnvelope(
                act="vesper", mode="live", status="ready" if ready else "fail",
                trace_id=trace,
                authority="presence_health_only",
                summary="Live DIO Presence Bridge reports Vesper ready." if ready else "Presence Bridge responded but did not report canonical Vesper readiness.",
                evidence=[{"kind":"live_health","value":data}],
                source_provenance=[SOURCE],
                details={"automatic_external_actions": data.get("automatic_external_actions"),
                         "attachment_mode": data.get("attachment_mode"),
                         "public_status": data.get("public_status")}
            )
        except Exception as exc:
            return DemoEnvelope(
                act="vesper", mode="unavailable", status="fail", trace_id=trace,
                authority="none", summary=f"DIO Presence Bridge unavailable: {exc}",
                source_provenance=[SOURCE]
            )

    def signed_ingress(self, *, secret: str, envelope: dict, key_id: str = "public-edge") -> DemoEnvelope:
        """Send one real signed Presence ingress message.

        This does NOT enable Telegram replies, payment, fulfilment, file parsing,
        or operator authority. Those remain source-system gates.
        """
        trace = f"dio-ingress-{uuid.uuid4().hex[:12]}"
        body = json.dumps(envelope, separators=(",",":")).encode("utf-8")
        ts = str(int(time.time()))
        nonce = uuid.uuid4().hex
        # Mirrors Presence signing's timestamp + nonce + raw body construction.
        message = ts.encode() + b"." + nonce.encode() + b"." + body
        sig = hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()
        headers = {
            "Content-Type":"application/json",
            "X-DIO-Presence-Signature":sig,
            "X-DIO-Presence-Timestamp":ts,
            "X-DIO-Presence-Nonce":nonce,
            "X-DIO-Presence-Key-Id":key_id,
        }
        try:
            data = self._json("POST","/api/presence/ingress",body,headers)
        except error.HTTPError as exc:
            payload = exc.read().decode("utf-8", errors="replace")
            return DemoEnvelope("vesper","live","refuse",trace,"source_system",
                f"Presence ingress refused with HTTP {exc.code}.",
                evidence=[{"kind":"http_refusal","status":exc.code,"body":payload}],
                source_provenance=[SOURCE])
        except Exception as exc:
            return DemoEnvelope("vesper","unavailable","fail",trace,"none",
                f"Presence ingress unavailable: {exc}",source_provenance=[SOURCE])

        decision = data.get("decision") or {}
        needs = data.get("needs_you") or data.get("needs_you_id")
        status = "needs_you" if needs else "pass"
        return DemoEnvelope(
            act="vesper", mode="live", status=status, trace_id=trace,
            authority="source_system_only",
            summary=f"Vesper processed the customer turn as {decision.get('intent','unknown')} / {decision.get('product') or 'unresolved product'}.",
            evidence=[{"kind":"presence_result","value":data}],
            source_provenance=[SOURCE],
            details={
                "intent":decision.get("intent"), "product":decision.get("product"),
                "confidence":decision.get("confidence"), "needs_you":needs,
                "external_authority_created":False,
            }
        )
