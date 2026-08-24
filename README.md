# Sunnystep Customer-Support AI Agent

A two-process AI customer-support prototype: a Next.js chat UI talking to a FastAPI agent backend that answers policy questions, performs verified order lookups, and safely escalates unsupported requests.

## Features

- Grounded policy/product answers from local Markdown via TF-IDF retrieval
- Verified order lookup with ownership checks and field masking
- Clarification, refusal, and escalation flows
- Structured JSON logging with sensitive-field redaction
- Backend tests (pytest) and scenario runner
- Frontend chat UI with evidence panel

## Non-goals

- Cancellations, refunds, address changes (unsafe mutations)
- Persistent conversation storage
- Distributed tracing or semantic retrieval
- Production auth or rate limiting

## Architecture

```text
Frontend (Next.js, port 3000)
    │
    │  /chat (POST)
    ▼
Backend (FastAPI, port 8000)
    │
    ├─► Agent Core (intent detection, state machine, tool routing)
    │       │
    │       ├─► Retrieval (TF-IDF over Markdown)
    │       │
    │       ├─► Order Service (SQLite lookup + ownership check)
    │       │
    │       └─► LLM (Claude Sonnet - optional, for natural response generation)
    │
    └─► Database (SQLite)
```

**Note:** The agent uses Claude Sonnet for natural response generation when `ANTHROPIC_API_KEY` is configured. Without the key, it falls back to deterministic template responses so the prototype remains runnable.

## Prerequisites

- Node.js ≥ 18
- Python 3.11+
- Anthropic API key (optional - enables Claude-based response generation; prototype works without it)

## Setup

```bash
make install
```

## Run

```bash
make run
```

Or individually:

```bash
make run-backend   # FastAPI on http://localhost:8000
make run-frontend  # Next.js on http://localhost:3000
```

## Stop

```bash
make stop
```

Stops both the FastAPI backend (port 8000) and Next.js frontend (port 3000).

## Test

```bash
make test
```

This runs backend unit tests, frontend unit tests, and the scenario runner.

## Data and Knowledge

- **Structured data**: `backend/data/app.db` (SQLite) - customers, products, orders, order items. Seeded on first run.
- **Unstructured knowledge**: `backend/data/knowledge/*.md` - return policy, shipping policy, product guide, FAQs.
- **Retrieval**: TF-IDF via `scikit-learn`. No external vector store.

## Safety Boundaries

- Order lookup requires order number + email. Three failed attempts → escalation.
- Ownership check is deterministic code; the model cannot bypass it.
- Unsafe requests (cancellations, refunds, address changes) are refused and escalated before any LLM call.
- Prompt injections are detected and handled safely.
- Sensitive fields are masked in order responses and redacted in logs.
- When the LLM is enabled, it only generates responses from pre-validated evidence or order data; it does not control routing or safety decisions.

## Observability

- JSON-line logs to stdout with field redaction for API keys, card numbers, and SSNs.
- Agent state transitions are returned in every `/chat` response.

## Assumptions

- Single-user prototype; SQLite is acceptable for this scope.
- TF-IDF retrieval is sufficient for the small fake dataset.
- Claude Sonnet is used for natural response generation when `ANTHROPIC_API_KEY` is set. Without it, the agent falls back to deterministic template responses.

## Known Limitations

- No distributed tracing or dashboards.
- SQLite is not thread-safe for concurrent writes.
- TF-IDF does not handle paraphrases well.
- No persistent conversation history.
- No rate limiting or distributed auth.

## Decision Summary

| Topic         | Chosen            | Rejected             | Reason                                                |
| ------------- | ----------------- | -------------------- | ----------------------------------------------------- |
| Retrieval     | TF-IDF + Markdown | ChromaDB, embeddings | Zero infra, deterministic, inspectable                |
| Order data    | SQLite            | PostgreSQL, JSON     | Zero infra; Supabase-compatible schema                |
| Orchestration | Vanilla Python    | LangChain            | Every branch is a readable `if`                       |
| Mutations     | Disabled          | Enabled              | Unsafe without full confirmation/idempotency controls |

