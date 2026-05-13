# Mạnh — Frontend Developer (components)

**Branch:** `frontend/manh-duy`
**Folder sở hữu:** `frontend/components/`

---

## Vai trò

Mạnh build toàn bộ UI components — phần người dùng thực sự nhìn thấy và tương tác. Không cần backend chạy, không cần biết API — chỉ cần `lib/mock.ts` và `lib/types.ts` của Duy.

---

## KPI cá nhân

| KPI | Target |
|---|---|
| BriefForm | Submit được, validate required fields, spinner khi loading |
| CandidateCard | Render đúng với mock data, score badge màu đúng (xanh/vàng/đỏ) |
| ScoreBreakdown | 7 bars hiển thị đúng proportion, label rõ |
| Visual pass | Chạy `NEXT_PUBLIC_USE_MOCK=true` → UI đẹp, không bị vỡ layout |

---

## Điều kiện bắt đầu

Chờ Duy xong **C2** (`lib/types.ts`) và **C3** (`lib/mock.ts`) — thường mất 2–3 giờ sau khi Duy bắt đầu.
Duy sẽ ping khi ready.

Trong lúc chờ: đọc API contract trong `TEAM_TASKS.md`, xem `data/directors_mockup.json` để hiểu data shape.

---

## Việc ngay bây giờ (tuần 6)

### C7 — `frontend/components/BriefForm.tsx` *(~4h)*

Form nhập brief — đây là màn hình đầu tiên người dùng thấy.

**Fields:**
```
Brand name          [text input]
Industry            [select] FMCG / F&B / Fashion / Banking / Insurance /
                             Healthcare / Tech / Beauty / Automotive / Entertainment
Campaign type       [select] TVC / digital_content / social_media_content /
                             music_video / corporate_video
Tone                [select] emotional_storytelling / cinematic / comedic /
                             bold_graphic / documentary_realism / premium_brand
Budget (USD)        [number + range slider $1,000–$250,000, step $1,000]
Timeline (tuần)     [range slider 2–12 tuần]
Description         [textarea, placeholder gợi ý, min 30 chars để submit]
Top N               [range slider 3–10, default 5]
```

**Behavior:**
- Submit button disabled khi: brand trống, description < 30 chars, hoặc đang loading
- Khi submit: show spinner trong button, gọi `matchDirectors()` từ `lib/api.ts`
- Khi có lỗi: hiển thị error message dưới button, không xóa form

**Props interface:**
```typescript
interface BriefFormProps {
  onSubmit: (result: MatchResponse) => void
  onLoading: (loading: boolean) => void
}
```

### C8 — `frontend/components/CandidateCard.tsx` *(~4h)*

Một card = một đạo diễn trong shortlist.

**Layout:**

```
┌─────────────────────────────────────────────────────┐
│  #1  Nguyễn Minh Khoa                    [ 87 ]     │
│       🟢 Available · từ 20/05/2026       /100        │
│                                                     │
│  Score breakdown:                                   │
│  Genre    ████████████████░░░░  25.0 / 25           │
│  Style    ██████████████░░░░░░  18.0 / 20           │
│  Specialty████████████████░░░░  20.0 / 20           │
│  ...                                                │
│                                                     │
│  "Nguyễn Minh Khoa có 9 năm kinh nghiệm TVC..."    │
│                                                     │
│  [Vinamilk]  [Manulife]  [Nestlé]                  │
└─────────────────────────────────────────────────────┘
```

**Score badge màu:**
- Score ≥ 70: xanh lá
- Score 50–69: vàng cam
- Score < 50: đỏ

**Availability badge:**
- `available`: 🟢 Available · từ [available_from]
- `booked`: 🔴 Booked

**Props:**
```typescript
interface CandidateCardProps {
  candidate: CandidateResult
}
```

### C9 — `frontend/components/ScoreBreakdown.tsx` *(~1h)*

Component nhỏ, dùng trong CandidateCard.
Nhận `score_breakdown` object, render 7 horizontal bars dùng Tailwind width.

```typescript
interface ScoreBreakdownProps {
  breakdown: ScoreBreakdown
  // max values per dimension:
  // genre_match: 25, style_match: 20, specialty_match: 20,
  // performance: 15, availability: 10, experience: 5, budget_fit: 5
}
```

Bar fill = `(value / max) * 100%`. Label tiếng Việt:
- `genre_match` → "Thể loại"
- `style_match` → "Phong cách"
- `specialty_match` → "Chuyên ngành"
- `performance` → "Hiệu suất"
- `availability` → "Sẵn sàng"
- `experience` → "Kinh nghiệm"
- `budget_fit` → "Ngân sách"

---

## Tuần 7 (integration)

- Verify components render đúng với data thật từ API (thay vì mock) — không cần sửa gì nếu types đúng
- Responsive check: card không vỡ trên màn hình nhỏ hơn
- Thành sẽ làm UAT — fix visual issues Thành phát hiện

---

## Long-term (sau VentureX)

- Expand card: thêm tab "Portfolio" với link video samples
- Comparison view: chọn 2–3 directors, so sánh side-by-side
- Sort + filter UI: lọc theo availability, sort theo từng score dimension
- Director profile modal: click card → xem full profile
- Animation: card entrance animation, score bar fill animation (dùng Framer Motion)

---

## Dependencies

| Cần từ | Thứ | Khi nào |
|---|---|---|
| Duy | `lib/types.ts` (C2) | Trước khi bắt đầu bất kỳ component nào |
| Duy | `lib/mock.ts` (C3) | Trước khi render thật sự |

**Không cần** backend, API, hay Đức. Mọi thứ chạy với mock data.
