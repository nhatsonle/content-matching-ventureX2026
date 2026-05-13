# Implementation Plan — AI Matching Engine
**Đọc CLAUDE.md trước để hiểu architecture và data schema.**

---

## Thứ tự build (theo dependency)

```
Step 1 → Step 2 → Step 3 → Step 4 → Step 5 → Step 6
Backend  Ingest   Layer1   Layer2   Layer3   Frontend
setup    data     retriev  scoring  explain  dashboard
```

Mỗi step độc lập, testable, và có thể commit riêng.

---

## Step 1 — Backend scaffold

**Mục tiêu:** FastAPI app chạy được, có health check endpoint.

**Việc làm:**
```bash
mkdir backend && cd backend
```

Tạo `requirements.txt`:
```
fastapi==0.115.0
uvicorn[standard]==0.30.0
chromadb==0.5.0
sentence-transformers==3.0.0
anthropic==0.34.0
pydantic==2.8.0
python-dotenv==1.0.0
```

Tạo `config.py`:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    anthropic_api_key: str
    chroma_persist_dir: str = "./chroma_db"
    data_path: str = "../data/directors_mockup.json"
    collection_name: str = "directors"

    class Config:
        env_file = ".env"

settings = Settings()
```

Tạo `models.py` với Pydantic models:
- `BriefRequest` — input từ frontend
- `CandidateResult` — một director trong shortlist (có score, breakdown, explanation)
- `MatchResponse` — full response từ `/match`

Tạo `main.py`:
- `GET /health` → `{"status": "ok"}`
- Placeholder `POST /match` → return empty shortlist
- Placeholder `POST /ingest` → return `{"message": "not implemented"}`

**Test:**
```bash
uvicorn main:app --reload
curl http://localhost:8000/health
```

---

## Step 2 — Data ingestion (Layer 0)

**Mục tiêu:** Load `directors_mockup.json` → embed → store trong ChromaDB.

**Tạo `ingest.py`:**

```python
# Logic:
# 1. Load JSON từ data_path
# 2. Với mỗi profile, tạo "text representation" để embed:
#    f"{name}. Genre: {primary_genre}. Style: {primary_style}. 
#      Specialties: {specialties}. Notable brands: {notable_brands}. 
#      Notes: {notes}"
# 3. Embed bằng SentenceTransformer('all-MiniLM-L6-v2')
# 4. Upsert vào ChromaDB collection "directors"
#    - id = profile["id"]
#    - embedding = vector
#    - document = text representation
#    - metadata = tất cả fields còn lại (flatten nếu cần)
```

**Lưu ý metadata trong ChromaDB:**
ChromaDB chỉ accept `str | int | float | bool` trong metadata. Flatten nested objects:
```python
metadata = {
    "name": p["name"],
    "primary_genre": p["primary_genre"],
    "primary_style": p["primary_style"],
    "specialties": ",".join(p["specialties"]),  # list → string
    "budget_min_usd": p["budget_min_usd"],
    "budget_max_usd": p["budget_max_usd"],
    "avg_views": p["success_metrics"]["avg_views_per_project"],
    "satisfaction": p["success_metrics"]["client_satisfaction_score"],
    "on_time_rate": p["success_metrics"]["on_time_delivery_rate"],
    "repeat_hire_rate": p["success_metrics"]["repeat_hire_rate"],
    "award_count": p["success_metrics"]["award_count"],
    "availability_status": p["availability"]["status"],
    "available_from": p["availability"]["available_from"],
    "lead_time_days": p["availability"]["lead_time_days"],
    "collaboration_style": p["collaboration_style"],
    "years_experience": p["years_experience"],
    "notes": p["notes"],
    # store full JSON as string for retrieval
    "raw_json": json.dumps(p)
}
```

**Test:**
```bash
python ingest.py
# Should print: "Ingested 25 profiles into ChromaDB"
```

---

## Step 3 — Layer 1: Retrieval

**Mục tiêu:** Nhận brief → embed → query ChromaDB → trả top 20 candidates.

**Tạo `retrieval.py`:**

```python
# Input: BriefRequest
# Output: list of (director_id, metadata, distance_score)

def retrieve_candidates(brief: BriefRequest, top_k: int = 20) -> list[dict]:
    # 1. Build query text từ brief:
    #    f"Campaign for {brief.brand} in {brief.industry}. 
    #      Type: {brief.campaign_type}. Tone: {brief.tone}. 
    #      {brief.description}"
    # 2. Embed query với cùng model (SentenceTransformer)
    # 3. ChromaDB query: collection.query(query_embeddings=[vec], n_results=top_k)
    # 4. Return list of dicts với id, metadata, distance
