# Đức — Backend Developer

**Branch:** `backend/duc`
**Folder sở hữu:** `backend/` — không ai được đụng vào khi chưa hỏi

---

## Vai trò

Đức build toàn bộ engine — từ lúc data JSON vào ChromaDB cho đến khi `/match` trả shortlist có điểm và lý do. Frontend của Duy và Mạnh chờ cái này để swap mock → real.

---

## KPI cá nhân

| KPI | Target |
|---|---|
| `POST /match` chạy end-to-end | Trả đúng schema trong `models.py`, không crash với 5 test briefs |
| Ingest thành công | 25 profiles vào ChromaDB, `collection.count()` = 25 |
| Kết quả "nghe có lý" | Thành xem output và nói "những người này mình cũng sẽ xem xét" |
| Explanation (Phase 2) | gpt-4o-mini trả text tiếng Việt có nhắc đến kinh nghiệm cụ thể |

> Response time không phải KPI cứng giai đoạn này — miễn là trả kết quả trong session là được.

---

## Việc Phase 0 (Tuần 1–2) — Research trước, code sau

Tuần đầu **chưa cần viết code production**. Việc của Đức là:

- Đọc kỹ `data/directors_mockup.json` — hiểu structure data, spot vấn đề gì trước khi ingest
- Setup Python environment local: `pip install -r requirements.txt --break-system-packages`
- Chạy thử ChromaDB và sentence-transformers để đảm bảo chạy được trên máy
- Nghe mentor session với Trung — architecture có thể thay đổi trước khi build
- Nếu architecture confirmed: bắt đầu B3

## Việc Phase 1 (Tuần 3–4) — Core engine

Làm theo thứ tự — mỗi bước có thể test độc lập trước khi qua bước tiếp.

### B3 — `backend/ingest.py` *(~2h)*
Scaffold đã có sẵn, chỉ cần implement `main()`:

```python
def main():
    profiles = json.loads(Path(settings.data_path).read_text(encoding="utf-8"))
    model = SentenceTransformer(MODEL_NAME)
    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    collection = client.get_or_create_collection(settings.collection_name)

    texts  = [build_text(p) for p in profiles]
    embeds = model.encode(texts).tolist()
    metas  = [flatten_metadata(p) for p in profiles]
    ids    = [p["id"] for p in profiles]

    collection.upsert(ids=ids, embeddings=embeds, documents=texts, metadatas=metas)
    print(f"Ingested {len(profiles)} profiles. Count: {collection.count()}")
```

Test: `python ingest.py` → in ra "Ingested 25 profiles. Count: 25"

### B4 — `backend/retrieval.py` *(~1.5h)*

```python
def retrieve_candidates(brief: BriefRequest, top_k: int = 20) -> list[dict]:
    query_text = (
        f"Campaign for {brief.brand} in {brief.industry}. "
        f"Type: {brief.campaign_type}. Tone: {brief.tone}. {brief.description}"
    )
    model = SentenceTransformer(MODEL_NAME)
    vec = model.encode([query_text]).tolist()

    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    collection = client.get_collection(settings.collection_name)
    result = collection.query(query_embeddings=vec, n_results=top_k)

    candidates = []
    for i in range(len(result["ids"][0])):
        candidates.append({
            "id": result["ids"][0][i],
            "metadata": result["metadatas"][0][i],
        })
    return candidates
```

Test nhanh: gọi `retrieve_candidates()` với brief test, in top 5 names.

### B5 — `backend/scoring.py` *(~2h)*

Implement `score_candidate()` và `rank_candidates()` theo weights đã có.
Nếu Sơn chưa gửi `scoring_design.md`, dùng weights mặc định trong `TEAM_TASKS.md`.
Đề xuất của Sơn sẽ là input để refactor weights sau.

```python
def score_candidate(meta: dict, brief: BriefRequest) -> dict:
    b = {}
    b["genre_match"]     = 1.0 if meta["primary_genre"] == brief.campaign_type else 0.3
    b["style_match"]     = 1.0 if meta["primary_style"] == brief.tone else 0.2
    b["specialty_match"] = 1.0 if brief.industry in meta["specialties"].split(",") else 0.2
    views_norm           = min(meta["avg_views"] / 20_000_000, 1.0)
    b["performance"]     = views_norm * 0.5 + (meta["satisfaction"] / 5.0) * 0.5
    b["availability"]    = 1.0 if meta["availability_status"] == "available" else 0.2
    b["experience"]      = min(meta["years_experience"] / 20, 1.0)
    in_range             = meta["budget_min_usd"] <= brief.budget_usd <= meta["budget_max_usd"]
    b["budget_fit"]      = 1.0 if in_range else 0.1

    total = sum(b[k] * WEIGHTS[k] for k in WEIGHTS) * 100
    breakdown = {k: round(b[k] * WEIGHTS[k] * 100, 1) for k in WEIGHTS}
    return {"score": round(total, 1), "score_breakdown": breakdown}
```

### B6 — `backend/explanation.py` *(~1h — Phase 2, làm sau B3–B5)*
Scaffold gần như done — đã dùng OpenAI. Chỉ cần `OPENAI_API_KEY` trong `.env` — lấy từ Trung qua DM.
Kiểm tra prompt output có dẫn tên director + kinh nghiệm cụ thể, không generic.

### B7 — Wire up `/match` *(~30m)*
`main.py` scaffold đã có. Chỉ cần uncomment + đảm bảo stubs không còn `raise NotImplementedError`.

```bash
uvicorn main:app --reload --port 8000
curl -X POST http://localhost:8000/match \
  -H "Content-Type: application/json" \
  -d '{"brand":"Vinamilk","industry":"FMCG","campaign_type":"TVC","tone":"emotional_storytelling","budget_usd":40000,"timeline_weeks":6,"description":"Tet campaign mothers 25-40","top_n":3}'
```

Khi `/match` trả JSON đúng schema → **ping Duy** để swap mock → real.

---

## Phase 2 (Tuần 5–6) — Integration

- Fix CORS nếu Duy báo lỗi từ `localhost:3000`
- Cache SentenceTransformer ở module level để không khởi tạo lại mỗi request
- Hỗ trợ Sơn debug nếu `validate.py` ra kết quả lạ
- Implement B6 (explanation) nếu B3–B5 đã stable

---

## Long-term (sau VentureX)

- Swap ChromaDB local → Qdrant cloud khi data > 1000 profiles
- Async explanation: gọi Claude API song song cho 5 candidates thay vì tuần tự → tiết kiệm ~3–4s
- Admin endpoint `PUT /profiles/{id}` để cập nhật profile không cần re-ingest toàn bộ
- KOL data type: cùng architecture, thêm fields `platform`, `follower_count`, `engagement_rate`
- Fine-tuned embedding: nếu có > 200 historical briefs → train domain-specific encoder

---

## Dependencies

| Cần từ | Thứ |
|---|---|
| Trung | `OPENAI_API_KEY` qua DM — cần trước B6 |
| Trung | Confirm architecture sau mentor session — trước khi bắt đầu B3 |
| Sơn | `data/scoring_design.md` — cần trước B5 (nếu không có thì dùng default weights) |

**Không cần** chờ frontend, Duy, hay Mạnh.
