import json
import re
import logging
from typing import TypedDict
from langgraph.graph import StateGraph, END
from src.memory import ShortTermMemory, LongTermMemory, EpisodicMemory, SemanticMemory
from src.memory.redis_long_term import RedisLongTermMemory
from src.providers import chat
from src.tokens import count_tokens
from openai.types.chat import ChatCompletionMessageParam

# --- Memory backends (shared instances) ---
short_term = ShortTermMemory(max_turns=10)
long_term = RedisLongTermMemory()  # uses Redis if REDIS_URL set, else JSON fallback
episodic = EpisodicMemory()
semantic = SemanticMemory()

MEMORY_BUDGET = 500  # max tokens for injected memory


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
    # Trim to token budget
    while count_tokens(system) > state["memory_budget"] and "\n" in system:
        system = system[:system.rfind("\n")]
    return system


def call_llm(state: MemoryState) -> MemoryState:
    system_prompt = build_prompt(state)
    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": system_prompt},
        *[{"role": m["role"], "content": m["content"]} for m in state["messages"]],  # type: ignore
    ]
    reply = chat(messages)
    state["messages"].append({"role": "assistant", "content": reply})
    return state


def save_memory(state: MemoryState) -> MemoryState:
    last_user = next(
        (m["content"] for m in reversed(state["messages"]) if m["role"] == "user"), ""
    )
    last_reply = next(
        (m["content"] for m in reversed(state["messages"]) if m["role"] == "assistant"), ""
    )

    # Extract profile facts via LLM
    extract_prompt: list[ChatCompletionMessageParam] = [
        {
            "role": "system",
            "content": (
                "Trích xuất thông tin cá nhân từ tin nhắn người dùng dưới dạng JSON key-value. "
                "Chỉ trả về JSON object, không giải thích. "
                "Ví dụ: {\"name\": \"Khang\", \"allergy\": \"đậu nành\"}. "
                "Nếu không có thông tin, trả về {}."
            ),
        },
        {"role": "user", "content": last_user},
    ]
    try:
        raw = chat(extract_prompt).strip()
        logger = logging.getLogger(__name__)
        # Strip markdown code fences if present
        raw = re.sub(r"```(?:json)?", "", raw).strip()
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            logger.warning("LLM extraction: no JSON found in response: %s", raw[:100])
        else:
            parsed = json.loads(match.group())
            if not isinstance(parsed, dict):
                logger.warning("LLM extraction: expected dict, got %s", type(parsed))
            else:
                for k, v in parsed.items():
                    if isinstance(k, str) and v not in (None, "", [], {}):
                        long_term.save(k, v)
    except json.JSONDecodeError as e:
        logging.getLogger(__name__).warning("LLM extraction JSON parse error: %s", e)
    except Exception as e:
        logging.getLogger(__name__).warning("LLM extraction failed: %s", e)

    # Save episodic if outcome detected
    outcome_keywords = ["xong", "done", "fixed", "thành công", "hoàn thành", "ok", "được rồi"]
    if any(kw in last_user.lower() or kw in last_reply.lower() for kw in outcome_keywords):
        episodic.save({"task": last_user[:80], "outcome": last_reply[:120]})

    # Ingest assistant reply into semantic store
    if last_reply:
        import hashlib
        doc_id = hashlib.md5(last_reply.encode()).hexdigest()
        semantic.save(last_reply, doc_id)

    return state


# --- Graph ---
def build_graph() -> StateGraph:
    g = StateGraph(MemoryState)
    g.add_node("retrieve_memory", retrieve_memory)
    g.add_node("call_llm", call_llm)
    g.add_node("save_memory", save_memory)
    g.set_entry_point("retrieve_memory")
    g.add_edge("retrieve_memory", "call_llm")
    g.add_edge("call_llm", "save_memory")
    g.add_edge("save_memory", END)
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
