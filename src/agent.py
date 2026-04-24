from typing import TypedDict
from langgraph.graph import StateGraph, END
from src.memory import ShortTermMemory, LongTermMemory, EpisodicMemory, SemanticMemory
from src.providers import chat
from openai.types.chat import ChatCompletionMessageParam

# --- Memory backends (shared instances) ---
short_term = ShortTermMemory(max_turns=10)
long_term = LongTermMemory()
episodic = EpisodicMemory()
semantic = SemanticMemory()

MEMORY_BUDGET = 2000  # max chars for injected memory


# --- State ---
class MemoryState(TypedDict):
    messages: list[dict]
    user_profile: dict
    episodes: list[dict]
    semantic_hits: list[str]
    memory_budget: int


# --- Nodes ---
def retrieve_memory(state: MemoryState) -> MemoryState:
    last_user = next(
        (m["content"] for m in reversed(state["messages"]) if m["role"] == "user"), ""
    )
    state["user_profile"] = long_term.all()
    state["episodes"] = episodic.retrieve(n=5)
    state["semantic_hits"] = semantic.retrieve(last_user, n_results=3) if last_user else []
    state["memory_budget"] = MEMORY_BUDGET
    return state


def build_prompt(state: MemoryState) -> str:
    profile_str = "\n".join(f"- {k}: {v}" for k, v in state["user_profile"].items())
    episodes_str = "\n".join(
        f"- [{e.get('task','')}] {e.get('outcome','')}" for e in state["episodes"]
    )
    semantic_str = "\n".join(f"- {s}" for s in state["semantic_hits"])
    recent = "\n".join(
        f"{m['role']}: {m['content']}" for m in state["messages"][-4:]
    )

    system = f"""Bạn là trợ lý AI có bộ nhớ đầy đủ.

## Profile
{profile_str or '(trống)'}

## Episodic Memory
{episodes_str or '(trống)'}

## Semantic Knowledge
{semantic_str or '(trống)'}

## Recent Conversation
{recent or '(trống)'}
"""
    # Trim to budget
    return system[: state["memory_budget"]]


def call_llm(state: MemoryState) -> MemoryState:
    system_prompt = build_prompt(state)
    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": system_prompt},
        *[{"role": m["role"], "content": m["content"]} for m in state["messages"]],  # type: ignore
    ]
    reply = chat(messages)
    state["messages"].append({"role": "assistant", "content": reply})
    return state


# --- Graph ---
def build_graph() -> StateGraph:
    g = StateGraph(MemoryState)
    g.add_node("retrieve_memory", retrieve_memory)
    g.add_node("call_llm", call_llm)
    g.set_entry_point("retrieve_memory")
    g.add_edge("retrieve_memory", "call_llm")
    g.add_edge("call_llm", END)
    return g.compile()


graph = build_graph()


# --- Entry point ---
def run_agent(user_input: str) -> str:
    short_term.add("user", user_input)
    state: MemoryState = {
        "messages": short_term.get().copy(),
        "user_profile": {},
        "episodes": [],
        "semantic_hits": [],
        "memory_budget": MEMORY_BUDGET,
    }
    result = graph.invoke(state)
    reply = result["messages"][-1]["content"]
    short_term.add("assistant", reply)
    return reply
