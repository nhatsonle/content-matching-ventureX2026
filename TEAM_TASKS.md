# Team Task Assignment — Parallel Tracks
**Cập nhật:** 13/05/2026 | **Sprint target:** Demo cuối tuần 7 · **Phase 0 (tuần 1–2): research trước, code sau**

> Features có thể thay đổi sau mentor session. Architecture hiện tại là starting point, không phải final.
> Xem full roadmap và KPIs tại `docs/OVERVIEW.md`.

---

## Nguyên tắc làm việc

1. **4 tracks chạy song song** — không ai phải chờ ai để bắt đầu
2. **File ownership rõ ràng** — mỗi người sở hữu folder riêng, không đụng vào folder của người khác
3. **Chỉ 1 điểm integration** — frontend + backend gặp nhau đúng 1 lần ở cuối, thông qua API contract đã được định sẵn
4. **Mock trước, real sau** — frontend dùng mock data để build UI độc lập, swap sang real API khi backend xong

---

## API Contract (đã định sẵn — không ai được thay đổi mà không thông báo)

Frontend và backend đều build theo đúng contract này:

```typescript
// POST /match — request
{
  brand: string
  industry: string
  campaign_type: string
  tone: string
  budget_usd: number
  timeline_weeks: number
  description: string
  top_n: number  // default 5
}

// POST /match — response
{
  brief_summary: string
  shortlist: Array<{
    rank: number
    director_id: string
    name: string
    score: number          // 0–100
    score_breakdown: {
      genre_match: number
      style_match: number
      specialty_match: number
      performance: number
      availability: number
      experience: number
      budget_fit: number
    }
    explanation: string    // 2–3 câu tiếng Việt
    availability_status: string
    available_from: string
    notable_brands: string[]
    collaboration_style: string
  }>
  total_candidates_considered: number
  response_time_ms: number
}
```

---

## Folder Ownership — không được đụng folder của người khác

```
ContentMatching/
├── backend/          → Đức (ONLY)
│   ├── main.py
│   ├── ingest.py
│   ├── retrieval.py
│   ├── scoring.py
│   ├── explanation.py
│   ├── models.py
│   ├── config.py
│   └── requirements.txt
│
├── frontend/
│   ├── components/   → Mạnh (ONLY)
│   │   ├── BriefForm.tsx
│   │   ├── CandidateCard.tsx
│   │   └── ScoreBreakdown.tsx
│   ├── lib/          → Duy (ONLY)
│   │   ├── api.ts
│   │   ├── mock.ts
│   │   └── types.ts
│   └── app/          → Duy (ONLY — routing, pages)
│       ├── page.tsx
│       └── results/page.tsx
│
└── data/
    ├── directors_mockup.json     → đã xong ✅
    ├── test_briefs.json          → Sơn
    ├── demo_briefs.json          → Thành
    └── validation_report.md     → Sơn
```

---

## 4 Tracks song song

```
TUẦN 6 (ngay bây giờ)
─────────────────────────────────────────────────────────
Track A │ Thành  │ Demo briefs + expected shortlists
Track A │ Sơn    │ Scoring formula + test framework
Track B │ Đức    │ Backend: ingest → retrieval → scoring → explain → /match
Track C │ Duy    │ Mock API server + routing + types
Track C │ Mạnh   │ UI components (dùng mock data của Duy)

TUẦN 7 (integration week)
─────────────────────────────────────────────────────────
        │ Sơn    │ Chạy test briefs thật trên backend Đức
        │ Thành  │ UAT trên dashboard Mạnh+Duy
        │ Trung  │ Code review + deploy + demo prep
─────────────────────────────────────────────────────────
        ↓ Duy swap mock → real API (1–2h) → DONE
```

---

## 👤 Track A — Thành (Marketing Lead)

**Bắt đầu:** Ngay bây giờ
**Không cần:** Code, backend, frontend
**Folder:** `data/demo_briefs.json`

### Việc làm:

**[A1] Viết 5 demo briefs thật** *(~3h)*

