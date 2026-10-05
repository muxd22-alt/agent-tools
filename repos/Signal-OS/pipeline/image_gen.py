"""
Phase 3b: Image Generator - Generates AI images for articles.
Uses Pollinations.ai (free, no API key).
"""
import datetime as dt
import json
import time
import requests
from pathlib import Path
from typing import List, Dict, Any
import yaml

ROOT = Path(__file__).parent.parent
CONFIG_DIR = ROOT / "config"
DATA_DIR = ROOT / "data"


def load_yaml(filename):
    path = CONFIG_DIR / filename
    if path.exists():
        return yaml.safe_load(path.read_text())
    return {}


def generate_image_prompt(article):
    headline = article.get("headline", "")
    category = article.get("category", "")

    style_map = {
        "frontier_intelligence": "futuristic AI, neural networks, glowing circuits, purple blue",
        "saudi_global_economy": "modern Middle Eastern city, economic growth, gold green",
        "financial_markets": "stock charts, trading floor, data visualization, blue",
        "products_platforms": "modern product design, sleek interface, orange accent",
        "mobile_infrastructure": "mobile devices, network, connectivity, red accent",
        "news_dashboards": "newsroom, data dashboard, information display, yellow accent",
    }
    style = style_map.get(category, "modern technology, clean design")

    return f"Professional tech news featured image: {headline[:80]}. Style: {style}. Clean, modern, editorial quality, 16:9, no text."


def generate_with_pollinations(prompt, width=1024, height=576):
    try:
        import urllib.parse
        encoded = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&nologo=true"
        resp = requests.get(url, timeout=120, stream=True)
        resp.raise_for_status()

        image_dir = DATA_DIR / "images"
        image_dir.mkdir(parents=True, exist_ok=True)
        ts = int(time.time() * 1000)
        path = image_dir / f"img_{ts}.jpg"

        with open(path, 'wb') as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)
        return str(path)
    except Exception as exc:
        print(f"[image] Failed: {exc}")
        return None


def generate_images(articles, budget=30):
    config = load_yaml("settings.yaml")
    enabled = config.get("images", {}).get("enabled", True)

    print(f"\n{'='*60}")
    print(f"PHASE 3b: IMAGE GENERATION (Budget: {budget})")
    print(f"{'='*60}\n")

    if not enabled:
        print("[image] Disabled in config")
        return articles

    used = 0
    for idx, article in enumerate(articles):
        if used >= budget:
            break

        print(f"[image] {idx+1}/{len(articles)}: {article.get('headline', '')[:40]}...")
        prompt = generate_image_prompt(article)
        path = generate_with_pollinations(prompt)
        used += 1

        if path:
            article["image"] = {"path": path, "prompt": prompt, "generated_at": dt.datetime.now(dt.timezone.utc).isoformat()}
        else:
            article["image"] = None

        time.sleep(2)

    print(f"\n[OK] Generated {len([a for a in articles if a.get('image')])} images")

    output_file = DATA_DIR / "articles" / f"articles_{dt.date.today().isoformat()}.json"
    output_file.write_text(json.dumps(articles, indent=2))
    return articles
