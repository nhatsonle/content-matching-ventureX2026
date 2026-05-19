"""
Owner: Mạnh — Layer 2 unit tests.
Run: uv run pytest test_scoring.py -v -s
"""

import pytest

from models import BriefRequest
from retrieval import retrieve_candidates
from scoring import (
    MAX_POINTS,
    _availability_score,
    _budget_fit_score,
    _experience_score,
    _genre_score,
    _performance_score,
    _specialty_score,
    _style_score,
    rank_candidates,
    score_candidate,
)


BASE_BRIEF = BriefRequest(
    brand="Vinamilk",
    industry="FMCG",
    campaign_type="TVC",
    tone="emotional_storytelling",
    budget_usd=50_000,
    timeline_weeks=8,
    description="Family TVC celebrating multi-generational warmth.",
)


def _meta(**overrides) -> dict:
    base = {
        "primary_genre": "TVC",
        "primary_style": "emotional_storytelling",
        "specialties": "FMCG,F&B,Healthcare",
        "availability_status": "available",
        "budget_min_usd": 20_000,
        "budget_max_usd": 80_000,
        "years_experience": 10,
        "avg_views": 2_500_000,
        "satisfaction": 4.5,
    }
    base.update(overrides)
    return base


# --- per-dimension ---

def test_genre_match_vs_mismatch():
    assert _genre_score(_meta(primary_genre="TVC"), BASE_BRIEF) == 1.0
    assert _genre_score(_meta(primary_genre="music_video"), BASE_BRIEF) == 0.3


def test_style_match_vs_mismatch():
    assert _style_score(_meta(primary_style="emotional_storytelling"), BASE_BRIEF) == 1.0
    assert _style_score(_meta(primary_style="comedic"), BASE_BRIEF) == 0.2


def test_specialty_match_csv_parsing():
    assert _specialty_score(_meta(specialties="FMCG,F&B"), BASE_BRIEF) == 1.0
    assert _specialty_score(_meta(specialties="Tech,Telco"), BASE_BRIEF) == 0.2
    # whitespace tolerant
    assert _specialty_score(_meta(specialties=" FMCG , F&B "), BASE_BRIEF) == 1.0


def test_performance_weights_satisfaction_more():
    high_sat_low_views = _performance_score(_meta(satisfaction=5.0, avg_views=0), BASE_BRIEF)
    low_sat_high_views = _performance_score(_meta(satisfaction=0.0, avg_views=5_000_000), BASE_BRIEF)
    # 0.7 * 1 + 0.3 * 0 = 0.7  vs  0.7 * 0 + 0.3 * 1 = 0.3
    assert high_sat_low_views > low_sat_high_views
    assert pytest.approx(high_sat_low_views, abs=1e-3) == 0.7
    assert pytest.approx(low_sat_high_views, abs=1e-3) == 0.3


def test_performance_views_capped():
    # 100M views should not exceed cap-normalized 1.0 contribution
    capped = _performance_score(_meta(satisfaction=5.0, avg_views=100_000_000), BASE_BRIEF)
    assert capped <= 1.0
    assert pytest.approx(capped, abs=1e-3) == 1.0


def test_availability_available_vs_booked():
    assert _availability_score(_meta(availability_status="available"), BASE_BRIEF) == 1.0
    assert _availability_score(_meta(availability_status="booked"), BASE_BRIEF) == 0.2


def test_experience_cap():
    assert _experience_score(_meta(years_experience=10), BASE_BRIEF) == 0.5
    assert _experience_score(_meta(years_experience=25), BASE_BRIEF) == 1.0  # capped
    assert _experience_score(_meta(years_experience=0), BASE_BRIEF) == 0.0


def test_budget_in_range_vs_out():
    inrange = _budget_fit_score(_meta(budget_min_usd=10_000, budget_max_usd=100_000), BASE_BRIEF)
    below = _budget_fit_score(_meta(budget_min_usd=70_000, budget_max_usd=200_000), BASE_BRIEF)
    above = _budget_fit_score(_meta(budget_min_usd=1_000, budget_max_usd=20_000), BASE_BRIEF)
    assert inrange == 1.0
    assert below == 0.1
    assert above == 0.1


# --- aggregation ---

def test_perfect_candidate_hits_100():
    perfect = _meta(
        satisfaction=5.0, avg_views=10_000_000, years_experience=20,
    )
    score, breakdown = score_candidate(perfect, BASE_BRIEF)
    assert score == pytest.approx(100.0, abs=0.01)
    assert breakdown.genre_match == MAX_POINTS["genre_match"]


def test_breakdown_sum_equals_score():
    score, breakdown = score_candidate(_meta(), BASE_BRIEF)
    parts_sum = sum(breakdown.model_dump().values())
    assert round(parts_sum, 2) == round(score, 2)


def test_defensive_missing_metadata():
    score, breakdown = score_candidate({}, BASE_BRIEF)
    # Should not crash; all mismatch defaults applied
    assert 0 <= score <= 100
    assert breakdown.genre_match == pytest.approx(0.3 * 25, abs=0.01)


# --- ranking ---

def test_rank_sorted_desc_and_top_n():
    candidates = [
        {"id": "A", "metadata": _meta(primary_genre="music_video", satisfaction=1.0, availability_status="booked")},
        {"id": "B", "metadata": _meta()},  # decent
        {"id": "C", "metadata": _meta(satisfaction=5.0, avg_views=5_000_000, years_experience=20)},  # best
    ]
    ranked = rank_candidates(candidates, BASE_BRIEF, top_n=2)
    assert len(ranked) == 2
    assert ranked[0]["id"] == "C"
    assert ranked[0]["score"] >= ranked[1]["score"]


def test_top_n_larger_than_list_returns_all():
    candidates = [{"id": "A", "metadata": _meta()}]
    ranked = rank_candidates(candidates, BASE_BRIEF, top_n=10)
    assert len(ranked) == 1


# --- Layer 1 → Layer 2 integration ---

def test_layer1_layer2_pipeline_smoke():
    """End-to-end: real Chroma retrieval → score → rank. Requires `python ingest.py` first."""
    candidates = retrieve_candidates(BASE_BRIEF, top_k=10)
    ranked = rank_candidates(candidates, BASE_BRIEF, top_n=5)
    assert len(ranked) == 5
    scores = [r["score"] for r in ranked]
    assert scores == sorted(scores, reverse=True)
    for r in ranked:
        assert 0 <= r["score"] <= 100
        assert "score_breakdown" in r