Đây là briefs thật từ thực tế Alien Media — dùng trong demo VentureX. Điền đúng format:

```json
// data/demo_briefs.json
[
  {
    "id": "DEMO-001",
    "label": "Tet TVC lớn",
    "brand": "...",
    "industry": "FMCG",
    "campaign_type": "TVC",
    "tone": "emotional_storytelling",
    "budget_usd": 40000,
    "timeline_weeks": 6,
    "description": "...",
    "expected_top3_director_ids": ["DIR-XXX", "DIR-XXX", "DIR-XXX"],
    "reason": "Vì sao chọn 3 người này (theo kinh nghiệm)"
  }
]
```

Gợi ý 5 loại brief:
1. Tet TVC FMCG — emotional, budget ~40K
2. Product launch F&B — bold/energetic, budget ~15K
3. Brand film Insurance — cinematic, budget ~60K
4. Social content Beauty — lifestyle, budget ~8K
5. Corporate film Banking — premium brand, budget ~80K

**[A2] UAT checklist** *(~1h, làm ngay)*

Viết ra 10 câu hỏi để test dashboard khi xong:
- "Explanation có nghe tự nhiên không?"
- "Score breakdown có dễ hiểu với người không phải dev không?"
- "Thiếu thông tin gì quan trọng trên director card?"
- v.v.

→ Lưu vào `data/uat_checklist.md`

---

## 👤 Track A — Sơn (Researcher)

**Bắt đầu:** Ngay bây giờ
**Không cần:** Backend chạy, frontend chạy
**Folder:** `data/test_briefs.json`, `data/validation_report.md`

### Việc làm:

**[A3] Thiết kế scoring weights** *(~2h, làm ngay)*

Đọc `directors_mockup.json` và `IMPLEMENTATION_PLAN.md` Step 4.

Với weights hiện tại:
```python
genre_match: 0.25 | style_match: 0.20 | specialty_match: 0.20
performance: 0.15 | availability: 0.10 | experience: 0.05 | budget_fit: 0.05
```

Câu hỏi cần trả lời:
- Trong thực tế Alien Media, cái nào quan trọng hơn — genre hay style?
- Budget fit có thực sự ảnh hưởng nhiều không, hay chỉ là filter cứng?
- availability có nên là hard filter (loại hẳn nếu booked) thay vì score component?

→ Viết đề xuất weights vào `data/scoring_design.md`. Đức sẽ implement theo.

**[A4] Viết 10 test briefs đa dạng** *(~2h)*

Khác với demo briefs của Thành (chỉ 5 briefs đẹp nhất), test briefs của Sơn cần **cover edge cases**:
- Brief rất vague vs rất cụ thể
- Budget ngoài range của mọi director
- Tone hiếm (documentary_realism)
- KOL/entertainment brief
- Brief tiếng Việt vs tiếng Anh

→ Lưu vào `data/test_briefs.json`

**[A5] Validation framework** *(~1h)*

Viết script Python đơn giản `data/validate.py`:
```python
# Load test_briefs.json
# Với mỗi brief: gọi POST /match (khi backend Đức xong)
# So sánh kết quả với expected_top3
# Print: agreement rate, cases sai
```

Script này chỉ cần viết, chưa cần chạy — chờ Đức xong backend là chạy được ngay.

---

## 👤 Track B — Đức (Backend Dev)

**Bắt đầu:** Ngay bây giờ
**Không cần:** Frontend, Duy, Mạnh
**Folder:** `backend/` — ONLY

### Việc làm (theo thứ tự, mỗi file là 1 commit):

**[B1] `backend/models.py`** *(~1h)*
Pydantic models cho `BriefRequest`, `CandidateResult`, `MatchResponse` — theo đúng API contract ở trên.

**[B2] `backend/config.py` + `requirements.txt`** *(~30m)*
Settings từ `.env`, danh sách packages.

**[B3] `backend/ingest.py`** *(~2h)*
Load JSON → build text representation → embed → upsert ChromaDB.
```bash
python ingest.py  # → "Ingested 25 profiles"
```

