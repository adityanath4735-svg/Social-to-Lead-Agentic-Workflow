import json
import os
import re
from pathlib import Path
from typing import Annotated, Literal, Optional, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages


load_dotenv()


class LeadData(TypedDict):
    name: Optional[str]
    email: Optional[str]
    platform: Optional[str]


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    intent: Literal["casual_greeting", "product_pricing_inquiry", "high_intent_lead"]
    lead: LeadData
    tool_called: bool


SUPPORTED_PLATFORMS = [
    "youtube",
    "instagram",
    "tiktok",
    "linkedin",
    "facebook",
    "x",
    "twitter",
    "podcast",
]

NON_NAME_SHORT_REPLIES = {
    "hi",
    "hello",
    "hey",
    "thanks",
    "thank you",
    "ok",
    "okay",
    "cool",
    "great",
    "yes",
    "yep",
    "no",
    "nope",
}


def get_llm() -> Optional[ChatOpenAI]:
    if os.getenv("OPENAI_API_KEY"):
        return ChatOpenAI(model="gpt-4o-mini", temperature=0)
    return None


def mock_lead_capture(name: str, email: str, platform: str) -> None:
    print(f"Lead captured successfully: {name}, {email}, {platform}")


def load_knowledge_base() -> dict:
    kb_path = Path(__file__).parent / "data" / "knowledge_base.json"
    with kb_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def intent_classifier(text: str) -> Literal["casual_greeting", "product_pricing_inquiry", "high_intent_lead"]:
    lowered = text.lower()

    high_intent_keywords = [
        "sign up",
        "signup",
        "get started",
        "start trial",
        "i want to try",
        "i want pro",
        "i'll buy",
        "let's do it",
        "book demo",
        "ready",
    ]
    inquiry_keywords = [
        "price",
        "pricing",
        "cost",
        "feature",
        "plan",
        "refund",
        "support",
        "resolution",
        "captions",
    ]
    greeting_keywords = ["hi", "hello", "hey", "good morning", "good evening"]

    if any(keyword in lowered for keyword in high_intent_keywords):
        return "high_intent_lead"
    if any(keyword in lowered for keyword in inquiry_keywords):
        return "product_pricing_inquiry"
    if any(keyword in lowered for keyword in greeting_keywords):
        return "casual_greeting"
    return "product_pricing_inquiry"


def extract_lead_fields(text: str, lead: LeadData) -> LeadData:
    updated = dict(lead)
    lowered = text.lower()

    if not updated.get("email"):
        email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", text)
        if email_match:
            updated["email"] = email_match.group(0)

    if not updated.get("platform"):
        for platform in SUPPORTED_PLATFORMS:
            if platform in lowered:
                updated["platform"] = "X (Twitter)" if platform in {"x", "twitter"} else platform.capitalize()
                break

    if not updated.get("name"):
        explicit_name = re.search(r"\bmy name is ([A-Za-z][A-Za-z\s'-]{1,40})\b", lowered)
        if explicit_name:
            updated["name"] = explicit_name.group(1).strip().title()
        else:
            short_reply = text.strip()
            if (
                short_reply.lower() not in NON_NAME_SHORT_REPLIES
                and
                "@" not in short_reply
                and 1 <= len(short_reply.split()) <= 3
                and all(token.isalpha() or "-" in token or "'" in token for token in short_reply.split())
            ):
                updated["name"] = " ".join(word.capitalize() for word in short_reply.split())

    return updated  # type: ignore[return-value]


def retrieve_context(query: str, kb: dict) -> str:
    snippets: list[str] = []
    for plan in kb["plans"]:
        snippets.append(f'{plan["name"]}: {plan["price"]}. Features: {", ".join(plan["features"])}.')
    for policy in kb["policies"]:
        snippets.append(f"Policy: {policy}.")

    query_terms = set(re.findall(r"[a-zA-Z]+", query.lower()))
    scored: list[tuple[int, str]] = []
    for snippet in snippets:
        snippet_terms = set(re.findall(r"[a-zA-Z]+", snippet.lower()))
        score = len(query_terms.intersection(snippet_terms))
        scored.append((score, snippet))

    top = [snippet for score, snippet in sorted(scored, reverse=True)[:3] if score > 0]
    if not top:
        top = snippets[:2]
    return "\n".join(top)


