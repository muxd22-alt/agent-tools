"""
Phase 3a: Writer - Generates AI articles from scored items.
"""
import datetime as dt
import json
import os
import time
from pathlib import Path
from typing import List, Dict, Any
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


def call_openrouter(model, system_prompt, user_prompt, max_tokens=1500, temperature=0.7):
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        return ""
    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": model, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], "max_tokens": max_tokens, "temperature": temperature},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return ""


def generate_article_prompt(item, article_type):
    title = item.get("title", "")
    summary = item.get("summary", "")
    source = item.get("source", "")
    url = item.get("url", "")

    if article_type == "news":
        system = "You are a professional tech news journalist. Write concise, informative news articles. 400-600 words. Factual, objective tone."
        user = f"Write a news article about:\nTitle: {title}\nSource: {source}\nSummary: {summary}\nURL: {url}\n\nInclude key details and context. Start with a compelling headline."
    elif article_type == "analysis":
        system = "You are a tech industry analyst. Write in-depth analysis exploring implications and trends. 600-800 words."
        user = f"Write an analysis piece about:\nTitle: {title}\nSource: {source}\nSummary: {summary}\nURL: {url}\n\nExplore implications, trends, and future impact. Start with a compelling headline."
    else:
        system = "You are a tech commentator. Write quick, punchy takes. 150-250 words. Be concise and engaging."
        user = f"Write a quick take about:\nTitle: {title}\nSource: {source}\nSummary: {summary}\nURL: {url}\n\nKey insight upfront. Why this matters. Start with a catchy headline."

    return system, user


def determine_article_type(item):
    score = item.get("score", 0)
    h = hash(item.get("title", "")) % 10
    if score >= 8:
        return "analysis" if h < 5 else ("news" if h < 8 else "quick_take")
    elif score >= 6:
        return "news" if h < 4 else ("quick_take" if h < 8 else "analysis")
    else:
        return "quick_take" if h < 6 else "news"


def write_articles(items, budget=200):
    config = load_yaml("settings.yaml")
    daily_target = config.get("articles", {}).get("daily_target", 15)

    print(f"\n{'='*60}")
    print(f"PHASE 3a: ARTICLE WRITING (Budget: {budget})")
    print(f"{'='*60}\n")

    has_key = bool(os.environ.get("OPENROUTER_API_KEY"))
    if not has_key:
        print("[writer] WARNING: No OPENROUTER_API_KEY set. Using fallback content.")

    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from free_models import get_free_models

    writing_model = get_free_models(n=1)[0] if has_key else "fallback"
    print(f"[writer] Model: {writing_model}")

    articles = []
    used = 0

    for idx, item in enumerate(items[:daily_target]):
        if used >= budget:
            break

        article_type = determine_article_type(item)
        print(f"[writer] {idx+1}/{daily_target} ({article_type}): {item['title'][:45]}...")

        content = ""
        if has_key:
            system, user = generate_article_prompt(item, article_type)
            content = call_openrouter(writing_model, system, user)
            used += 1

        # Fallback: use original summary if AI failed
        if not content:
            content = item.get("summary", item.get("title", "No content available."))

        headline = content.split("\n")[0].replace("#", "").strip() if content else item.get("title", "")
        if not headline or len(headline) < 10:
            headline = item.get("title", "Untitled")

        articles.append({
            "id": idx + 1,
            "original_title": item.get("title", ""),
            "original_url": item.get("url", ""),
            "original_source": item.get("source", ""),
            "category": item.get("category", "uncategorized"),
            "score": item.get("score", 0),
            "article_type": article_type,
            "content": content,
            "headline": headline,
            "written_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "model_used": writing_model,
            "image": None,
            "comments": [],
        })
        time.sleep(0.5)

    print(f"\n[OK] Wrote {len(articles)} articles using {used} requests")

    output_file = DATA_DIR / "articles" / f"articles_{dt.date.today().isoformat()}.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(articles, indent=2))
    return articles
