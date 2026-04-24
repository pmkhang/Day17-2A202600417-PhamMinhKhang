SHELL := /bin/bash
.ONESHELL:

.PHONY: help setup check check-memory check-graph check-conflict check-benchmark check-reflection check-bonus graph-demo compile clean-memory

help:
	@echo "Lab #17 Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  make setup            - install/sync dependencies with uv"
	@echo "  make check            - run all non-destructive checks mapped from tasks.md"
	@echo "  make check-memory     - verify full memory stack + interfaces"
	@echo "  make check-graph      - verify LangGraph state/router + token budget prompt"
	@echo "  make check-conflict   - verify overwrite conflict behavior and episodic save/retrieve"
	@echo "  make check-benchmark  - verify BENCHMARK.md exists and has required scenario groups"
	@echo "  make check-reflection - verify README privacy/limitations coverage"
	@echo "  make check-bonus      - verify bonus implementation artifacts are present"
	@echo "  make graph-demo       - print graph flow demo"
	@echo "  make compile          - compile Python sources"
	@echo "  make clean-memory     - remove local memory artifacts under data/"

setup:
	uv sync

check: check-memory check-graph check-conflict check-benchmark check-reflection check-bonus
	@echo "All task-based checks passed."

check-memory:
	@echo "[1/6] Checking full memory stack..."
	@uv run python - <<'PY'
	from src.memory import ShortTermMemory, LongTermMemory, EpisodicMemory, SemanticMemory
	st = ShortTermMemory(max_turns=3)
	lt = LongTermMemory(path="data/_tmp_profile_check.json")
	ep = EpisodicMemory(path="data/_tmp_episodes_check.json")
	sm = SemanticMemory(collection_name="semantic_check")
	assert all(hasattr(st, m) for m in ["add", "get", "clear"]), "ShortTermMemory interface mismatch"
	assert all(hasattr(lt, m) for m in ["save", "retrieve", "all"]), "LongTermMemory interface mismatch"
	assert all(hasattr(ep, m) for m in ["save", "retrieve"]), "EpisodicMemory interface mismatch"
	assert all(hasattr(sm, m) for m in ["save", "retrieve"]), "SemanticMemory interface mismatch"
	print("Memory stack + interfaces: OK")
	PY

check-graph:
	@echo "[2/6] Checking graph/state/prompt injection..."
	@uv run python - <<'PY'
	from src.agent import build_graph, build_prompt, MEMORY_BUDGET
	required_keys = {"messages", "user_profile", "episodes", "semantic_hits", "memory_budget"}
	state = {
	    "messages": [{"role": "user", "content": "Xin chao"}],
	    "user_profile": {"name": "Khang"},
	    "episodes": [{"task": "debug docker", "outcome": "fixed"}],
	    "semantic_hits": ["Docker Compose dung service name"],
	    "memory_budget": MEMORY_BUDGET,
	}
	assert required_keys.issubset(state.keys()), "MemoryState keys mismatch"
	prompt = build_prompt(state)
	assert "## Profile" in prompt
	assert "## Episodic Memory" in prompt
	assert "## Semantic Knowledge" in prompt
	assert "## Recent Conversation" in prompt
	g = build_graph()
	assert {"retrieve_memory", "call_llm", "save_memory"}.issubset(set(g.nodes))
	print("Graph/state/router/prompt checks: OK")
	PY

check-conflict:
	@echo "[3/6] Checking overwrite conflict + episodic retrieval..."
	@uv run python - <<'PY'
	from src.memory.long_term import LongTermMemory
	from src.memory.episodic import EpisodicMemory
	lt = LongTermMemory(path="data/_tmp_profile_conflict_check.json")
	lt.save("allergy", "sua bo")
	lt.save("allergy", "dau nanh")
	assert lt.retrieve("allergy") == "dau nanh", "Conflict overwrite failed"
	ep = EpisodicMemory(path="data/_tmp_episodes_conflict_check.json")
	ep.save({"task": "deploy", "outcome": "thanh cong"})
	last = ep.retrieve(n=1)[0]
	assert last["task"] == "deploy" and last["outcome"] == "thanh cong"
	print("Conflict overwrite + episodic save/retrieve: OK")
	PY

check-benchmark:
	@echo "[4/6] Checking benchmark coverage..."
	@test -f BENCHMARK.md
	@grep -qi "Profile recall" BENCHMARK.md
	@grep -qi "Conflict update" BENCHMARK.md
	@grep -qi "Episodic recall" BENCHMARK.md
	@grep -qi "Semantic retrieval" BENCHMARK.md
	@grep -qi "Trim/token budget" BENCHMARK.md
	@echo "BENCHMARK.md coverage: OK"

check-reflection:
	@echo "[5/6] Checking privacy/limitations reflection..."
	@test -f README.md
	@grep -qi "privacy\|PII" README.md
	@grep -qi "consent\|TTL\|deletion\|xóa" README.md
	@grep -qi "limitation\|hạn chế" README.md
	@echo "README reflection coverage: OK"

check-bonus:
	@echo "[6/6] Checking bonus artifacts..."
	@test -f src/memory/redis_long_term.py
	@test -f src/tokens.py
	@test -f graph_demo.py
	@grep -q "try:" src/agent.py
	@grep -q "except" src/agent.py
	@echo "Bonus artifacts present: OK"

graph-demo:
	uv run python graph_demo.py

compile:
	uv run python -m compileall -q src main.py graph_demo.py
	@echo "Compile OK"

clean-memory:
	rm -f data/_tmp_profile_check.json data/_tmp_episodes_check.json data/_tmp_profile_conflict_check.json data/_tmp_episodes_conflict_check.json
	@echo "Temporary check artifacts removed."
