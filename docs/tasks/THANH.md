# Thành — Marketing Lead

**Branch:** `main` (push trực tiếp vào data/ và docs/)
**Folder sở hữu:** `data/demo_briefs.json`, `data/uat_checklist.md`

---

## Vai trò

Thành đại diện cho business user — người sẽ thực sự dùng tool này trong công việc hàng ngày. Hai đóng góp quan trọng nhất: (1) cung cấp briefs thật để demo không bị giả tạo, (2) UAT trên dashboard thành phẩm để đảm bảo non-technical user dùng được.

---

## KPI cá nhân

| KPI | Target |
|---|---|
| Demo briefs | 5 briefs thật, đa dạng, chạy được trên production |
| Expected output | Mỗi brief có expected_top3 dựa trên kinh nghiệm thực tế |
| UAT | Dashboard chạy được không cần hỗ trợ từ dev |
| Explanation quality | Approve: lý do AI có dẫn chứng cụ thể, không generic |

---

## Việc ngay bây giờ (tuần 6)

### A1 — `data/demo_briefs.json` *(~3h)*

Đây là 5 briefs **thật từ thực tế Alien Media** — dùng trong demo VentureX.
Không phải briefs giả — audience sẽ hỏi "case này có thật không?", câu trả lời phải là "có".

Mở `data/directors_mockup.json` để xem 25 director profiles và chọn expected_top3 theo kinh nghiệm.

```json
[
  {
    "id": "DEMO-001",
    "label": "Tết TVC — FMCG lớn",
    "brand": "Vinamilk",
    "industry": "FMCG",
    "campaign_type": "TVC",
    "tone": "emotional_storytelling",
    "budget_usd": 45000,
    "timeline_weeks": 6,
    "description": "TVC Tết 2026 nhắm vào bà mẹ 25–40 tuổi, thông điệp gia đình sum vầy, phong cách ấm áp chân thật, không dàn dựng quá.",
    "expected_top3_director_ids": ["DIR-XXX", "DIR-XXX", "DIR-XXX"],
    "why": "Vì sao chọn 3 người này theo kinh nghiệm của mình"
  }
]
```

**5 loại brief cần cover:**
1. TVC Tết FMCG — emotional, budget trung (~$40–50K)
2. Product launch F&B — bold/energetic, budget thấp (~$12–18K)
3. Brand film Insurance — cinematic, budget cao (~$60–80K)
4. Social content Beauty/Fashion — lifestyle, budget nhỏ (~$6–10K)
5. Corporate film Banking/Finance — premium brand, budget lớn (~$80–120K)

**Lưu ý:** field `why` chỉ cho con người đọc, không đưa vào API request — đây là benchmark để Sơn validate.

### A2 — `data/uat_checklist.md` *(~1h — làm ngay, không cần chờ gì)*

Viết 10–15 câu hỏi để tự test khi dashboard ra đời.
Không cần biết tech — đây là góc nhìn của người dùng cuối.

```markdown
# UAT Checklist — AI Matching Engine

**Người test:** Thành
**Ngày test:** [điền khi test]

## Usability
- [ ] Mình tự điền form được mà không cần hỏi dev
- [ ] Label và placeholder đủ rõ để hiểu cần điền gì
- [ ] Budget slider dễ dùng, range hợp lý
- [ ] Submit xong biết đang loading hay xong chưa

## Kết quả
- [ ] Số điểm hiển thị rõ, hiểu được ý nghĩa
- [ ] Score breakdown (7 dimensions) có dễ đọc không
- [ ] Explanation của mỗi director nghe tự nhiên, không máy móc
- [ ] Explanation có nhắc đến kinh nghiệm cụ thể (brand, genre, style)
- [ ] Available/Booked hiển thị rõ
- [ ] Thông tin trên card có đủ để ra quyết định initial không?

## Content
- [ ] Director nào trong top-3 mình thấy hợp lý
- [ ] Có director nào bị thiếu mà mình biết là nên có không?
- [ ] Có director nào trong list mà mình thấy không hợp không? Tại sao?

## Speed
- [ ] Từ submit đến có kết quả: ______ giây (ghi lại)
- [ ] Nhanh / chậm hơn mong đợi?

## Ghi chú tự do
...
```

---

## Tuần 7 (integration)

### UAT thật sự trên dashboard

Khi Trung deploy lên Vercel:
- Chạy lần lượt cả 5 demo briefs, ghi lại kết quả
- So sánh top-3 AI với expected_top3 của mình — có khớp không?
- Điền UAT checklist đầy đủ
- Ghi lại response time cho từng brief
- Approve hoặc request changes cho explanation quality

**Nếu AI cho kết quả khác với expected:** đừng assume AI sai — có thể cả hai đều hợp lý. Ghi chú lý do và thảo luận với team.

---

## Long-term (sau VentureX)

- Viết user guide: "Cách dùng Matching Engine để tìm đạo diễn" (non-technical, dành cho business team Alien Media)
- Template library: 10 brief templates theo loại dự án phổ biến — người dùng chọn template rồi chỉnh
- Feedback loop: sau mỗi project thật → điền "ai thực sự được chọn + kết quả" → data này improve engine
- Onboarding checklist cho client mới dùng tool

---

## Dependencies

| Cần từ | Thứ |
|---|---|
| Không ai | A1 + A2: tự làm ngay |
| Trung deploy | Dashboard lên Vercel — cần để làm UAT thật |
