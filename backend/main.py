"""
Run: uvicorn main:app --reload  (from inside backend/)
"""
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import BriefRequest, MatchResponse, CandidateResult, ScoreBreakdown
from retrieval import retrieve_candidates
from scoring import rank_candidates
from explanation import generate_explanation

app = FastAPI(title="AI Matching Engine", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/match", response_model=MatchResponse)
def match(brief: BriefRequest):
    start = time.time()

    candidates = retrieve_candidates(brief, top_k=20)
    ranked = rank_candidates(candidates, brief, top_n=brief.top_n)

    shortlist = []
    for i, c in enumerate(ranked):
        shortlist.append(CandidateResult(
            rank=i + 1,
            director_id=c["id"],
            name=c["metadata"]["name"],
            score=c["score"],
            score_breakdown=ScoreBreakdown(**c["score_breakdown"]),
            explanation=generate_explanation(brief, c),
            availability_status=c["metadata"]["availability_status"],
            available_from=c["metadata"]["available_from"],
            notable_brands=c["metadata"]["notable_brands"].split(","),
            collaboration_style=c["metadata"]["collaboration_style"],
        ))

    return MatchResponse(
        brief_summary=f"{brief.campaign_type} for {brief.brand} ({brief.industry})",
        shortlist=shortlist,
        total_candidates_considered=len(candidates),
        response_time_ms=int((time.time() - start) * 1000),
    )