```

**Test inline:**
```python
# Tạo test brief: Tet campaign, FMCG, emotional, budget 40K
# Expect: top results nên có directors có primary_style=emotional_storytelling 
#         và specialties chứa FMCG
```

---

## Step 4 — Layer 2: Scoring

**Mục tiêu:** Nhận candidates từ Layer 1 → tính weighted score → return ranked list.

**Tạo `scoring.py`:**

```python
WEIGHTS = {
    "genre_match":     0.25,
    "style_match":     0.20,
    "specialty_match": 0.20,
    "performance":     0.15,
    "availability":    0.10,
    "experience":      0.05,
    "budget_fit":      0.05,
}

def score_candidate(candidate_metadata: dict, brief: BriefRequest) -> dict:
    breakdown = {}
    
    # genre_match: exact match = 1.0, no match = 0.0
    breakdown["genre_match"] = 1.0 if candidate_metadata["primary_genre"] == brief.campaign_type else 0.3
    
    # style_match: exact match = 1.0, else 0.2
    breakdown["style_match"] = 1.0 if candidate_metadata["primary_style"] == brief.tone else 0.2
    
    # specialty_match: industry in specialties list
    specialties = candidate_metadata["specialties"].split(",")
    breakdown["specialty_match"] = 1.0 if brief.industry in specialties else 0.2
    
    # performance: normalize avg_views (max ~20M) + satisfaction (max 5.0)
    views_score = min(candidate_metadata["avg_views"] / 20_000_000, 1.0)
    sat_score = candidate_metadata["satisfaction"] / 5.0
    breakdown["performance"] = (views_score * 0.5) + (sat_score * 0.5)
    
    # availability: available = 1.0, booked = 0.2
    breakdown["availability"] = 1.0 if candidate_metadata["availability_status"] == "available" else 0.2
    
    # experience: normalize (max ~20 years)
    breakdown["experience"] = min(candidate_metadata["years_experience"] / 20, 1.0)
    
    # budget_fit: brief budget within [min, max] range = 1.0, outside = 0.1
    in_range = candidate_metadata["budget_min_usd"] <= brief.budget_usd <= candidate_metadata["budget_max_usd"]
    breakdown["budget_fit"] = 1.0 if in_range else 0.1
    
    # weighted total (0–100)
    total = sum(breakdown[k] * WEIGHTS[k] for k in WEIGHTS) * 100
    return {"score": round(total, 1), "breakdown": {k: round(v * WEIGHTS[k] * 100, 1) for k, v in breakdown.items()}}


def rank_candidates(candidates: list[dict], brief: BriefRequest, top_n: int = 5) -> list[dict]:
    scored = []
    for c in candidates:
        result = score_candidate(c["metadata"], brief)
        scored.append({**c, **result})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_n]
```

**Test:**
```python
# Chạy với test brief + candidates từ Step 3
# Print score breakdown cho top 3
# Verify: emotional_storytelling directors score cao hơn với Tet brief
```

---

## Step 5 — Layer 3: Explanation

**Mục tiêu:** Với mỗi top candidate → gọi Claude API → sinh 2–3 câu giải thích.

**Tạo `explanation.py`:**

```python
import anthropic
from models import BriefRequest

client = anthropic.Anthropic()

EXPLANATION_PROMPT = """
You are a casting advisor at a Vietnamese production company.

Campaign Brief:
- Brand: {brand}
- Industry: {industry}  
- Type: {campaign_type}
- Tone: {tone}
- Budget: ${budget_usd:,}
- Description: {description}

Director Profile:
{director_notes}
- Primary genre: {primary_genre}
- Primary style: {primary_style}
- Specialties: {specialties}
- Notable brands: {notable_brands}
- Score breakdown: {score_breakdown}

Write 2–3 concise sentences explaining why this director is recommended for this campaign.
Be specific — reference their actual experience and style. Write in Vietnamese.
"""

def generate_explanation(brief: BriefRequest, candidate: dict) -> str:
    meta = candidate["metadata"]
    prompt = EXPLANATION_PROMPT.format(
        brand=brief.brand,
        industry=brief.industry,
        campaign_type=brief.campaign_type,
        tone=brief.tone,
        budget_usd=brief.budget_usd,
        description=brief.description,
        director_notes=meta.get("notes", ""),
        primary_genre=meta["primary_genre"],
        primary_style=meta["primary_style"],
        specialties=meta["specialties"],
        notable_brands=meta.get("notable_brands", ""),
        score_breakdown=candidate["breakdown"]
    )
    
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text


