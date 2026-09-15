"""Stage 1: fast classification with Nemotron 3 Nano."""
import re

from ..config import settings
from .. import nebius_client

CATEGORIES = ["billing", "technical", "account", "security", "shipping", "feature_request", "general"]
URGENCIES = ["low", "medium", "high", "critical"]
SENTIMENTS = ["positive", "neutral", "negative", "angry"]

_SYSTEM = f"""You are a fast support-ticket classifier. Read the ticket and return
ONLY a JSON object with keys:
- "category": one of {CATEGORIES}
- "urgency": one of {URGENCIES}
- "sentiment": one of {SENTIMENTS}
- "summary": a one-sentence summary of the issue
No prose, no markdown, just the JSON object."""


def classify(subject: str, body: str) -> tuple[dict, int]:
    if settings.effective_mock_mode:
        return _mock_classify(subject, body), 0

    user = f"Subject: {subject}\n\nBody:\n{body}"
    result, latency_ms = nebius_client.chat_json(settings.model_nano, _SYSTEM, user, temperature=0.1)

    result["category"] = result.get("category") if result.get("category") in CATEGORIES else "general"
    result["urgency"] = result.get("urgency") if result.get("urgency") in URGENCIES else "medium"
    result["sentiment"] = result.get("sentiment") if result.get("sentiment") in SENTIMENTS else "neutral"
    return result, latency_ms


_CATEGORY_KEYWORDS = {
    "security": [
        "hack", "breach", "unauthorized", "phishing", "leaked", "vulnerability",
        "compromised", "suspicious login", "suspicious activity", "never been to",
        "wasn't me", "wasnt me",
    ],
    "shipping": [
        "shipping", "delivery", "delivered", "package", "tracking", "in transit",
        "delayed", "customs", "reship",
    ],
    "account": [
        "password", "login", "log in", "locked out", "2fa", "authenticator",
        "delete my account", "delete account",
    ],
    "billing": [
        "refund", "invoice", "charge", "charged", "billing", "payment", "subscription",
        "cancel my subscription", "cancelling my subscription", "price", "pro-rated",
    ],
    "feature_request": [
        "feature request", "would be nice", "nice-to-have", "suggestion", "please add",
    ],
    "technical": [
        "error", "bug", "crash", "not working", "api", "rate limit", "429", "500",
        "timeout", "integration",
    ],
}

_CATEGORY_PRIORITY = ["security", "shipping", "account", "billing", "feature_request", "technical"]

_URGENCY_CRITICAL = ["urgent", "immediately", "asap", "critical", "right now", "down", "breach", "unauthorized"]
_URGENCY_HIGH = ["soon", "important", "blocking", "affecting our customers"]
_URGENCY_LOW = ["not urgent", "no rush", "whenever you", "whenever i get a chance", "just curious"]

_SENTIMENT_ANGRY = ["angry", "furious", "ridiculous", "unacceptable", "terrible", "worst"]
_SENTIMENT_NEGATIVE = ["frustrated", "disappointed", "not happy", "annoyed"]
_SENTIMENT_POSITIVE = ["thanks", "thank you", "great", "love", "appreciate"]


def _count_hits(text: str, phrases: list[str]) -> int:
    count = 0
    for phrase in phrases:
        pattern = r"\b" + re.escape(phrase) + r"\b"
        count += len(re.findall(pattern, text))
    return count


def _mock_classify(subject: str, body: str) -> dict:
    text = f"{subject} {body}".lower()

    scores = {cat: _count_hits(text, kws) for cat, kws in _CATEGORY_KEYWORDS.items()}
    best_category = max(_CATEGORY_PRIORITY, key=lambda c: (scores[c], -_CATEGORY_PRIORITY.index(c)))
    category = best_category if scores[best_category] > 0 else "general"

    if _count_hits(text, _URGENCY_LOW) > 0:
        urgency = "low"
    elif _count_hits(text, _URGENCY_CRITICAL) > 0:
        urgency = "critical"
    elif _count_hits(text, _URGENCY_HIGH) > 0:
        urgency = "high"
    else:
        urgency = "medium"

    if _count_hits(text, _SENTIMENT_ANGRY) > 0:
        sentiment = "angry"
    elif _count_hits(text, _SENTIMENT_NEGATIVE) > 0:
        sentiment = "negative"
    elif _count_hits(text, _SENTIMENT_POSITIVE) > 0:
        sentiment = "positive"
    else:
        sentiment = "neutral"

    return {
        "category": category,
        "urgency": urgency,
        "sentiment": sentiment,
        "summary": subject.strip() or body.strip()[:120],
    }
