"""
Owner: Đức — Layer 3
Input:  one ranked candidate + BriefRequest
Output: 2–3 sentence explanation string in Vietnamese
Uses OpenAI gpt-4o-mini. Requires OPENAI_API_KEY in .env
"""
import openai
from models import BriefRequest
from config import settings

client = openai.OpenAI(api_key=settings.openai_api_key)

PROMPT = """\
You are a casting advisor at a Vietnamese production company.

Campaign Brief:
- Brand: {brand}
- Industry: {industry}
- Type: {campaign_type}
- Tone: {tone}
- Budget: ${budget_usd:,}
- Description: {description}

Director Profile:
- Name: {name}
- Primary genre: {primary_genre}
- Primary style: {primary_style}
- Specialties: {specialties}
- Notable brands: {notable_brands}
- Score breakdown: {score_breakdown}
- Notes: {notes}

Write 2–3 concise sentences explaining why this director is recommended for this campaign.
Be specific — reference their actual experience and style. Write in Vietnamese.\
"""


def generate_explanation(brief: BriefRequest, candidate: dict) -> str:
    meta = candidate["metadata"]
    prompt = PROMPT.format(
        brand=brief.brand,
        industry=brief.industry,
        campaign_type=brief.campaign_type,
        tone=brief.tone,
        budget_usd=brief.budget_usd,
        description=brief.description,
        name=meta["name"],
        primary_genre=meta["primary_genre"],
        primary_style=meta["primary_style"],
        specialties=meta["specialties"],
        notable_brands=meta["notable_brands"],
        score_breakdown=candidate.get("score_breakdown", {}),
        notes=meta.get("bio", ""),
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
