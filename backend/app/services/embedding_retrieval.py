import math
import os
from dataclasses import dataclass
from functools import lru_cache

from app.services.evidence_retrieval import APPROVED_MESSAGE_TEMPLATES
from app.services.simulation import segment_for_context


@dataclass(frozen=True)
class EvidenceDocument:
    doc_id: str
    text: str
    metadata: dict


class LocalVectorStore:
    def __init__(self, embedding_model):
        self.embedding_model = embedding_model
        self.documents: list[EvidenceDocument] = []
        self.embeddings: list[list[float]] = []

    def add_documents(self, documents: list[EvidenceDocument]) -> None:
        self.documents.extend(documents)
        self.embeddings.extend(self.embedding_model.encode([doc.text for doc in documents]))

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        if not self.documents:
            return []
        query_embedding = self.embedding_model.encode([query])[0]
        scored = [
            {
                "doc_id": document.doc_id,
                "text": document.text,
                "metadata": document.metadata,
                "score": round(_cosine_similarity(query_embedding, embedding), 4),
            }
            for document, embedding in zip(self.documents, self.embeddings, strict=True)
        ]
        return sorted(scored, key=lambda item: item["score"], reverse=True)[:top_k]


class DeterministicEmbeddingModel:
    """Deployment-safe fallback that still produces dense local vectors."""

    def encode(self, texts: list[str]) -> list[list[float]]:
        return [_hashing_vector(text) for text in texts]


KeywordEmbeddingModel = DeterministicEmbeddingModel


class SentenceTransformerEmbeddingModel:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_name)

    def encode(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(texts, normalize_embeddings=True)
        return [list(vector) for vector in vectors]


def build_embedding_retriever(events: list, embedding_model=None) -> LocalVectorStore:
    model = embedding_model or get_embedding_model()
    store = LocalVectorStore(model)
    store.add_documents(build_evidence_documents(events))
    return store


def build_evidence_documents(events: list) -> list[EvidenceDocument]:
    documents = []
    for template in APPROVED_MESSAGE_TEMPLATES:
        documents.append(
            EvidenceDocument(
                doc_id=f"template:{template['template_id']}",
                text=(
                    f"approved template {template['template_id']} channel {template['channel']} "
                    f"tone {template['tone']} topic {template['topic_family']} cta "
                    f"{template['cta_aggressiveness']}"
                ),
                metadata={"type": "approved_message_template", **template},
            )
        )

    documents.extend(_campaign_example_documents(events))
    documents.extend(_segment_summary_documents(events))
    documents.extend(_policy_outcome_documents(events))
    return documents


def retrieve_embedding_evidence(
    events: list,
    user_context: dict,
    selected_policy: str,
    top_k: int = 3,
    embedding_model=None,
) -> list[dict]:
    retriever = build_embedding_retriever(events, embedding_model=embedding_model)
    query = (
        f"{segment_for_context(user_context)} profile maturity "
        f"{user_context.get('profile_maturity', 0)} fatigue {user_context.get('fatigue_score', 0)} "
        f"unsubscribe risk {user_context.get('unsubscribe_risk', 0)} policy {selected_policy}"
    )
    return retriever.search(query, top_k=top_k)


@lru_cache(maxsize=1)
def sentence_transformers_available() -> bool:
    try:
        import sentence_transformers  # noqa: F401
    except ImportError:
        return False
    return True


def optional_sentence_transformer_model():
    if not sentence_transformers_available():
        return None
    try:
        model_name = os.getenv("EMBEDDING_MODEL_NAME", "paraphrase-MiniLM-L3-v2")
        return SentenceTransformerEmbeddingModel(model_name=model_name)
    except Exception:
        return None


@lru_cache(maxsize=1)
def cached_sentence_transformer_model():
    return optional_sentence_transformer_model()


def get_embedding_model():
    return cached_sentence_transformer_model() or DeterministicEmbeddingModel()


def _campaign_example_documents(events: list) -> list[EvidenceDocument]:
    docs = []
    for index, event in enumerate(events[:50], start=1):
        intervention = (event.context or {}).get("intervention", {})
        outcome = (event.context or {}).get("outcome", {})
        docs.append(
            EvidenceDocument(
                doc_id=f"campaign:{index}",
                text=(
                    f"prior campaign policy {event.policy} action {event.action} "
                    f"channel {intervention.get('channel', 'unknown')} tone "
                    f"{intervention.get('tone', 'unknown')} long term reward "
                    f"{outcome.get('long_term_reward', event.reward)}"
                ),
                metadata={"type": "prior_campaign_example", "policy": event.policy},
            )
        )
    return docs


def _segment_summary_documents(events: list) -> list[EvidenceDocument]:
    grouped: dict[str, list] = {}
    for event in events:
        grouped.setdefault(segment_for_context(event.context or {}), []).append(event)

    docs = []
    for segment, segment_events in grouped.items():
        avg_reward = sum(event.reward for event in segment_events) / len(segment_events)
        docs.append(
            EvidenceDocument(
                doc_id=f"segment:{segment}",
                text=f"segment summary {segment} average immediate reward {avg_reward:.3f}",
                metadata={"type": "segment_summary", "segment": segment},
            )
        )
    return docs


def _policy_outcome_documents(events: list) -> list[EvidenceDocument]:
    grouped: dict[str, list] = {}
    for event in events:
        grouped.setdefault(event.policy, []).append(event)

    docs = []
    for policy, policy_events in grouped.items():
        avg_long_term = sum(
            float((event.context or {}).get("outcome", {}).get("long_term_reward", event.reward))
            for event in policy_events
        ) / len(policy_events)
        docs.append(
            EvidenceDocument(
                doc_id=f"policy:{policy}",
                text=f"policy outcome summary {policy} average long term reward {avg_long_term:.3f}",
                metadata={"type": "policy_outcome_summary", "policy": policy},
            )
        )
    return docs


def _keyword_vector(text: str) -> list[float]:
    tokens = text.lower().replace("_", " ").split()
    dimensions = [
        "supportive",
        "urgent",
        "email",
        "sms",
        "push",
        "fatigue",
        "risk",
        "mature",
        "developing",
        "policy",
        "template",
        "segment",
    ]
    return [tokens.count(dimension) for dimension in dimensions]


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    dot = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if not left_norm or not right_norm:
        return 0.0
    return dot / (left_norm * right_norm)


def _hashing_vector(text: str, dimensions: int = 64) -> list[float]:
    vector = [0.0] * dimensions
    tokens = text.lower().replace("_", " ").replace("-", " ").split()
    for token in tokens:
        index = sum(ord(character) for character in token) % dimensions
        vector[index] += 1.0
    return vector
