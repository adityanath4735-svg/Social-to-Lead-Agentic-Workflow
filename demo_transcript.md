# Demo Transcript (2–3 Minutes)

Use this script while screen recording to cover every rubric checkpoint.

## 1) Start + Intro (10–15 sec)

Say:
"This is a LangGraph-based Social-to-Lead agent for AutoStream. It classifies intent, retrieves plan/policy info from a local knowledge base, and captures high-intent leads via a guarded tool call."

Show:
- Project files in editor: `agent.py`, `data/knowledge_base.json`, `README.md`

## 2) Run the Agent (10 sec)

Command:
```bash
./run_demo.sh
```

## 3) Pricing/RAG Question (30–40 sec)

User input:
`Hi, tell me about your pricing.`

What to point out:
- Agent returns Basic and Pro plan details from local KB.
- This demonstrates product/pricing inquiry intent + retrieval.

## 4) Intent Shift to High-Intent (25–35 sec)

User input:
`That sounds good, I want to try the Pro plan for my YouTube channel.`

What to point out:
- Agent recognizes high intent.
- Agent starts qualification by asking for missing lead details.

## 5) Multi-turn Detail Collection (30–40 sec)

User input sequence:
1. `Aditya`
2. `aditya@example.com`

What to point out:
- Agent remembers earlier platform ("YouTube") from the high-intent sentence.
- Agent waits until required fields are complete.

## 6) Successful Tool Execution (20–30 sec)

Expected terminal print:
`Lead captured successfully: Aditya, aditya@example.com, Youtube`

What to point out:
- Tool call happens only after name + email + platform are all present.
- No premature trigger.

## 7) Close (10 sec)

Say:
"This implementation uses LangGraph state + checkpoint memory for multi-turn context and can be connected to WhatsApp via webhooks as described in the README."
