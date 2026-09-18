# Demo Master Plan

## Objective

Demonstrate role-relevant AI engineering capability through four small, defensible acts backed by existing systems rather than attempting to expose every capability in the portfolio.

## Act 1 — Vesper / DIO

**Question:** Can an AI agent turn ambiguous business intent into useful, governed work?

Target path:

```text
customer request
→ Vesper conversation/context
→ intent/product resolution
→ governed DIO capability
→ commercial/work artifact
→ authority boundary
→ receipt/evidence
```

Build rule: bind to the newest production-facing Vesper/DIO entry points. Do not recreate Vesper inside this repo.

## Act 2 — BEAST

**Question:** Can an engineering agent diagnose, change and verify code without collapsing proposal, approval and execution?

Target path:

```text
small broken repository
→ AgentRun/context
→ Action IR / SourcePlan
→ MCP/tool decision
→ approval when required
→ patch
→ tests/verification
→ Chronicle/evidence
```

The demo repo will contain a deliberately small sacrificial project so the live repair is fast, legible and repeatable.

## Act 3 — Seraph MCP + VNS

**Question:** Can an agent use tools while execution authority and independent observation remain separate?

Target path:

```text
principal + requested capability
→ governance decision / scoped token
→ VNS pre-observation
→ MCP boundary
→ allowed / queued / denied
→ VNS post-observation
→ audit evidence
```

Run one benign crossing and one controlled adversarial crossing. Use the existing Seraph boundary-control implementation rather than inventing demo-only security logic.

## Act 4 — ARDA / Valinor

**Question:** What happens when application-level authorization is not the final trust boundary?

Target read-only path on the actual Valinor laptop:

```text
kernel identity
→ post-boot gate
→ BPF authoritative state
→ measured generation/manifest
→ TPM/PCR attestation state
→ verifier verdict
```

Default to read-only inspection. No interview demo should mutate kernel policy or measured state unless separately rehearsed and explicitly enabled.

## Shared dashboard contract

Each act emits a normalized envelope:

```json
{
  "act": "vesper|beast|seraph|arda",
  "mode": "live|replay|unavailable",
  "status": "ready|running|pass|refuse|needs_you|fail",
  "trace_id": "...",
  "authority": "...",
  "summary": "...",
  "evidence": [],
  "source_provenance": []
}
```

The UI may summarize source systems but must not invent state.

## Preflight

One command should eventually verify:

- DIO/Vesper health
- BEAST health
- Seraph health
- ARDA/Valinor local state
- local model/Ollama availability where required
- evidence fixtures
- demo ports

A failed preflight disables only the affected act and offers an explicitly labelled replay path.

## Build order

1. Act 4 read-only ARDA adapter
2. Act 3 deterministic Seraph MCP/VNS scenario
3. Act 2 BEAST sacrificial repair
4. Act 1 current Vesper production path
5. Unified dashboard and preflight
6. Rehearsal, timing and failure recovery
