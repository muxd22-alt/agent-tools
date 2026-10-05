"""
Phase 3c: Commenter - Adds AI comments to articles.
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


def call_openrouter(model, system_prompt, user_prompt, max_tokens=300, temperature=0.8):
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        return ""
    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": model, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], "max_tokens": max_tokens, "temperature": temperature},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return ""


PERSONAS = {
    "expert": "You are a senior tech expert. Provide a concise technical comment (2-3 sentences). Focus on technical implications.",
    "skeptic": "You are a critical thinker. Provide a skeptical comment (2-3 sentences). What's missing or overhyped?",
    "optimist": "You are a tech optimist. Provide an optimistic comment (2-3 sentences). What does this enable?",
}


def generate_comment(persona, article, model):
    system = PERSONAS[persona]
    user = f"Comment on this article:\nHeadline: {article.get('headline', '')}\nCategory: {article.get('category', '')}\nContent: {article.get('content', '')[:400]}"
    text = call_openrouter(model, system, user)
    return {"persona": persona, "text": text, "model": model, "generated_at": dt.datetime.now(dt.timezone.utc).isoformat()}


def add_comments(articles, budget=20):
    print(f"\n{'='*60}")
    print(f"PHASE 3c: COMMENT GENERATION (Budget: {budget})")
    print(f"{'='*60}\n")

    has_key = bool(os.environ.get("OPENROUTER_API_KEY"))
    if not has_key:
        print("[commenter] WARNING: No OPENROUTER_API_KEY. Skipping comments.")
        return articles

    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from free_models import get_free_models

    models = get_free_models(n=3)
    print(f"[commenter] Models: {models}")

    used = 0
    personas = list(PERSONAS.keys())

    for idx, article in enumerate(articles):
        if used >= budget:
            break

        print(f"[commenter] {idx+1}/{len(articles)}: {article.get('headline', '')[:40]}...")
        comments = []
        for i, persona in enumerate(personas):
            if used >= budget:
                break
            model = models[i % len(models)]
            comments.append(generate_comment(persona, article, model))
            used += 1
            time.sleep(0.3)

        article["comments"] = comments
        time.sleep(0.5)

    print(f"\n[OK] Added comments to {len(articles)} articles ({used} requests)")

    output_file = DATA_DIR / "articles" / f"articles_{dt.date.today().isoformat()}.json"
    output_file.write_text(json.dumps(articles, indent=2))
    return articles
