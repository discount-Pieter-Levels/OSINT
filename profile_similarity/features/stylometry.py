import math
import re
from typing import Dict, Tuple

import numpy as np


def stylometry_similarity(profile1: Dict[str, object], profile2: Dict[str, object]) -> Tuple[float, str]:
    text1 = " ".join(str(c) for c in (profile1.get("captions") or []))
    text2 = " ".join(str(c) for c in (profile2.get("captions") or []))
    if not text1 or not text2:
        return 0.0, "No caption text was available for stylometry analysis."

    def features(text: str) -> np.ndarray:
        sentences = re.split(r"[.!?]+", text)
        words = re.findall(r"\b\w+\b", text.lower())
        punctuation = re.findall(r"[.!?,'\";:-]", text)
        vowels = re.findall(r"[aeiou]", text.lower())
        uppercase = sum(1 for ch in text if ch.isupper())
        lowercase = sum(1 for ch in text if ch.islower())
        stopwords = {"the", "and", "a", "an", "to", "of", "in", "is", "it", "for", "on", "with", "this", "that"}
        stop_count = sum(1 for w in words if w in stopwords)
        unique_ratio = len(set(words)) / max(1, len(words))
        return np.array(
            [
                len(sentences) / max(1, len(words)),
                len(words) / max(1, len(sentences)),
                len(punctuation) / max(1, len(words)),
                text.count("?"),
                text.count("!"),
                uppercase / max(1, len(text)),
                lowercase / max(1, len(text)),
                stop_count / max(1, len(words)),
                len(vowels) / max(1, len(text)),
                unique_ratio,
            ],
            dtype=np.float32,
        )

    vec1 = features(text1)
    vec2 = features(text2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0, "Stylometry vectors were empty."
    score = float(np.dot(vec1, vec2) / (norm1 * norm2))
    score = max(0.0, min(1.0, score))
    return round(score, 4), f"The stylometry feature vector was compared with cosine similarity at {score:.2f}."
