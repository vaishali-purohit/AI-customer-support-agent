from pathlib import Path
from typing import Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from app.core.constants import (
    KNOWLEDGE_PATH,
    RETRIEVAL_TOP_K,
    RETRIEVAL_SCORE_THRESHOLD,
    RETRIEVAL_SNIPPET_MAX_LENGTH,
)


# Represents a single retrieved document snippet with its relevance score
class RetrievalResult:
    def __init__(self, source_id: str, snippet: str, score: float):
        self.source_id = source_id
        self.snippet = snippet
        self.score = score


# Loads and queries a local knowledge base using TF-IDF similarity search
class RetrievalService:
    def __init__(self, knowledge_dir: Optional[Path] = None):
        self.knowledge_dir = knowledge_dir or Path(KNOWLEDGE_PATH)
        self._vectorizer: Optional[TfidfVectorizer] = None
        self._doc_matrix = None
        self._documents: list[dict] = []
        self._loaded = False

    # Loads markdown documents from the knowledge directory and builds the TF-IDF index
    def _load(self) -> None:
        if self._loaded:
            return
        docs = []
        for path in self.knowledge_dir.glob("*.md"):
            text = path.read_text(encoding="utf-8")
            docs.append({"source_id": path.stem, "text": text})
        if not docs:
            self._loaded = True
            return
        self._documents = docs
        self._vectorizer = TfidfVectorizer(stop_words="english")
        self._doc_matrix = self._vectorizer.fit_transform([d["text"] for d in docs])
        self._loaded = True

    # Searches the knowledge base for the most relevant passages to the query
    def query(self, query_text: str, top_k: int = RETRIEVAL_TOP_K, score_threshold: float = RETRIEVAL_SCORE_THRESHOLD) -> list[dict]:
        self._load()
        if not self._documents:
            return []
        q_vec = self._vectorizer.transform([query_text])
        scores = cosine_similarity(q_vec, self._doc_matrix)[0]
        idx = np.argsort(scores)[::-1][:top_k]
        results = []
        for i in idx:
            if scores[i] < score_threshold:
                continue
            text = self._documents[i]["text"]
            paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
            if not paragraphs:
                paragraphs = [text.strip()]
            para_vec = self._vectorizer.transform(paragraphs)
            para_scores = cosine_similarity(q_vec, para_vec)[0]
            best_para_idx = int(np.argmax(para_scores))
            snippet = paragraphs[best_para_idx]
            if len(snippet) > RETRIEVAL_SNIPPET_MAX_LENGTH:
                snippet = snippet[:RETRIEVAL_SNIPPET_MAX_LENGTH].rsplit(" ", 1)[0] + "..."
            results.append({
                "source_id": self._documents[i]["source_id"],
                "snippet": snippet,
                "score": float(scores[i]),
            })
        return results
