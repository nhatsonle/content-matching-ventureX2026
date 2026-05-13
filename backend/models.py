from pydantic import BaseModel


class BriefRequest(BaseModel):
    brand: str
    industry: str        # FMCG | F&B | Fashion | Tech | Banking | Healthcare | Entertainment | Telco | Automotive | Luxury
    campaign_type: str   # TVC | digital_content | social_media_content | music_video | corporate_video
    tone: str            # emotional_storytelling | comedic | cinematic | bold_graphic | documentary_realism | premium_brand | lifestyle
    budget_usd: float
    timeline_weeks: int
    description: str
    top_n: int = 5


class ScoreBreakdown(BaseModel):
    genre_match: float      # 0–25 pts
    style_match: float      # 0–20 pts
    specialty_match: float  # 0–20 pts
    performance: float      # 0–15 pts
    availability: float     # 0–10 pts
    experience: float       # 0–5 pts
    budget_fit: float       # 0–5 pts


class CandidateResult(BaseModel):
    rank: int
    director_id: str
    name: str
    score: float
    score_breakdown: ScoreBreakdown
    explanation: str
    availability_status: str   # "available" | "booked"
    available_from: str        # ISO date e.g. "2026-05-20"
    notable_brands: list[str]
    collaboration_style: str


class MatchResponse(BaseModel):
    brief_summary: str
    shortlist: list[CandidateResult]
    total_candidates_considered: int
    response_time_ms: int
