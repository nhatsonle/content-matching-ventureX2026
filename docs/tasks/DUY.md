# Duy — Frontend Developer (lib + routing)

**Branch:** `frontend/manh-duy`
**Folder sở hữu:** `frontend/lib/`, `frontend/app/`

---

## Vai trò

Duy là người build nền móng frontend: TypeScript types, mock data, API client, và routing. Mạnh xây UI components trên nền này. Cuối sprint, Duy là người duy nhất cần làm 1 việc để kết nối toàn bộ hệ thống: swap mock → real API.

---

## KPI cá nhân

| KPI | Target |
|---|---|
| Mock mode | `NEXT_PUBLIC_USE_MOCK=true npm run dev` → form submit được, hiện đủ 5 cards |
| Types | `lib/types.ts` khớp 100% với API contract trong `TEAM_TASKS.md` — Mạnh import được không lỗi |
| Integration | Sau khi Đức xong backend: swap mock → real trong < 2 giờ |
| Error states | Loading spinner + error message hiển thị đúng khi API chậm hoặc lỗi |

---

## Việc ngay bây giờ (tuần 6)

**Thứ tự quan trọng:** C2 + C3 trước — Mạnh cần để bắt đầu.

### C1 — Setup Next.js *(~1h)*

```bash
npx create-next-app@latest frontend --typescript --tailwind --app
cd frontend
# Tạo folder structure:
mkdir -p components lib
```

Xóa boilerplate không cần (page.tsx mặc định, globals.css thừa).

### C2 — `frontend/lib/types.ts` *(~30m — làm ngay)*

```typescript
export interface BriefRequest {
  brand: string
  industry: string
  campaign_type: string
  tone: string
  budget_usd: number
  timeline_weeks: number
  description: string
  top_n: number
}

export interface ScoreBreakdown {
  genre_match: number
  style_match: number
  specialty_match: number
  performance: number
  availability: number
  experience: number
  budget_fit: number
}

export interface CandidateResult {
  rank: number
  director_id: string
  name: string
  score: number
  score_breakdown: ScoreBreakdown
  explanation: string
  availability_status: string
  available_from: string
  notable_brands: string[]
  collaboration_style: string
}

export interface MatchResponse {
  brief_summary: string
  shortlist: CandidateResult[]
  total_candidates_considered: number
  response_time_ms: number
}
```

**Ping Mạnh ngay khi xong C2** — Mạnh đang chờ file này.

### C3 — `frontend/lib/mock.ts` *(~2h)*

Mock response phải thật và đầy đủ — Mạnh dùng data này để build UI.
Tạo 5 candidates khác nhau với score range thực tế (55–90), explanation tiếng Việt có nội dung cụ thể, brands thật.

```typescript
import { MatchResponse } from "./types"

export const MOCK_RESPONSE: MatchResponse = {
  brief_summary: "TVC cho Vinamilk (FMCG) — emotional storytelling",
  shortlist: [
    {
      rank: 1,
      director_id: "DIR-001",
      name: "Nguyễn Minh Khoa",
      score: 87.4,
      score_breakdown: {
        genre_match: 25.0, style_match: 18.0, specialty_match: 20.0,
        performance: 11.2, availability: 10.0, experience: 4.0, budget_fit: 5.0
      },
      explanation: "Nguyễn Minh Khoa có 9 năm kinh nghiệm TVC FMCG với phong cách emotional storytelling — chính xác những gì brief Tết yêu cầu. Đã hợp tác thành công với Vinamilk 3 lần, client satisfaction 4.8/5.",
      availability_status: "available",
      available_from: "2026-05-20",
      notable_brands: ["Vinamilk", "Manulife", "Nestlé"],
      collaboration_style: "detail_oriented"
    },
    // ... thêm 4 candidates
  ],
  total_candidates_considered: 25,
  response_time_ms: 1840
}
```

### C4 — `frontend/lib/api.ts` *(~1h)*

```typescript
import { BriefRequest, MatchResponse } from "./types"
import { MOCK_RESPONSE } from "./mock"

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"
const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === "true"

export async function matchDirectors(brief: BriefRequest): Promise<MatchResponse> {
  if (USE_MOCK) {
    await new Promise(r => setTimeout(r, 800)) // simulate latency
    return MOCK_RESPONSE
  }
  const res = await fetch(`${API_URL}/match`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(brief),
  })
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json()
}
```

### C5 — `frontend/app/page.tsx` + `app/results/page.tsx` *(~2h)*

`page.tsx` — render `<BriefForm>`, khi submit: lưu kết quả vào state → redirect results.
`results/page.tsx` — nhận data từ state, render list `<CandidateCard>`, hiển thị response_time_ms.
Handle: loading (spinner), error (message + retry button), empty results.

---

## Tuần 7 (integration)

### C6 — Swap mock → real *(~2h, khi Đức báo backend xong)*

```bash
# Test local trước
NEXT_PUBLIC_USE_MOCK=false NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

Checklist swap:
- Form submit → data thật từ API (không phải mock)
- Score numbers và explanation là thật (khác mock)
- Response time hiển thị đúng (field `response_time_ms`)
- CORS không lỗi (nếu lỗi: báo Đức fix `allow_origins` trong `main.py`)

---

## Long-term (sau VentureX)

- Share state quản lý bằng Zustand khi app phức tạp hơn (hiện `useState` là đủ)
- Thêm `/profiles` page để xem toàn bộ director database
- Filter client-side: lọc theo genre, sort theo score, filter theo availability
- Brief history: lưu các briefs đã submit (localStorage)
- Export shortlist thành PDF / email

---

## Dependencies

| Cần từ | Thứ | Khi nào |
|---|---|---|
| Không ai | — | C1 → C5: tự làm song song |
| Đức | Backend `/match` chạy được | Chỉ cần cho C6 — làm cuối tuần 7 |

**Mạnh cần Duy xong C2 + C3 trước khi bắt đầu.** Ưu tiên 2 file này.
