"""
Owner: Đức
Run once (or re-run to refresh): python ingest.py
Loads directors_mockup.json → embeds → stores in ChromaDB.
"""
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb
from config import settings

MODEL_NAME = "all-MiniLM-L6-v2"


def build_text(p: dict) -> str:
    return (
        f"{p['name']}. Genre: {p['primary_genre']}. Style: {p['primary_style']}. "
        f"Specialties: {', '.join(p['specialties'])}. "
        f"Notable brands: {', '.join(p['notable_brands'])}. "
        f"Notes: {p.get('bio', '')}"
    )


def flatten_metadata(p: dict) -> dict:
    # ChromaDB only accepts str | int | float | bool in metadata
    return {
        "name":                  p["name"],
        "primary_genre":         p["primary_genre"],
        "primary_style":         p["primary_style"],
        "specialties":           ",".join(p["specialties"]),
        "notable_brands":        ",".join(p["notable_brands"]),
        "years_experience":      p["years_experience"],
        "base_day_rate":         p["base_day_rate"],
        "budget_min_usd":        p["budget_min_usd"],
        "budget_max_usd":        p["budget_max_usd"],
        "availability_status":   p["availability"]["status"],
        "available_from":        p["availability"]["available_from"],
        "lead_time_days":        p["availability"]["lead_time_days"],
        "collaboration_style":   p["collaboration_style"],
        "avg_views":             p["success_metrics"]["avg_views_per_project"],
        "satisfaction":          p["success_metrics"]["client_satisfaction_score"],
        "on_time_rate":          p["success_metrics"]["on_time_delivery_rate"],
        "repeat_hire_rate":      p["success_metrics"]["repeat_hire_rate"],
        "award_count":           p["success_metrics"]["award_count"],
        "raw_json":              json.dumps(p, ensure_ascii=False),
    }


def main():
    # TODO (Đức): implement this
    raise NotImplementedError


if __name__ == "__main__":
    main()
