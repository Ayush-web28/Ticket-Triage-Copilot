"""Stage 2: routing and prioritization with Nemotron 3 Super."""
from ..config import settings
from .. import nebius_client

TEAMS = ["billing", "technical", "account", "security", "logistics", "product", "general_support"]

_SYSTEM = f"""You are a support ticket router making a prioritization decision.
Given a ticket's classification, decide:
- "priority": integer 1 (lowest) to 5 (drop-everything critical)
- "team": one of {TEAMS}
- "escalate": true if this needs immediate human attention before any auto-drafted
  reply goes out (e.g. security incidents, legal threats, very angry high-value complaints)
- "reason": one short sentence explaining the priority and team choice
Return ONLY a JSON object with those four keys."""


def route(classification: dict, subject: str, body: str) -> tuple[dict, int]:
    if settings.effective_mock_mode:
        return _mock_route(classification), 0

    user = (
        f"Classification: {classification}\n\n"
        f"Subject: {subject}\n\nBody:\n{body}"
    )
    result, latency_ms = nebius_client.chat_json(settings.model_super, _SYSTEM, user, temperature=0.2)

    result["team"] = result.get("team") if result.get("team") in TEAMS else "general_support"
    try:
        result["priority"] = max(1, min(5, int(result.get("priority", 3))))
    except (TypeError, ValueError):
        result["priority"] = 3
    result["escalate"] = bool(result.get("escalate", False))
    return result, latency_ms


def _mock_route(classification: dict) -> dict:
    category = classification.get("category", "general")
    urgency = classification.get("urgency", "medium")
    sentiment = classification.get("sentiment", "neutral")

    team_map = {
        "billing": "billing",
        "technical": "technical",
        "account": "account",
        "security": "security",
        "shipping": "logistics",
        "feature_request": "product",
        "general": "general_support",
    }
    team = team_map.get(category, "general_support")

    urgency_score = {"low": 1, "medium": 2, "high": 3, "critical": 5}.get(urgency, 2)
    sentiment_bump = {"angry": 1, "negative": 0, "neutral": 0, "positive": -1}.get(sentiment, 0)
    priority = max(1, min(5, urgency_score + sentiment_bump))

    escalate = category == "security" or (urgency == "critical" and sentiment in {"angry", "negative"})

    return {
        "priority": priority,
        "team": team,
        "escalate": escalate,
        "reason": f"{urgency} urgency {category} ticket with {sentiment} sentiment routed to {team}.",
    }
