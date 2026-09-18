# Act 01 — Vesper / DIO

## What this act proves

The live demo binds to DIO's existing Presence Bridge. The harness does not recreate customer identity, routing, pricing, payment or fulfilment authority.

The source system currently exposes:

- canonical Vesper Presence health;
- signed ingress with replay protection;
- public/operator trust separation;
- persistent conversation/customer-case state;
- deterministic product routing with bounded Ollama classification fallback;
- attachment quarantine;
- explicit identity binding before order-status disclosure;
- governed quote authority;
- payment evidence gates;
- human/operator boundaries for consequential commercial and fulfilment actions.

## Interview scenario

A training organisation asks for help reviewing 80 assessments consistently, with an audit trail and human approval before marks are released.

Expected narrative:

1. Vesper receives the ambiguous business request.
2. Conversation continuity is established.
3. Intent/product routing resolves the request toward the relevant DIO capability.
4. The response is useful, but no external/commercial authority is created merely by model output.
5. When the workflow reaches a consequential boundary, the source system's policy determines whether it may proceed or becomes Needs You.

## Run

Health only:

```bash
python scripts/act1_vesper.py
```

Live bounded ingress:

```bash
export DIO_PRESENCE_PUBLIC_SHARED_SECRET='...'
python scripts/act1_vesper.py --send
```

The secret must already belong to the local DIO runtime. Never copy production secrets into this repository.

## What to say

> The interesting part isn't that Vesper can talk. Conversation becomes stateful business intent, but the model does not acquire authority just because it produced a plausible answer. Identity, commercial truth and release authority remain separate controls.

## Claim boundary

A successful Act 01 proves this configured local path. It does not prove enterprise-scale load, universal product correctness, legal clearance, or autonomous fulfilment.
