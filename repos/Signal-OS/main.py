"""
AI Signal Daily - Main Orchestrator
====================================
Runs the complete pipeline: Scrape -> Score -> Write -> Images -> Comments -> Render

Budget: 500 requests per day
"""
import datetime as dt
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from pipeline.scraper import scrape_all
from pipeline.scorer import score_items
from pipeline.writer import write_articles
from pipeline.image_gen import generate_images
from pipeline.commenter import add_comments
from pipeline.renderer import render_page


def print_banner():
    print("""
============================================================
  AI SIGNAL DAILY
  AI-First Tech News Pipeline
============================================================
    """)


def print_phase(phase, description, budget):
    print(f"\n{'='*60}")
    print(f"PHASE {phase}: {description}")
    print(f"Budget: {budget} requests")
    print(f"{'='*60}\n")


def run_pipeline(skip_scraping=False, skip_ai=False, output_dir=None):
    print_banner()
    start_time = time.time()
    date = dt.date.today().isoformat()

    BUDGET_TOTAL = 500
    BUDGET_SCRAPING = 200
    BUDGET_SCORING = 50
    BUDGET_WRITING = 200
    BUDGET_IMAGES = 30
    BUDGET_COMMENTS = 20

    print(f"Date: {date}")
    print(f"Total Budget: {BUDGET_TOTAL} requests")
    print(f"Budget: Scrape={BUDGET_SCRAPING} Score={BUDGET_SCORING} Write={BUDGET_WRITING} Images={BUDGET_IMAGES} Comments={BUDGET_COMMENTS}")

    if not skip_scraping:
        print_phase("1", "SCRAPING", BUDGET_SCRAPING)
        items = scrape_all(budget_total=BUDGET_SCRAPING)
        print(f"\n[OK] Scraped {len(items)} items")
    else:
        print("\n[skip] Skipping scraping...")
        raw_file = ROOT / "data" / "raw" / f"raw_{date}.json"
        if raw_file.exists():
            items = json.loads(raw_file.read_text())
            print(f"Loaded {len(items)} items from {raw_file}")
        else:
            print("ERROR: No raw data found.")
            return

    print_phase("2", "SCORING", BUDGET_SCORING)
    if not skip_ai:
        scored_items = score_items(items, budget_remaining=BUDGET_SCORING)
    else:
        print("[skip] Using keyword scores only...")
        scored_items = items
    print(f"\n[OK] Scored {len(scored_items)} items")

    print_phase("3a", "ARTICLE WRITING", BUDGET_WRITING)
    if not skip_ai:
        articles = write_articles(scored_items, budget=BUDGET_WRITING)
    else:
        print("[skip] Creating stub articles...")
        articles = []
        for idx, item in enumerate(scored_items[:15]):
            articles.append({
                "id": idx + 1,
                "original_title": item.get("title", ""),
                "original_url": item.get("url", ""),
                "original_source": item.get("source", ""),
                "category": item.get("category", "uncategorized"),
                "score": item.get("score", 0),
                "article_type": "news",
                "content": f"[AI article for: {item.get('title', '')}]",
                "headline": item.get("title", ""),
                "written_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                "model_used": "stub",
                "image": None,
                "comments": [],
            })
    print(f"\n[OK] Wrote {len(articles)} articles")

    print_phase("3b", "IMAGE GENERATION", BUDGET_IMAGES)
    if not skip_ai:
        articles = generate_images(articles, budget=BUDGET_IMAGES)
    else:
        print("[skip] Skipping image generation...")
    print(f"\n[OK] Generated {len([a for a in articles if a.get('image')])} images")

    print_phase("3c", "COMMENT GENERATION", BUDGET_COMMENTS)
    if not skip_ai:
        articles = add_comments(articles, budget=BUDGET_COMMENTS)
    else:
        print("[skip] Skipping comment generation...")
    print(f"\n[OK] Added comments to {len(articles)} articles")

    print_phase("4", "RENDERING", 0)
    output_path = render_page(articles, date, output_dir=output_dir)
    print(f"\n[OK] Rendered page at {output_path}")

    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"PIPELINE COMPLETE")
    print(f"{'='*60}")
    print(f"Date: {date}")
    print(f"Items Scraped: {len(items)}")
    print(f"Articles Written: {len(articles)}")
    print(f"Images: {len([a for a in articles if a.get('image')])}")
    print(f"Comments: {len([a for a in articles if a.get('comments')])}")
    print(f"Output: {output_path}")
    print(f"Time: {elapsed:.1f}s")
    print(f"{'='*60}\n")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="AI Signal Daily Pipeline")
    parser.add_argument("--skip-scraping", action="store_true")
    parser.add_argument("--skip-ai", action="store_true")
    parser.add_argument("--output-dir", type=str, default=None)
    args = parser.parse_args()

    try:
        run_pipeline(skip_scraping=args.skip_scraping, skip_ai=args.skip_ai, output_dir=args.output_dir)
    except KeyboardInterrupt:
        print("\n\nPipeline interrupted.")
        sys.exit(1)
    except Exception as exc:
        print(f"\n\nERROR: {exc}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
