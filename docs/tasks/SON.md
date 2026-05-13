# Sơn — Researcher

**Branch:** `main` (push trực tiếp vào data/)
**Folder sở hữu:** `data/test_briefs.json`, `data/scoring_design.md`, `data/validate.py`

---

## Vai trò

Sơn là người duy nhất có thể đánh giá xem engine có hoạt động đúng không. Team toàn dev — không ai khác có domain knowledge để nói "kết quả này hợp lý hay không".

Output của Sơn là input trực tiếp cho Đức (scoring weights) và là tín hiệu go/no-go cuối sprint: "kết quả có nghe tốt với người biết ngành không?"

---

## KPI cá nhân

| KPI | Target |
|---|---|
| Scoring design | Đề xuất weights có lý do — không phải con số random |
| Test briefs | 10 briefs cover edge cases đủ để expose lỗi scoring |
| Validation report | Khi backend Đức xong: chạy `validate.py` → báo cáo case nào pass/fail + tại sao |
| Qualitative signal | "Kết quả nhìn có lý với người biết ngành" — chưa cần đạt % cụ thể ở giai đoạn này |

---

## Phase 0 (Tuần 1–2) — Research

### A0 — Phân tích 25 director profiles *(~2h)*

Mở `data/directors_mockup.json`, đọc kỹ tất cả 25 profiles. Viết ghi chú về:
- Distribution: genre phổ biến nhất là gì? Style nào chiếm đa số?
- Gaps: có loại director nào thiếu trong data không?
- Outliers: profile nào trông bất thường — budget range quá rộng, specialty quá generic?
- Câu hỏi cho Thành: "Trong thực tế, có loại project nào Alien Media làm thường xuyên mà không thấy director phù hợp trong list này?"

Output: ghi chú thô vào `data/data_analysis_notes.md` — không cần đẹp, cần thật.

### A3 — `data/scoring_design.md` *(~2h — sau khi đọc profiles)*

### A3 — `data/scoring_design.md` *(~2h — làm ngay)*

Đọc `data/directors_mockup.json` (25 profiles) và `docs/OVERVIEW.md` (scoring weights section).

Trả lời 3 câu hỏi này với lý do dựa trên kinh nghiệm Alien Media:

**1. Genre vs Style — cái nào quan trọng hơn trong thực tế?**

Weights hiện tại: genre 25%, style 20%. Có nên đổi không?
Ví dụ: một director giỏi TVC nhưng style không khớp — có tệ hơn director style khớp nhưng chưa làm TVC?

**2. Budget fit — soft score hay hard filter?**

Hiện tại budget fit chỉ chiếm 5% score. Trong thực tế Alien Media:
- Client có flexible không khi gặp director phù hợp vượt budget?
- Hay nên loại hẳn (hard filter) nếu brief budget ngoài range của director?

**3. Availability — bao nhiêu % là hợp lý?**

Hiện 10%. Nếu director tốt nhất đang booked, có worth it không để chờ?
Đề xuất: nên là soft score (như hiện tại) hay weighted penalty dựa trên `lead_time_days`?

**Format output:**
```markdown
# Scoring Design — đề xuất từ Sơn

## Weights đề xuất
| Dimension | Current | Proposed | Lý do |
|---|---|---|---|
| genre_match | 0.25 | ... | ... |
...

## Budget fit: soft score vs hard filter
...

## Availability: đề xuất xử lý
...
```

**Gửi cho Trung review → Trung approve → Đức implement.**

### A4 — `data/test_briefs.json` *(~2h)*

10 briefs để test engine — khác với demo briefs của Thành (chỉ cần đẹp), test briefs cần cover edge cases:

```json
[
  {
    "id": "TEST-001",
    "label": "Brief chuẩn — FMCG TVC emotional",
    "brand": "Vinamilk",
    "industry": "FMCG",
    "campaign_type": "TVC",
    "tone": "emotional_storytelling",
    "budget_usd": 40000,
    "timeline_weeks": 6,
    "description": "Tet campaign targeting mothers 25-40, warm and authentic",
    "expected_top3_director_ids": ["DIR-001", "DIR-008", "DIR-012"],
    "test_type": "standard"
  },
  {
    "id": "TEST-002",
    "label": "Edge case — budget rất thấp ($5K)",
    "test_type": "edge_budget_low",
    ...
  },
  {
    "id": "TEST-003",
    "label": "Edge case — tone hiếm (documentary_realism)",
    "test_type": "edge_rare_tone",
    ...
  },
  ...
]
```

Gợi ý 10 loại:
1. Brief chuẩn FMCG TVC emotional
2. Budget rất thấp ($5K) — không director nào fit perfectly
3. Budget rất cao ($150K) — premium tier only
4. Tone hiếm: documentary_realism
5. Industry hiếm: Automotive
6. Brief vague (description 1 câu ngắn)
7. Brief rất cụ thể (description dài, nhiều điều kiện)
8. Booked directors — test availability scoring
9. Social media content, tone comedic — khác hoàn toàn TVC
10. Corporate film + premium_brand tone

### A5 — `data/validate.py` *(~1h)*

Script đơn giản, viết xong chờ backend Đức xong mới chạy:

```python
import json, requests

TEST_BRIEFS  = json.loads(open("test_briefs.json").read())
API_URL = "http://localhost:8000"

results = []
for brief in TEST_BRIEFS:
    expected = set(brief.get("expected_top3_director_ids", []))
    if not expected:
        continue

    payload = {k: brief[k] for k in
               ["brand","industry","campaign_type","tone","budget_usd","timeline_weeks","description"]
              }
    payload["top_n"] = 3
    r = requests.post(f"{API_URL}/match", json=payload).json()
    actual = {c["director_id"] for c in r["shortlist"]}

    overlap = len(expected & actual) / len(expected)
    results.append({
        "id": brief["id"],
        "label": brief["label"],
        "expected": list(expected),
        "actual": list(actual),
        "overlap": round(overlap, 2),
        "response_time_ms": r["response_time_ms"],
        "pass": overlap >= 0.67
    })
    print(f"{'✅' if overlap >= 0.67 else '❌'} {brief['id']} — overlap: {overlap:.0%} | {r['response_time_ms']}ms")

passed = sum(1 for r in results if r["pass"])
print(f"\nKết quả: {passed}/{len(results)} passed ({passed/len(results):.0%})")
print(f"Avg response time: {sum(r['response_time_ms'] for r in results)//len(results)}ms")
```

---

## Phase 2 (Tuần 5–6) — Validation

- Chạy `validate.py` ngay khi Đức báo `/match` ready
- Báo cáo cho Trung: case nào pass, case nào fail, và tại sao (phân tích, không chỉ số)
- Nếu kết quả tệ: đề xuất điều chỉnh weights cụ thể → Đức update → chạy lại
- Không cần đạt 70% — cần hiểu rõ engine đang fail ở đâu để fix đúng chỗ

---

## Long-term (sau VentureX)

- Mở rộng test suite: thêm 50+ briefs từ brief thật Alien Media (anonymized)
- A/B test weights: compare kết quả với 2 weight configurations khác nhau
- Automated regression: chạy validate.py mỗi lần Đức merge vào main
- KOL test data: khi mở rộng sang KOL matching

---

## Dependencies

| Cần từ | Thứ |
|---|---|
| Không ai | A3 + A4: tự làm ngay |
| Đức | Backend `/match` chạy — chỉ cần để chạy A5 |
