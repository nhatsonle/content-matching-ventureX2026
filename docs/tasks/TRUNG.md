# Trung — Founder / Tech Lead

**Branch:** `main`
**Vai trò:** Research lead + unblock team + review + deploy + demo

---

## Vai trò

Trung không làm feature — Trung làm những gì giúp 5 người kia làm feature được: dẫn dắt research phase, kết nối với mentor, review scoring design, deploy khi đến giai đoạn, và chuẩn bị demo.

**Quan trọng:** Team toàn dev, thiếu domain expertise. Trung là cầu nối giữa team và người biết ngành (Thành, mentor). Architecture và features có thể thay đổi sau tuần 1–2.

---

## KPI cá nhân

| KPI | Target |
|---|---|
| Team unblocked | Đức có `OPENAI_API_KEY` trước khi bắt đầu B6 |
| Architecture decision | Xác nhận rõ cho team sau mentor session đầu tiên — tiếp tục build hay điều chỉnh gì |
| Deploy | Backend live trên Railway, frontend live trên Vercel trước demo |
| Demo reliability | Chạy 3 briefs liên tiếp trên production không lỗi ngay trước demo |

---

## Phase 0 — Research Lead (Tuần 1–2)

Đây là việc quan trọng nhất của Trung trong 2 tuần đầu.

### D0 — Kickstart research session *(~3h, tuần 1)*

Tổ chức 1 session với Thành để hiểu workflow thật:
- Quy trình shortlist thủ công hiện tại diễn ra thế nào? Ai làm, mất bao lâu, bước nào đau nhất?
- Brief thật của Alien Media trông như thế nào? Có fields nào quan trọng mình chưa có trong schema?
- 3–5 case thật: "brief X → ai được chọn → tại sao" — Thành kể, Trung ghi lại

Output: `data/domain_research.md` — notes thô từ session này, chia sẻ cho cả team đọc.

### D1 — Mentor session *(khi có lịch)*

Mang theo:
- Architecture diagram hiện tại (3 layers)
- 2–3 brief examples thật từ Thành
- Câu hỏi cụ thể: "Cách match kiểu này có phù hợp với industry không? Thiếu gì?"

Sau session: ra quyết định rõ cho team — tiếp tục build theo plan hiện tại hay điều chỉnh features gì.
Ghi quyết định vào `docs/OVERVIEW.md` phần Feature backlog.

### D2 — Unblock team sau research *(cuối tuần 2)*

- Gửi `OPENAI_API_KEY` cho Đức qua DM (không bỏ vào group, không commit vào repo)
  - Tạo key tại [platform.openai.com](https://platform.openai.com) → API Keys
- Confirm với Đức, Duy, Mạnh: "architecture xác nhận, bắt đầu build từ tuần 3"
- Review `scoring_design.md` của Sơn + approve hoặc adjust weights

---

## Phase 2 — Deploy (Tuần 5–6)

### D3 — Deploy backend lên Railway *(~2h, khi Đức báo `/match` stable)*

```bash
# Railway: New Project → Deploy from GitHub → chọn backend/
# Environment variables cần set:
OPENAI_API_KEY=sk-...
CHROMA_PERSIST_DIR=/data/chroma_db
DATA_PATH=/app/data/directors_mockup.json
```

Verify: `curl https://[railway-url]/health` → `{"status":"ok"}`

### D4 — Deploy frontend lên Vercel *(~30 phút, khi Duy xong swap mock)*

```bash
# Vercel: Import Project → chọn frontend/
# Environment variables:
NEXT_PUBLIC_API_URL=https://[railway-url]
NEXT_PUBLIC_USE_MOCK=false
```

### D5 — Demo prep *(1–2h trước demo)*

```
[ ] Chạy 5 demo briefs của Thành trên production — kết quả có "nghe hợp lý" không?
[ ] Explanation tiếng Việt nghe tự nhiên, không lỗi encoding
[ ] Score breakdown hiển thị đúng (Chrome + Safari)
[ ] Backup: record Loom 3–5 phút chạy live demo — phòng wifi yếu
[ ] Chuẩn bị brief đẹp nhất sẵn để mở ngay khi lên sân khấu
```

---

## Story cho demo VentureX

**Hook:** "Alien Media mất 2–5 ngày để shortlist đạo diễn. Tôi sẽ cho bạn thấy điều đó mất bao lâu với AI."

**Flow demo (3 phút):**
1. Mở dashboard live
2. Điền brief thật từ Thành: Vinamilk TVC Tết, emotional, $40K
3. Submit → đợi → shortlist xuất hiện
4. Chỉ vào score breakdown: "Không chỉ rank — nó giải thích tại sao từng người"
5. Đọc 1 explanation thật, có tên brand cụ thể
6. "Đây là starting point. Thành vẫn là người quyết định cuối — nhưng giờ cô ấy bắt đầu từ đây, không phải từ tờ giấy trắng."

> Đừng nói "10 giây" nếu thực tế chậm hơn — nói "vài phút thay vì vài ngày" vẫn là win thuyết phục.

---

## Long-term (sau VentureX)

- Data thật: thay mockup bằng profiles thật từ Alien Media
- KOL extension: cùng architecture, thêm data type mới
- Admin panel: Thành tự thêm/sửa profiles
- Feedback loop: business user rate kết quả → cải thiện weights
- API cho agencies: gửi brief → nhận shortlist programmatically

---

## Dependencies nhận từ team

| Từ ai | Thứ | Cần cho |
|---|---|---|
| Thành | Domain research session | D0 — tuần 1 |
| Sơn | `scoring_design.md` | Review + approve → Đức implement B5 |
| Đức | Confirm `/match` stable local | D3 deploy backend |
| Duy | Confirm swap mock → real xong | D4 deploy frontend |
| Thành | UAT passed | D5 demo prep |
