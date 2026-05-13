# AI Matching Engine — Bức tranh toàn thể

**Project:** Pennyworth — VentureX 2026
**Team:** Trung · Đức · Duy · Mạnh · Sơn · Thành
**Sprint:** 6 tuần · Demo target: cuối tuần 7 (19/05/2026)

> **Note về approach:** Team toàn dev, chưa có domain expert nội bộ. Features có thể thay đổi sau mentor sessions — document này là living doc, cập nhật theo từng phase.

---

## Vấn đề đang giải quyết

Alien Media mất 2–5 ngày để shortlist đạo diễn phù hợp cho mỗi brief — quá trình thủ công, phụ thuộc vào kinh nghiệm cá nhân, không nhất quán giữa các project.

**Hypothesis:** Một hệ thống AI có thể compress bước initial shortlisting xuống còn vài phút, đủ để business user lấy làm starting point — không cần thay thế hoàn toàn judgment của người có kinh nghiệm.

---

## Kiến trúc 3 lớp (current plan — có thể thay đổi sau mentor feedback)

```
Brief (text input)
        │
        ▼
┌───────────────────────────────────────────────────────────────┐
│  Layer 1 — Semantic Retrieval                                  │
│  Brief → embed → query ChromaDB → top 20 candidates           │
│  Model: all-MiniLM-L6-v2 (sentence-transformers)              │
└───────────────────────────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────────────────────────┐
│  Layer 2 — Weighted Scoring                                    │
│  top 20 → genre · style · specialty · performance · budget    │
│  → ranked shortlist top 5–10                                  │
└───────────────────────────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────────────────────────┐
│  Layer 3 — LLM Explanation  [Phase 2+]                        │
│  shortlist → OpenAI gpt-4o-mini → 2–3 câu lý do / ứng viên  │
└───────────────────────────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────────────────────────┐
│  Dashboard (Next.js + FastAPI)  [Phase 2+]                    │
│  Form nhập brief → hiển thị shortlist + score breakdown        │
└───────────────────────────────────────────────────────────────┘
```

### Scoring weights (Layer 2) — v1, chờ Sơn review

| Dimension | Weight | Cách tính |
|---|---|---|
| Genre match | 25% | primary_genre = campaign_type → 1.0, khác → 0.3 |
| Style match | 20% | primary_style = tone → 1.0, khác → 0.2 |
| Specialty match | 20% | industry in specialties → 1.0, khác → 0.2 |
| Performance | 15% | normalize(avg_views + satisfaction_score) |
| Availability | 10% | available = 1.0, booked = 0.2 |
| Experience | 5% | normalize(years_experience, max=20) |
| Budget fit | 5% | brief_budget in [min, max] → 1.0, ngoài range → 0.1 |

Weights này là v1 để bắt đầu build — không phải final. Sơn + mentor input sẽ điều chỉnh.

---

## Roadmap 6 tuần

### Phase 0 — Research & Kickstart (Tuần 1–2)

**Mục tiêu:** Hiểu domain trước khi build. Team toàn dev nên bước này quan trọng hơn bình thường.

```
⬜  Đọc và thảo luận: brief thật của Alien Media trông như thế nào?
⬜  Phỏng vấn / shadow Thành: quy trình shortlist thủ công diễn ra thế nào?
⬜  Mentor session đầu tiên: nghe lời khuyên trước khi commit vào architecture
⬜  Sơn: phân tích 25 director profiles — distribution, outliers, gaps trong data
⬜  Thành: viết 3–5 brief thật từ memory, kèm "ai mình đã chọn và tại sao"
⬜  Trung: quyết định go/no-go với architecture hiện tại sau mentor feedback
⬜  Setup môi trường dev cho cả team (Python env, Node, Git)
```

**Output Phase 0:**
- Brief format thật đã được validate bởi Thành
- Scoring dimensions đã được Sơn + mentor xác nhận là đúng
- Quyết định rõ: build tiếp architecture hiện tại hay pivot?

### Phase 1 — Core Engine (Tuần 3–4)

**Mục tiêu:** Engine chạy được end-to-end, test được bằng API call — chưa cần UI đẹp.

```
🔨  Đức: ingest.py → retrieval.py → scoring.py → /match endpoint
🔨  Sơn: test_briefs.json + validate.py (script test accuracy)
🔨  Duy: Next.js scaffold + types.ts + mock data (Mạnh build UI trên này)
🔨  Mạnh: BriefForm + CandidateCard cơ bản (chạy với mock)
⬜  Thành: 5 demo briefs + expected shortlists
```

**Gate Phase 1:** `POST /match` trả shortlist có điểm, không crash, kết quả "nghe có lý" với người biết ngành.

### Phase 2 — Product Layer (Tuần 5–6)

**Mục tiêu:** Dashboard dùng được, deploy được, demo được. Thêm explanation nếu còn thời gian.