def detect_intent_node(state: AgentState) -> AgentState:
    latest_user = state["messages"][-1].content
    intent = intent_classifier(latest_user)
    existing_lead = state.get("lead") or {"name": None, "email": None, "platform": None}
    updated_lead = extract_lead_fields(latest_user, existing_lead)
    return {"intent": intent, "lead": updated_lead}


def route_from_intent(state: AgentState) -> str:
    lead = state.get("lead", {"name": None, "email": None, "platform": None})
    has_partial_lead = any(lead.get(field) for field in ("name", "email", "platform"))
    if state["intent"] == "high_intent_lead" or has_partial_lead:
        return "lead_qualification"
    if state["intent"] == "casual_greeting":
        return "greet"
    return "rag_response"


def greeting_node(_: AgentState) -> AgentState:
    reply = (
        "Hi! I can help with AutoStream pricing, features, and policies. "
        "Ask me anything about plans, and if you want to get started I can capture your details."
    )
    return {"messages": [AIMessage(content=reply)]}


def rag_response_node(state: AgentState) -> AgentState:
    kb = load_knowledge_base()
    query = state["messages"][-1].content
    context = retrieve_context(query, kb)
    llm = get_llm()

    if llm:
        prompt = (
            "You are an AutoStream sales assistant. Answer only using the provided context. "
            "If something is missing in context, say you do not have that policy detail.\n\n"
            f"Context:\n{context}\n\n"
            f"User question: {query}\n\n"
            "Answer in a concise and friendly way."
        )
        llm_answer = llm.invoke(prompt).content
        response = f"{llm_answer}\n\nIf you want, I can help you choose the right plan."
    else:
        response = (
            "Here is what I found from AutoStream's knowledge base:\n"
            f"{context}\n\n"
            "If you want, I can also help you choose the right plan based on your content workflow."
        )
    return {"messages": [AIMessage(content=response)]}


def lead_qualification_node(state: AgentState) -> AgentState:
    lead = state["lead"]
    missing = [field for field in ("name", "email", "platform") if not lead.get(field)]

    if not missing and not state.get("tool_called", False):
        mock_lead_capture(lead["name"], lead["email"], lead["platform"])  # type: ignore[arg-type]
        reply = (
            "Perfect, I have all your details and captured your lead successfully. "
            "Our team will reach out to you shortly."
        )
        return {"tool_called": True, "messages": [AIMessage(content=reply)]}

    if missing:
        prompts = {
            "name": "your name",
            "email": "your email address",
            "platform": "your creator platform (YouTube, Instagram, etc.)",
        }
        ask_for = ", ".join(prompts[item] for item in missing)
        reply = (
            "Great to hear you are interested in AutoStream. "
            f"To get you set up, could you share {ask_for}?"
        )
        return {"messages": [AIMessage(content=reply)]}

    return {"messages": [AIMessage(content="Your lead is already captured. Let me know if you need anything else.")] }


def build_agent():
    graph = StateGraph(AgentState)
    graph.add_node("detect_intent", detect_intent_node)
    graph.add_node("greet", greeting_node)
    graph.add_node("rag_response", rag_response_node)
    graph.add_node("lead_qualification", lead_qualification_node)

    graph.set_entry_point("detect_intent")
    graph.add_conditional_edges(
        "detect_intent",
        route_from_intent,
        {
            "greet": "greet",
            "rag_response": "rag_response",
            "lead_qualification": "lead_qualification",
        },
    )
    graph.add_edge("greet", END)
    graph.add_edge("rag_response", END)
    graph.add_edge("lead_qualification", END)

    memory = MemorySaver()
    return graph.compile(checkpointer=memory)


def run_cli() -> None:
    agent = build_agent()
    config = {"configurable": {"thread_id": "autostream-demo"}}

    print("AutoStream Agent is live. Type 'exit' to quit.")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Agent: Bye! Feel free to come back anytime.")
            break

        result = agent.invoke(
            {"messages": [HumanMessage(content=user_input)]},
            config=config,
        )
        print(f"Agent: {result['messages'][-1].content}")


if __name__ == "__main__":
    run_cli()
