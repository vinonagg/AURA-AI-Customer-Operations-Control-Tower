"""Policy retrieval with semantic OpenAI embeddings and deterministic local fallback.

The fallback is intentionally retained so the demo remains runnable without an API key.
When OPENAI_API_KEY is present, the retriever uses text-embedding-3-small and cosine
similarity over the policy corpus, with a small on-disk cache for repeat runs.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.config import settings
from .data import policies


class PolicyRetriever:
    def __init__(self) -> None:
        self.rows = policies()
        self.docs = [
            f"Category: {r['category']}. Policy: {r['policy_text']}. Eligibility: {r['eligibility']}. Approval: {r['approval_required']}"
            for r in self.rows
        ]
        self.mode = "tfidf-fallback"
        self.embeddings: np.ndarray | None = None
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = self.vectorizer.fit_transform(self.docs)
        if settings.enable_semantic_rag and settings.openai_api_key:
            self._load_or_create_embeddings()

    @property
    def cache_path(self) -> Path:
        return Path("data/.policy_embeddings.json")

    def _load_or_create_embeddings(self) -> None:
        try:
            if self.cache_path.exists():
                payload = json.loads(self.cache_path.read_text())
                if payload.get("model") == settings.embedding_model and len(payload.get("embeddings", [])) == len(self.docs):
                    self.embeddings = np.array(payload["embeddings"], dtype=np.float32)
                    self.mode = "openai-semantic"
                    return

            from openai import OpenAI

            client = OpenAI(api_key=settings.openai_api_key)
            response = client.embeddings.create(model=settings.embedding_model, input=self.docs)
            vectors = [item.embedding for item in response.data]
            self.embeddings = np.array(vectors, dtype=np.float32)
            self.cache_path.write_text(json.dumps({"model": settings.embedding_model, "embeddings": vectors}))
            self.mode = "openai-semantic"
        except Exception:
            # A portfolio demo must remain usable even if the API is unavailable.
            self.embeddings = None
            self.mode = "tfidf-fallback"

    def search(self, query: str, k: int = 3) -> list[dict[str, Any]]:
        if self.mode == "openai-semantic" and self.embeddings is not None:
            try:
                from openai import OpenAI

                client = OpenAI(api_key=settings.openai_api_key)
                response = client.embeddings.create(model=settings.embedding_model, input=[query])
                q = np.array(response.data[0].embedding, dtype=np.float32)
                denom = np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(q)
                scores = (self.embeddings @ q) / np.where(denom == 0, 1, denom)
                idx = np.argsort(scores)[::-1][:k]
                return [{**self.rows[i], "score": round(float(scores[i]), 4), "retrieval_mode": self.mode} for i in idx]
            except Exception:
                pass

        q = self.vectorizer.transform([query])
        scores = cosine_similarity(q, self.matrix)[0]
        idx = scores.argsort()[::-1][:k]
        return [{**self.rows[i], "score": round(float(scores[i]), 4), "retrieval_mode": "tfidf-fallback"} for i in idx]
