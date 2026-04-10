# Social-to-Lead Agentic Workflow (AutoStream)

This repository contains a conversational AI agent for a fictional SaaS company, **AutoStream**.  
The agent is designed to move users from social-style conversation to qualified lead capture.

## Features Implemented

- Intent classification into:
  - `casual_greeting`
  - `product_pricing_inquiry`
  - `high_intent_lead`
- Local RAG-style retrieval from `data/knowledge_base.json`
- Lead qualification flow for `name`, `email`, and `platform`
- Guarded tool execution with:
  - `mock_lead_capture(name, email, platform)`
  - tool runs **only after all three required fields are present**
- Multi-turn conversation memory using LangGraph state + checkpointing

## Project Structure

- `agent.py` - LangGraph workflow, state schema, intent logic, retrieval, and lead capture
- `data/knowledge_base.json` - Pricing, features, and company policy knowledge base
- `requirements.txt` - Python dependencies
- `run_demo.sh` - One-command setup and demo runner
- `demo_transcript.md` - Suggested 2-3 minute demo script
- `DEMO_CHECKLIST.md` - Pre-recording and submission checklist

## How to Run Locally

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. (Optional) Set LLM key for `gpt-4o-mini` generation:

```bash
export OPENAI_API_KEY="your_key_here"
```

4. Run the agent:

```bash
python agent.py
```

Or use the demo helper:

```bash
./run_demo.sh
```

## Example Conversation

- User: `Hi, tell me about your pricing.`
- User: `That sounds good, I want to try the Pro plan for my YouTube channel.`
- User: `Aditya`
- User: `aditya@example.com`

Expected behavior:
- The agent answers pricing/policy from local KB context.
- The agent detects high intent and asks for missing lead fields.
- `mock_lead_capture(...)` runs only after all required fields are collected.

## Architecture Explanation

I chose **LangGraph** because this problem is a stateful workflow, not a single prompt-response task.  
The solution has clear stages: intent detection, knowledge retrieval, and lead qualification/tool execution.  
LangGraph makes these stages explicit through graph nodes and routing, which improves control, traceability, and reliability.

State is managed through a typed `AgentState` that stores:
- conversation messages
- latest intent label
- partial lead fields (`name`, `email`, `platform`)
- a `tool_called` guard flag

Memory is persisted with `MemorySaver` checkpointing and a fixed `thread_id`, so the agent retains context across 5-6+ turns.  
On each turn, the latest user input is parsed to update lead fields. If fields are missing, the agent asks only for the missing values.  
When all three fields are available, the agent triggers `mock_lead_capture(...)` once and confirms success.  
This design prevents premature tool calls and mirrors real lead-qualification behavior used in production assistant workflows.

## WhatsApp Deployment via Webhooks

To deploy this agent on WhatsApp, I would use the **WhatsApp Business Cloud API** with a webhook backend:

1. Configure Meta webhook endpoint (for example, `/webhook`) to receive message events.
2. Validate webhook tokens during setup and secure all webhook requests.
3. For each incoming WhatsApp message:
   - map sender id to a stable LangGraph `thread_id`
   - call `agent.invoke(...)` with the incoming text
   - persist checkpoints in Redis/Postgres for horizontal scalability
4. Send the generated reply back via WhatsApp send-message API.
5. When lead capture completes, forward lead data to CRM (HubSpot/Salesforce/internal service).
6. Add production safeguards: retries, idempotency keys, structured logs, and dead-letter queues.

This keeps the core agent logic unchanged while swapping only the transport layer (CLI to WhatsApp).