## Answers to the Five Technical Judgment Questions

1. **What was unsafe to automate, and why?**  
   Cancellations, refunds, and address changes are unsafe because they are irreversible mutations that can cause financial harm. The model cannot reliably verify eligibility conditions (return window, item condition). A misclassified edge case causes real harm with no recovery path.

2. **What would most likely fail first in production, and how would it be detected and contained?**  
   Hallucinated answers when retrieval has no supporting evidence. Detection: log evidence scores and flag answers with low or missing scores. Containment: the agent already says "I cannot verify" when evidence is absent.

3. **What architecture or product choices were made, what alternatives were rejected, and what evidence informed them?**  
   TF-IDF over local Markdown was chosen over embeddings/vector stores because the dataset is small and deterministic retrieval is easier to audit. SQLite was chosen over PostgreSQL because the prototype must run from a ZIP with zero infrastructure. Vanilla Python orchestration was chosen over LangChain because every branch must be explainable during a walkthrough.

4. **What did an AI tool suggest or generate that was rejected, corrected, or improved?**  
   Initial scaffold suggested hardcoding model logic inside API route handlers. This was rejected because it mixes transport, orchestration, and business rules. The code was restructured into `app/core`, `app/services`, and `app/api` layers.

5. **What evidence supports trust today, what remains unproven, and what would be improved first with one additional day?**  
   Trust is supported by unit tests covering happy paths, adversarial paths, ownership checks, and unsafe-request handling. Unproven: end-to-end latency under load, semantic retrieval quality, and long-term conversation handling. First improvement: add a regression test for the discovered defect (order lookup without verification).

## Defect Record

> ## DEFECT-001
>
> - **Scenario:** Customer asks "What is the refund policy?"
> - **Expected behavior:** Agent retrieves and returns the refund policy from knowledge base
> - **Observed behavior:** Agent escalated with "I'm not able to perform cancellations, refunds, or address changes"
> - **Impact and risk:** Informational policy questions are incorrectly refused, breaking a core demo path
> - **Root cause:** Safety check used bare substring "refund" which matches both informational and action requests
> - **Fix:** Changed unsafe list to action-specific phrases ("process a refund", "get a refund") and kept "refund" in knowledge_query keywords
> - **New test or guardrail:** test_chat_policy_query asserts refund policy questions return evidence, not escalation
> - **Evidence before fix:** POST /chat {"messages": [{"role": "user", "content": "What is the refund policy?"}]} returned state=escalated
> - **Evidence after fix:** Same request returns state=ready_to_answer with evidence
> - **Remaining limitation:** Keyword matching may still miss paraphrases
>
> ## DEFECT-002
>
> - **Scenario:** Scenario runner "unknown topic" case ("What is the meaning of life?")
> - **Expected behavior:** Scenario passes - agent returns an in-scope redirect response
> - **Observed behavior:** Scenario always printed FAIL; assertion checked for "couldn't find" / "wasn't able to find" / "not able to find" - none of which appear in GENERAL_FALLBACK_MESSAGE
> - **Impact and risk:** Scenario runner appeared broken on every run; misrepresented test coverage to reviewers
> - **Root cause:** Assertion strings were written against a prior version of GENERAL_FALLBACK_MESSAGE that was later changed; the mismatch was not caught because the runner was not executed against a live server before submission
> - **Fix:** Updated assertion to check state == "ready_to_answer" and "sunnystep" in response content, which correctly characterises the actual fallback behaviour
> - **New test or guardrail:** Scenario runner "unknown topic" case now passes on a live server; test_unknown_question in test_agent_core.py uses the same assertion pattern
> - **Evidence before fix:** python -m scenarios.runner printed "FAIL unknown topic" on every run
> - **Evidence after fix:** Same command prints "PASS unknown topic"
> - **Remaining limitation:** Scenario runner assertions are still string-based; a schema-based check against the full response object would be more robust

## AI-Tool Disclosure

- **Claude Code**: Used for code generation, debugging, and test writing. Every generated suggestion was reviewed against the submission plan before acceptance. One suggestion to embed tool logic in route handlers was rejected and restructured into service/core layers.