```
⬜  Đức: explanation.py (Layer 3 — OpenAI) nếu Phase 1 xong sớm
⬜  Mạnh: ScoreBreakdown + polish UI
⬜  Duy: swap mock → real API
⬜  Thành: UAT checklist + chạy 5 demo briefs thật
⬜  Trung: deploy Railway + Vercel + demo prep
```

**Gate Phase 2 = Demo day:** Business user (Thành) tự dùng được, kết quả "thuyết phục được mentor".

---

## KPIs thực tế

KPIs được chia theo phase — không đặt hard number cho những thứ chưa có ground truth.

### Phase 0 — KPIs nghiên cứu

| KPI | Cách đo |
|---|---|
| Brief format validated | Thành confirm: "đây đúng là thứ mình điền trong thực tế" |
| Scoring dimensions signed off | Mentor hoặc Thành xác nhận 7 dimensions là đúng và đủ |
| Architecture decision | Trung ra quyết định rõ ràng: build tiếp hay thay đổi gì |

### Phase 1 — KPIs engine

| KPI | Cách đo |
|---|---|
| Engine chạy end-to-end | `/match` trả JSON đúng schema, không crash với 5 test briefs |
| Kết quả "nghe có lý" | Thành xem top-3 output và nói "những người này mình cũng sẽ xem xét" |
| Data ingested | 25 profiles vào ChromaDB thành công |
| Test coverage | Sơn chạy được validate.py, có output (accuracy số cụ thể chưa cần đạt target) |

### Phase 2 — KPIs demo

| KPI | Cách đo |
|---|---|
| Usability | Thành tự dùng được không cần hỏi dev |
| Demo reliability | Chạy 3 lần liên tiếp không lỗi ngay trước demo |
| Story convincing | Mentor nghe pitch xong nói "thú vị, tôi muốn biết thêm" |
| Speed (relative) | Rõ ràng nhanh hơn làm tay — dù 1 phút hay 10 giây đều là win |

> **Về response time:** "< 10 giây" là nice-to-have, không phải KPI cứng ở giai đoạn này. Demo proof-of-concept thì 30–60 giây vẫn OK nếu kết quả tốt. Optimize sau khi có real usage data.

### Không đo ở giai đoạn này

- "Top-3 overlap ≥ 70%" — chưa có enough ground truth data để validate số này có ý nghĩa
- Response time milliseconds — premature optimization
- Concurrent users, uptime SLA — chưa cần

---

## Feature backlog — có thể thay đổi sau mentor feedback

### Confirmed (build tuần 3–6)
- Brief input form với 7 fields cơ bản
- Semantic retrieval từ ChromaDB
- Weighted scoring với 7 dimensions
- Shortlist display với score per dimension

### Likely (nếu có thời gian Phase 2)
- LLM explanation per candidate (gpt-4o-mini)
- Availability badge + available_from date
- Notable brands display

### Uncertain — chờ mentor input
- Explanation có nên là tiếng Việt hay tiếng Anh?
- Có nên cho user điều chỉnh weights không (advanced mode)?
- Brief history / save briefs — user cần không?
- Export PDF shortlist — workflow thực tế có cần không?
- KOL matching — cùng sprint hay phase riêng?

### Không build trong 6 tuần này
- Authentication / multi-user
- Admin panel để thêm profiles
- Real director data (vẫn dùng mockup)
- Mobile app

---

## Tech stack

| Component | Công nghệ | Lý do |
|---|---|---|
| Backend | FastAPI (Python) | Async, auto OpenAPI docs |
| Vector DB | ChromaDB (local) | Zero-infra, dễ swap sang Qdrant sau |
| Embeddings | sentence-transformers `all-MiniLM-L6-v2` | Free, local, không cần API call |
| Scoring | Rule-based weighted | Explainable, không cần training data |
| Explanation | OpenAI `gpt-4o-mini` | Rẻ (~$0.0002/request), nhanh, multilingual |
| Frontend | Next.js + Tailwind | Nhanh build, deploy Vercel 1 click |
| Deploy | Railway (backend) + Vercel (frontend) | Free tier đủ cho demo |

---

## Ownership

| Người | Phần sở hữu | Branch |
|---|---|---|
| Đức | `backend/` toàn bộ | `backend/duc` |
| Duy | `frontend/lib/` + `frontend/app/` | `frontend/manh-duy` |
| Mạnh | `frontend/components/` | `frontend/manh-duy` |
| Sơn | `data/test_briefs.json` + `data/scoring_design.md` + `data/validate.py` | `main` |
| Thành | `data/demo_briefs.json` + `data/uat_checklist.md` | `main` |
| Trung | Research lead + review + deploy + demo | `main` |

API contract (`backend/models.py`) là ground truth — muốn thay đổi thì thông báo cả team trước.
