from typing import Dict, Tuple

import numpy as np

try:
    from keybert import KeyBERT
except Exception:  # pragma: no cover - optional dependency
    KeyBERT = None


def topic_similarity(profile1: Dict[str, object], profile2: Dict[str, object]) -> Tuple[float, str]:
    text1 = " ".join(str(c) for c in (profile1.get("captions") or [])) + " " + str(profile1.get("bio", ""))
    text2 = " ".join(str(c) for c in (profile2.get("captions") or [])) + " " + str(profile2.get("bio", ""))
    if not text1 or not text2:
        return 0.0, "No text was available for topic extraction."
    if KeyBERT is None:
        tokens1 = [t.lower() for t in text1.split() if len(t) > 3]
        tokens2 = [t.lower() for t in text2.split() if len(t) > 3]
        topic1 = sorted(set(tokens1))[:10]
        topic2 = sorted(set(tokens2))[:10]
    else:
        kw_model = KeyBERT()
        topic1 = [t for t, _ in kw_model.extract_keywords(text1, top_n=10)]
        topic2 = [t for t, _ in kw_model.extract_keywords(text2, top_n=10)]
    if not topic1 or not topic2:
        return 0.0, "No topics could be extracted from the provided text."
    combined = sorted(set(topic1) | set(topic2))
    if not combined:
        return 0.0, "Keyword sets were empty."
    vec1 = np.array([1 if term in topic1 else 0 for term in combined], dtype=np.float32)
    vec2 = np.array([1 if term in topic2 else 0 for term in combined], dtype=np.float32)
    score = float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2) + 1e-9))
    return round(max(0.0, min(1.0, score)), 4), f"The extracted topic keywords overlapped with a similarity score of {score:.2f}."