**[B4] `backend/retrieval.py`** *(~2h)*
Brief → embed → query ChromaDB → return top 20 candidates với metadata.

**[B5] `backend/scoring.py`** *(~2h)*
Implement theo weights từ `data/scoring_design.md` của Sơn.
Nếu Sơn chưa xong thì dùng weights mặc định, refactor sau.

**[B6] `backend/explanation.py`** *(~2h)*
Gọi OpenAI API (`gpt-4o-mini`). Cần `OPENAI_API_KEY` — hỏi Trung. Làm sau khi B3–B5 xong.

**[B7] `backend/main.py`** *(~1h)*
Wire up `/match`, `/ingest`, `/health`.
CORS: `allow_origins=["http://localhost:3000", "https://*.vercel.app"]`

**Khi xong B7:** Ping Duy để swap mock → real. Không cần làm gì thêm.

---

## 👤 Track C — Duy (Developer)

**Bắt đầu:** Ngay bây giờ
**Không cần:** Backend chạy
**Folder:** `frontend/lib/`, `frontend/app/`

### Việc làm:

**[C1] Setup Next.js + cấu trúc** *(~1h)*
```bash
npx create-next-app@latest frontend --typescript --tailwind --app
```
Tạo folder structure: `components/`, `lib/`, `app/results/`

**[C2] `frontend/lib/types.ts`** *(~30m)*
TypeScript types cho `BriefRequest` và `MatchResponse` — theo đúng API contract trên.
Mạnh import từ đây để build components có type safety.

**[C3] `frontend/lib/mock.ts`** *(~2h)*
Mock response **thật và đầy đủ** — Mạnh cần cái này để build UI:

```typescript
// mock.ts — trả về data giả khớp 100% với API contract
export const MOCK_RESPONSE: MatchResponse = {
  brief_summary: "TVC cho Vinamilk (FMCG)",
  shortlist: [
    {
      rank: 1,
      director_id: "DIR-001",
      name: "Nguyễn Minh Khoa",
      score: 87.4,
      score_breakdown: {
        genre_match: 25, style_match: 18, specialty_match: 20,
        performance: 11, availability: 10, experience: 4, budget_fit: 5
      },
      explanation: "Nguyễn Minh Khoa có kinh nghiệm 9 năm với FMCG...",
      availability_status: "available",
      available_from: "2026-05-20",
      notable_brands: ["Vinamilk", "Manulife"],
      collaboration_style: "detail_oriented"
    },
    // ... 4 more
  ],
  total_candidates_considered: 25,
  response_time_ms: 1840
}
```

**[C4] `frontend/lib/api.ts`** *(~1h)*
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === "true"

