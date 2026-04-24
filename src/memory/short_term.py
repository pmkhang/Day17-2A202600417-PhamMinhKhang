class ShortTermMemory:
    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
        self._messages: list[dict] = []

    def add(self, role: str, content: str) -> None:
        self._messages.append({"role": role, "content": content})
        if len(self._messages) > self.max_turns:
            self._messages = self._messages[-self.max_turns:]

    def get(self) -> list[dict]:
        return self._messages

    def clear(self) -> None:
        self._messages = []
