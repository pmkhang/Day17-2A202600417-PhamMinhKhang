import json
import os


class EpisodicMemory:
    def __init__(self, path: str = "data/episodes.json"):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            with open(path, "w") as f:
                json.dump([], f)

    def save(self, episode: dict) -> None:
        with open(self.path) as f:
            episodes = json.load(f)
        episodes.append(episode)
        with open(self.path, "w") as f:
            json.dump(episodes, f, ensure_ascii=False, indent=2)

    def retrieve(self, n: int = 5) -> list[dict]:
        with open(self.path) as f:
            episodes = json.load(f)
        return episodes[-n:]