export async function matchDirectors(brief: BriefRequest): Promise<MatchResponse> {
  if (USE_MOCK) return MOCK_RESPONSE  // ← Mạnh dùng cái này
  const res = await fetch(`${API_URL}/match`, { method: "POST", ... })
  return res.json()
}
```

**[C5] `frontend/app/page.tsx`** + **`app/results/page.tsx`** *(~2h)*
- `page.tsx`: render `<BriefForm>` component của Mạnh
- `results/page.tsx`: gọi `matchDirectors()`, render list `<CandidateCard>`
- Handle loading + error states

**[C6] Swap mock → real** *(~1h, khi Đức báo backend xong)*
Set `NEXT_PUBLIC_USE_MOCK=false`, test với backend Đức. Fix CORS nếu cần.

---

## 👤 Track C — Mạnh (Developer)

**Bắt đầu:** Sau khi Duy xong C2 + C3** (~2h sau)**
**Không cần:** Backend, API thật
**Folder:** `frontend/components/` — ONLY

### Việc làm:

**[C7] `BriefForm.tsx`** *(~4h)*
Form nhận input brief. Khi submit: gọi `matchDirectors()` từ `lib/api.ts`.

Fields:
- Brand (text)
- Industry (select 10 options)
- Campaign type (select 5 options)
- Tone (select 6 options)
- Budget USD (number input + range slider $1K–$250K)
- Timeline (range slider 2–12 tuần)
- Description (textarea, min 50 chars)
- Top N (range slider 3–10)
- Submit button: disabled khi loading, hiển thị spinner

**[C8] `CandidateCard.tsx`** *(~4h)*
Props: nhận 1 object `shortlist[i]` từ `MatchResponse`.

Layout:
```
┌─────────────────────────────────────┐
│ #1  Nguyễn Minh Khoa        87.4 ●  │
│ 🟢 Available from 20/05            │
│                                     │
│ Score breakdown:                    │
│ Genre    ████████████████░░  25/25  │
│ Style    ██████████████░░░░  18/20  │
│ Specialty████████████████░░  20/20  │
│ ...                                 │
│                                     │
│ "Nguyễn Minh Khoa có kinh nghiệm   │
│ 9 năm với FMCG..."                  │
│                                     │
│ Brands: Vinamilk  Manulife  ...    │
└─────────────────────────────────────┘
```

**[C9] `ScoreBreakdown.tsx`** *(~1h)*
Mini horizontal bars dùng Tailwind `w-[XX%]`. Nhận `score_breakdown` object, render 7 bars.

**Test Mạnh:** Chạy với `NEXT_PUBLIC_USE_MOCK=true` → UI hiển thị đúng mock data là pass.

---

## 👤 Trung — Founder

**Track D — Integration & Deploy**
**Bắt đầu:** Khi các track khác xong

**[D1] Ngay bây giờ — unblock team** *(~30m)*
- Tạo `.env` cho Đức với `OPENAI_API_KEY` (qua DM, không commit vào repo)
- Setup repo Git nếu chưa có, tạo branches: `backend/duc`, `frontend/manh-duy`
- Share `IMPLEMENTATION_PLAN.md` + `TEAM_TASKS.md` cho cả team

**[D2] Review scoring weights** *(khi Sơn xong A3)*
Đọc `data/scoring_design.md` của Sơn, approve hoặc adjust trước khi Đức implement B5.

**[D3] Deploy backend** *(khi Đức xong B7)*
Railway hoặc Render free tier. Set env vars, verify `/health` endpoint live.

**[D4] Deploy frontend** *(khi Duy xong C6)*
Vercel. Set `NEXT_PUBLIC_API_URL` = backend URL trên Railway.

**[D5] Demo prep** *(cuối tuần 7)*
- Chạy 5 demo briefs của Thành trên production
- Verify response time < 10s
- Record Loom video 3–5 phút làm backup

---

## Dependency graph thật sự

```
Thành [A1+A2] ──────────────────────────────→ UAT cuối tuần 7
Sơn   [A3] → Đức dùng weights → [A4+A5] → chạy validation
Đức   [B1→B7] ────────────────────────────→ ping Duy swap mock
Duy   [C1→C5] → Mạnh bắt đầu [C7+C8+C9] → [C6 swap mock]
Trung [D1 ngay] ──────────→ [D2 review] → [D3+D4 deploy] → [D5 demo]
```

Điểm gặp nhau duy nhất: **Duy C6** (swap mock → real API) — chỉ mất 1–2h.
Tất cả việc còn lại: parallel hoàn toàn.

---

## Checklist bắt đầu ngay hôm nay

- [ ] **Trung** → tạo `.env` gửi cho Đức qua DM (OPENAI_API_KEY — không bỏ vào group)
- [ ] **Trung** → setup Git repo + tạo branches, share link cho team
- [ ] **Thành** → mở `directors_mockup.csv`, bắt đầu chọn directors cho 5 demo briefs
- [ ] **Sơn** → đọc `directors_mockup.json`, viết `data/scoring_design.md`
- [ ] **Đức** → `mkdir backend`, bắt đầu B1 (models.py)
- [ ] **Duy** → `npx create-next-app`, bắt đầu C1+C2+C3
- [ ] **Mạnh** → đọc `lib/types.ts` của Duy, bắt đầu C7 khi Duy xong C3
