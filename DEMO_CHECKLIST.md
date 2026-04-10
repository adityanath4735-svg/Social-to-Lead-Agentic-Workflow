# Demo + Submission Checklist

## Pre-Recording Setup

- [ ] `python3 --version` is 3.9+
- [ ] Virtual environment is ready (`.venv`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `OPENAI_API_KEY` exported (optional but recommended)
- [ ] Terminal font is readable in recording
- [ ] Microphone/system audio settings checked

## Before You Hit Record

- [ ] Open project root in editor
- [ ] Keep these files visible in file tree:
  - [ ] `agent.py`
  - [ ] `data/knowledge_base.json`
  - [ ] `README.md`
- [ ] Keep `demo_transcript.md` open for guidance
- [ ] Start clean terminal

## Recording Flow (2-3 Minutes)

- [ ] Brief intro: objective + stack (LangGraph + local RAG + lead tool)
- [ ] Run `./run_demo.sh`
- [ ] Ask pricing question: "Hi, tell me about your pricing."
- [ ] Show correct pricing/policy response from local KB
- [ ] Send high-intent query: "I want to try the Pro plan for my YouTube channel."
- [ ] Provide name + email when prompted
- [ ] Show tool print: `Lead captured successfully: ...`
- [ ] Conclude with memory/tool-guard explanation

## Technical Rubric Validation

- [ ] Intent classification covers 3 categories
- [ ] RAG is from local file (`data/knowledge_base.json`)
- [ ] Lead tool is called only after name + email + platform are present
- [ ] State is preserved across multi-turn conversation
- [ ] Code is structured and easy to explain

## Final Repository Checks

- [ ] `README.md` includes:
  - [ ] local run steps
  - [ ] architecture explanation
  - [ ] WhatsApp webhook integration explanation
- [ ] `requirements.txt` is present and complete
- [ ] Demo artifacts included:
  - [ ] `demo_transcript.md`
  - [ ] `run_demo.sh`
  - [ ] `DEMO_CHECKLIST.md`

## Final Submission Package

- [ ] GitHub repository is accessible
- [ ] Demo video link works and is viewable
- [ ] README links/instructions are accurate
- [ ] Last sanity run completed successfully
