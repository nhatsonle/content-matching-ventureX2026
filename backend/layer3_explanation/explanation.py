"""
Layer 3 — Explanation Generator
Owner: Trung (Founder)

Goal: For each scored candidate, generate 2–3 human-readable sentences
      explaining WHY they were recommended.

For the POC, use template-based generation (no LLM needed).
The template picks the top-2 strongest signals from the feature_breakdown
and formats them into natural Vietnamese text.

Optional upgrade: replace _build_from_template() with an LLM call
when we want richer explanations.
"""

from backend.layer2_scoring.scoring import ScoredCandidate

TEMPLATES = {
    "genre_match":        "Đã có kinh nghiệm trong thể loại {genres} — phù hợp trực tiếp với brief.",
    "style_match":        "Phong cách {styles} trùng khớp với yêu cầu sáng tạo của dự án.",
    "experience_score":   "Với {years} năm kinh nghiệm, đủ để xử lý quy mô và áp lực sản xuất.",
    "availability_bonus": "Hiện đang rảnh lịch — có thể bắt đầu ngay.",
    "outcome_score":      "{pct}% dự án trước đây đạt kết quả tốt (rating cao / đúng tiến độ / giải thưởng).",
}

def generate_explanation(scored: ScoredCandidate) -> str:
    """
    Returns a 2–3 sentence explanation string in Vietnamese.
    """
    # TODO (Trung): Implement template selection
    # Hint: sort feature_breakdown by value desc, pick top 2 signals,
    #       format using TEMPLATES, join into a paragraph.
    raise NotImplementedError
