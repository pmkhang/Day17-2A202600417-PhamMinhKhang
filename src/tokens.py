"""Token counting using tiktoken (more accurate than word count)."""
try:
    import tiktoken
    _enc = tiktoken.get_encoding("cl100k_base")

    def count_tokens(text: str) -> int:
        return len(_enc.encode(text))

except ImportError:
    # Fallback: word count × 1.3
    def count_tokens(text: str) -> int:  # type: ignore
        return int(len(text.split()) * 1.3)


def count_messages_tokens(messages: list[dict]) -> int:
    return sum(count_tokens(m.get("content", "")) for m in messages)
