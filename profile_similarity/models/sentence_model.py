from typing import List

import numpy as np


class SentenceEncoder:
    def __init__(self) -> None:
        self._available = False
        self._model = None
        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer("all-MiniLM-L6-v2")
            self._available = True
        except Exception:
            self._available = False

    def encode(self, text: str) -> np.ndarray:
        if self._available and self._model is not None:
            return np.asarray(self._model.encode([text])[0], dtype=np.float32)
        tokens = [t.lower() for t in text.split() if t.isalnum()]
        if not tokens:
            return np.zeros(32, dtype=np.float32)
        vec = np.zeros(32, dtype=np.float32)
        for idx, token in enumerate(tokens[:32]):
            vec[idx % 32] += 1.0
        return vec / max(1.0, np.linalg.norm(vec))

    def encode_many(self, texts: List[str]) -> List[np.ndarray]:
        return [self.encode(text) for text in texts]
