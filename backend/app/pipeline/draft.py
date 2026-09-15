"""Stage 3: grounded resolution drafting with Nemotron 3 Ultra."""
from ..config import settings
from .. import nebius_client

_SYSTEM = """You are a senior support agent writing a reply to a customer.
Use ONLY the provided knowledge-base excerpts as your factual grounding --
if they don't cover the issue, say a human specialist will follow up rather
than inventing a policy. Be warm, concise, and specific. Reference concrete
steps. Sign off as "The Support Team".
Return ONLY a JSON object with keys:
- "reply": the full drafted reply text
- "used_kb_ids": array of KB doc ids you actually relied on (integers)
- "confidence": "high" | "medium" | "low" -- how well the KB covered this issue"""


def draft(subject: str, body: str, classification: dict, routing: dict, kb_snippets: list[dict]) -> tuple[dict, int]:
    if settings.effective_mock_mode:
        return _mock_draft(subject, body, classification, kb_snippets), 0

    kb_text = "\n\n".join(f"[KB#{s['id']}] {s['title']}\n{s['content']}" for s in kb_snippets) or "(no relevant KB articles found)"
    user = (
        f"Subject: {subject}\nBody:\n{body}\n\n"
        f"Classification: {classification}\nRouting: {routing}\n\n"
        f"Knowledge base excerpts:\n{kb_text}"
    )
    result, latency_ms = nebius_client.chat_json(settings.model_ultra, _SYSTEM, user, temperature=0.4)
    result.setdefault("reply", "")
    result.setdefault("used_kb_ids", [s["id"] for s in kb_snippets])
    result.setdefault("confidence", "medium")
    return result, latency_ms


def _mock_draft(subject: str, body: str, classification: dict, kb_snippets: list[dict]) -> dict:
    category = classification.get("category", "general")
    if kb_snippets:
        top = kb_snippets[0]
        body_text = (
            f"Hi there,\n\nThanks for reaching out about \"{subject.strip() or category}\". "
            f"Based on our '{top['title']}' guide: {top['content'].strip().splitlines()[0]}\n\n"
            "Here are the steps to resolve this:\n"
            f"{_bulletize(top['content'])}\n\n"
            "If this doesn't fully resolve things, just reply here and a specialist will jump in.\n\n"
            "The Support Team"
        )
        confidence = "high" if len(kb_snippets) >= 2 else "medium"
    else:
        body_text = (
            f"Hi there,\n\nThanks for reaching out about \"{subject.strip() or category}\". "
            "We don't have a documented answer for this exact case yet, so I've flagged it "
            "for a specialist on our team to follow up with you directly and make it right.\n\n"
            "The Support Team"
        )
        confidence = "low"

    return {
        "reply": body_text,
        "used_kb_ids": [s["id"] for s in kb_snippets],
        "confidence": confidence,
    }


def _bulletize(content: str) -> str:
    lines = [l.strip("- ").strip() for l in content.strip().splitlines() if l.strip()]
    steps = [l for l in lines if l][1:4] or lines[:3]
    return "\n".join(f"- {s}" for s in steps)
