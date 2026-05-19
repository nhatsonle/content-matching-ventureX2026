"""
Owner: Mạnh — Layer 2 (Weighted Scoring)
Input:  candidates from retrieval.py (Layer 1) + BriefRequest
Output: ranked top_n list with `score` (0–100) and `score_breakdown` (per-dim points)

Rule-based, deterministic. 7 dimensions per OVERVIEW.md v1.
"""

from models import BriefRequest, ScoreBreakdown

WEIGHTS = {
    "genre_match": 0.25,
    "style_match": 0.20,
    "specialty_match": 0.20,
    "performance": 0.15,
    "availability": 0.10,
    "experience": 0.05,
    "budget_fit": 0.05,
}

MAX_POINTS = {dim: w * 100 for dim, w in WEIGHTS.items()}

VIEWS_CAP = 5_000_000
EXPERIENCE_CAP = 20
SATISFACTION_MAX = 5.0


def _genre_score(meta: dict, brief: BriefRequest) -> float:
    return 1.0 if meta.get("primary_genre") == brief.campaign_type else 0.3


def _style_score(meta: dict, brief: BriefRequest) -> float:
    return 1.0 if meta.get("primary_style") == brief.tone else 0.2


def _specialty_score(meta: dict, brief: BriefRequest) -> float:
    raw = meta.get("specialties", "")
    specialties = {s.strip() for s in raw.split(",") if s.strip()}
    return 1.0 if brief.industry in specialties else 0.2


def _performance_score(meta: dict, brief: BriefRequest) -> float:
    views = min(meta.get("avg_views", 0), VIEWS_CAP) / VIEWS_CAP
    satisfaction = meta.get("satisfaction", 0) / SATISFACTION_MAX
    return 0.7 * satisfaction + 0.3 * views


def _availability_score(meta: dict, brief: BriefRequest) -> float:
    return 1.0 if meta.get("availability_status") == "available" else 0.2


def _experience_score(meta: dict, brief: BriefRequest) -> float:
    years = meta.get("years_experience", 0)
    return min(years / EXPERIENCE_CAP, 1.0)


def _budget_fit_score(meta: dict, brief: BriefRequest) -> float:
    lo = meta.get("budget_min_usd", 0)
    hi = meta.get("budget_max_usd", 0)
    return 1.0 if lo <= brief.budget_usd <= hi else 0.1


_SCORERS = {
    "genre_match": _genre_score,
    "style_match": _style_score,
    "specialty_match": _specialty_score,
    "performance": _performance_score,
    "availability": _availability_score,
    "experience": _experience_score,
    "budget_fit": _budget_fit_score,
}


def score_candidate(meta: dict, brief: BriefRequest) -> tuple[float, ScoreBreakdown]:
    points = {
        dim: round(scorer(meta, brief) * MAX_POINTS[dim], 2)
        for dim, scorer in _SCORERS.items()
    }
    total = round(sum(points.values()), 2)
    return total, ScoreBreakdown(**points)


def rank_candidates(
    candidates: list[dict], brief: BriefRequest, top_n: int = 5
) -> list[dict]:
    scored = []
    for c in candidates:
        score, breakdown = score_candidate(c["metadata"], brief)
        scored.append({**c, "score": score, "score_breakdown": breakdown.model_dump()})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_n]
