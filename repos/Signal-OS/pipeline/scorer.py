"""
Phase 2: Scorer - Scores and categorizes scraped items.
"""
import datetime as dt
import json
import os
import re
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple
import requests
import yaml

ROOT = Path(__file__).parent.parent
CONFIG_DIR = ROOT / "config"
DATA_DIR = ROOT / "data"


def load_yaml(filename):
    path = CONFIG_DIR / filename
    if path.exists():
        return yaml.safe_load(path.read_text())
    return {}


def keyword_score(text, categories, scoring_config):
    text = text.lower()
    best_cat, best_score = None, 0.0
    for cat_id, cat in categories.items():
        score = 0.0
        for tier, weight in scoring_config.get("keyword_weights", {}).items():
            for kw in cat.get("keywords", {}).get(tier, []):
                if kw in text:
                    score += weight
        score *= cat.get("weight", 1.0)
        if score > best_score:
            best_cat, best_score = cat_id, score
    return best_cat, round(min(best_score, 10.0), 2)


def calculate_recency_boost(published_str, scoring_config):
    if not published_str:
        return 0.0
    try:
        if "T" in published_str:
            pub_date = dt.datetime.fromisoformat(published_str.replace("Z", "+00:00"))
        else:
            pub_date = dt.datetime.strptime(published_str, "%Y-%m-%d").replace(tzinfo=dt.timezone.utc)
        age_hours = (dt.datetime.now(dt.timezone.utc) - pub_date).total_seconds() / 3600
        if age_hours <= scoring_config.get("recency_boost_hours", 24):
            return scoring_config.get("recency_boost_points", 1.5)
    except Exception:
        pass
    return 0.0


def score_items(items, budget_remaining=50):
    categories = load_yaml("categories.yaml").get("categories", {})
    scoring_config = load_yaml("categories.yaml").get("scoring", {})

    print(f"\n{'='*60}")
    print(f"PHASE 2: SCORING (AI Budget: {budget_remaining})")
    print(f"{'='*60}\n")

    print("[scorer] Keyword scoring (free)...")
    for item in items:
        text = f"{item.get('title', '')} {item.get('summary', '')}"
        category, score = keyword_score(text, categories, scoring_config)
        recency_boost = calculate_recency_boost(item.get("published", ""), scoring_config)
        score += recency_boost
        item["category"] = category or "uncategorized"
        item["score"] = score

    items.sort(key=lambda i: i.get("score", 0), reverse=True)

    ai_budget = min(budget_remaining, scoring_config.get("llm_review_top_n", 50))
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    if not openrouter_key:
        print("[scorer] No OPENROUTER_API_KEY. Using keyword scores only.")
        return items

    print(f"[scorer] AI scoring top {ai_budget} items...")
    openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
    scored_count = 0

    for item in items[:ai_budget]:
        if scored_count >= ai_budget:
            break
        try:
            prompt = f"""Score this news item (1-10 each):
Title: {item.get('title', '')}
Source: {item.get('source', '')}
Summary: {item.get('summary', '')[:300]}
Return JSON: {{"relevance": N, "novelty": N, "urgency": N, "category": "one of [frontier_intelligence, saudi_global_economy, financial_markets, products_platforms, mobile_infrastructure, news_dashboards, uncategorized]"}}"""

            headers = {"Authorization": f"Bearer {openrouter_key}", "Content-Type": "application/json"}
            payload = {
                "model": "openrouter/free",
                "messages": [
                    {"role": "system", "content": "Return only valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": 150,
                "temperature": 0.3,
            }

            resp = requests.post(openrouter_url, headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            result = resp.json()["choices"][0]["message"]["content"].strip()

            json_match = re.search(r'\{[^}]+\}', result)
            if json_match:
                scores = json.loads(json_match.group())
                item["ai_relevance"] = scores.get("relevance", 5)
                item["ai_novelty"] = scores.get("novelty", 5)
                item["ai_urgency"] = scores.get("urgency", 5)
                if scores.get("category") and scores["category"] != "uncategorized":
                    item["category"] = scores["category"]
                ai_score = (item["ai_relevance"] + item["ai_novelty"] + item["ai_urgency"]) / 3
                item["score"] = round((item.get("score", 0) * 0.4 + ai_score * 0.6), 2)

            scored_count += 1
            if scored_count % 10 == 0:
                print(f"[scorer] {scored_count}/{ai_budget} scored")
            time.sleep(0.5)
        except Exception as exc:
            print(f"[scorer] Failed: {exc}")

    items.sort(key=lambda i: i.get("score", 0), reverse=True)
    print(f"\n[OK] Scored {len(items)} items ({scored_count} AI-scored)")

    output_file = DATA_DIR / "scored" / f"scored_{dt.date.today().isoformat()}.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(items, indent=2))
    return items