def generate_explanations_batch(brief: BriefRequest, candidates: list[dict]) -> list[dict]:
    # Run sequentially (can parallelize later with asyncio if needed)
    for c in candidates:
        c["explanation"] = generate_explanation(brief, c)
    return candidates
```

**Test:**
```bash
# Requires ANTHROPIC_API_KEY in .env
python -c "from explanation import generate_explanation; ..."
# Verify: explanation mentions specific brand experience or style
```

---

## Step 6 — Wire up `/match` endpoint

**Cập nhật `main.py`** để kết nối cả 3 layers:

```python
@app.post("/match", response_model=MatchResponse)
async def match(brief: BriefRequest):
    import time
    start = time.time()
    
    # Layer 1
    candidates = retrieve_candidates(brief, top_k=20)
    
    # Layer 2
    ranked = rank_candidates(candidates, brief, top_n=brief.top_n)
    
    # Layer 3
    with_explanations = generate_explanations_batch(brief, ranked)
    
    elapsed_ms = int((time.time() - start) * 1000)
    
    return MatchResponse(
        brief_summary=f"{brief.campaign_type} for {brief.brand} ({brief.industry})",
        shortlist=[CandidateResult(**c) for c in with_explanations],
        total_candidates_considered=len(candidates),
        response_time_ms=elapsed_ms
    )
```

**End-to-end test:**
```bash
curl -X POST http://localhost:8000/match \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "Vinamilk",
    "industry": "FMCG",
    "campaign_type": "TVC",
    "tone": "emotional_storytelling",
    "budget_usd": 40000,
    "timeline_weeks": 6,
    "description": "Tet campaign targeting mothers 25-40, warm and authentic",
    "top_n": 5
  }'
# Expect: 5 ranked directors with scores + Vietnamese explanations, < 10s
```

---

## Step 7 — Frontend (Next.js)

**Mục tiêu:** UI để input brief → hiển thị shortlist kết quả.

```bash
npx create-next-app@latest frontend --typescript --tailwind --app
cd frontend
npm install
```

**Các components cần build:**

**`BriefForm.tsx`** — form với fields:
- Brand name (text)
- Industry (select: FMCG, Fashion, Tech, F&B, Banking, Healthcare, Entertainment, Telco, Automotive, Luxury)
- Campaign type (select: TVC, digital_content, social_media_content, music_video, corporate_video)
- Tone (select: emotional_storytelling, comedic, cinematic, bold_graphic, documentary_realism, premium_brand)
- Budget USD (number input với slider)
- Description (textarea)
- Top N (slider: 3–10)
- Submit → `POST /match`

**`CandidateCard.tsx`** — hiển thị một director:
- Rank number + Name
- Score (big number, color-coded: green ≥70, yellow 50–69, red <50)
- Score breakdown (mini bar chart per dimension)
- Explanation text
- Availability badge (green = available, red = booked, with available_from date)
- Notable brands (chips)

**`ScoreBreakdown.tsx`** — visual bar chart cho 7 score dimensions

**`app/page.tsx`** — layout:
```
[ALIEN Matching Engine]
[BriefForm]
```

**`app/results/page.tsx`** — layout:
```
Brief summary + response time
[CandidateCard × N]
[Back to new brief button]
```

**Test:** Submit brief từ form → kết quả hiển thị đúng, score bars visible.

---

## Step 8 — Polish & deployment

- [ ] Add loading state khi đang query (spinner trên Submit button)
- [ ] Error handling (API down, no results)
- [ ] CORS config trên FastAPI (`allow_origins=["http://localhost:3000"]`)
- [ ] Environment variable cho API URL trong Next.js (`NEXT_PUBLIC_API_URL`)
- [ ] Deploy backend lên Railway / Render (free tier đủ cho demo)
- [ ] Deploy frontend lên Vercel (same domain as alien-roi-demo or new subdomain)

---

## Checklist tổng

- [ ] Step 1 — Backend scaffold + health check
- [ ] Step 2 — Ingest 25 profiles vào ChromaDB
- [ ] Step 3 — Layer 1: retrieval hoạt động
- [ ] Step 4 — Layer 2: scoring + ranking hoạt động
- [ ] Step 5 — Layer 3: explanation từ Claude API
- [ ] Step 6 — `/match` endpoint wire up end-to-end
- [ ] Step 7 — Frontend form + result cards
- [ ] Step 8 — Polish + deploy

**Estimated time:** ~2–3 ngày làm việc để có MVP demo-able (Steps 1–7).

---

## Để chạy với Claude Code

```bash
cd /Users/trung/Work/ContentMatching
# Claude Code sẽ đọc CLAUDE.md tự động khi mở folder này
# Bắt đầu từ Step 1, làm tuần tự theo plan
```
