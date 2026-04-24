"""Graph flow demo — prints the agent graph structure."""
from src.agent import build_graph


def main() -> None:
    graph = build_graph()
    print("=== Agent Graph Flow ===")
    print()
    print("  [START]")
    print("     |")
    print("     v")
    print("  retrieve_memory   ← loads: long_term, episodic, semantic")
    print("     |")
    print("     v")
    print("  call_llm          ← injects: profile + episodic + semantic + recent")
    print("     |")
    print("     v")
    print("  save_memory       ← updates: long_term (LLM extract), episodic (outcome)")
    print("     |")
    print("     v")
    print("  [END]")
    print()
    print("Nodes:", list(graph.nodes))


if __name__ == "__main__":
    main()
