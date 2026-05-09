"""
API Routes
Owner: Đồng Đức (Backend Developer)

Two endpoints for the POC:
  POST /match   — main matching endpoint
  GET  /health  — sanity check
"""

from fastapi import APIRouter
from pydantic import BaseModel
from backend.layer1_retrieval.retrieval import retriever
from backend.layer2_scoring.scoring import score_candidates
from backend.layer3_explanation.explanation import generate_explanation

router = APIRouter()


class BriefRequest(BaseModel):
    brief_text: str
    genres: list[str] = []
    style_tags: list[str] = []
    top_n: int = 5


class CandidateResult(BaseModel):
    id: str
    name: str
    score: float
    explanation: str
    feature_breakdown: dict


class MatchResponse(BaseModel):
    shortlist: list[CandidateResult]
    total_candidates_considered: int


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/match", response_model=MatchResponse)
def match(req: BriefRequest):
    """
    Full pipeline: brief → Layer 1 retrieval → Layer 2 scoring → Layer 3 explanation
    """
    # TODO (Đồng Đức): Wire the three layers together
    # Step 1: retriever.search(req.brief_text)  → candidates (list of dicts)
    # Step 2: score_candidates(candidates, req.genres, req.style_tags, req.top_n)  → scored
    # Step 3: for each scored: generate_explanation(s)  → add to result
    # Return MatchResponse
    raise NotImplementedError
