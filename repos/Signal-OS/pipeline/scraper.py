"""
Phase 1: Scraper - Fetches news from multiple sources.
Budget: 200 requests for scraping.
"""
import datetime as dt
import hashlib
import json
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any
import requests
import yaml

ROOT = Path(__file__).parent.parent
SOURCES_DIR = ROOT / "sources"
DATA_DIR = ROOT / "data" / "raw"


class RequestBudget:
    def __init__(self, total, requests_per_minute=16):
        self.total = total
        self.used = 0
        self.requests_per_minute = requests_per_minute
        self.last_request_time = 0

    def can_make_request(self):
        return self.used < self.total

    def record_request(self):
        self.used += 1
        self.last_request_time = time.time()

    def wait_if_needed(self):
        if self.used > 0 and self.used % self.requests_per_minute == 0:
            elapsed = time.time() - self.last_request_time
            if elapsed < 60:
                time.sleep(60 - elapsed)

    def remaining(self):
        return self.total - self.used


def load_yaml(filename):
    path = SOURCES_DIR / filename
    if path.exists():
        return yaml.safe_load(path.read_text())
    return {}


def make_request(url, budget, headers=None, timeout=10):
    if not budget.can_make_request():
        return None
    budget.wait_if_needed()
    default_headers = {"User-Agent": "AI-Signal-Daily/1.0"}
    if headers:
        default_headers.update(headers)
    try:
        resp = requests.get(url, headers=default_headers, timeout=timeout)
        resp.raise_for_status()
        budget.record_request()
        return resp
    except Exception as exc:
        print(f"[scraper] Request failed: {url}: {exc}")
        return None


def scrape_rss(budget):
    config = load_yaml("rss_feeds.yaml")
    feeds = config.get("feeds", [])
    settings = config.get("settings", {})
    timeout = settings.get("timeout", 10)
    max_items = settings.get("max_items_per_feed", 20)
    items = []

    for feed in feeds:
        if not budget.can_make_request():
            break
        print(f"[rss] {feed['name']}...")
        resp = make_request(feed["url"], budget, timeout=timeout)
        if resp is None:
            continue
        try:
            root = ET.fromstring(resp.content)
            namespace = {"atom": "http://www.w3.org/2005/Atom"}
            entries = root.findall(".//item") or root.findall(".//atom:entry", namespace)
            for entry in entries[:max_items]:
                item = parse_rss_entry(entry, feed, namespace)
                if item:
                    items.append(item)
            print(f"[rss] Got {min(len(entries), max_items)} from {feed['name']}")
        except Exception as exc:
            print(f"[rss] Failed to parse {feed['name']}: {exc}")
    return items


def parse_rss_entry(entry, feed, namespace):
    try:
        import re
        title = entry.findtext("title") or ""
        link = entry.findtext("link") or ""
        description = entry.findtext("description") or ""
        pub_date = entry.findtext("pubDate") or ""

        if not title:
            el = entry.find("atom:title", namespace)
            title = el.text if el is not None else ""
        if not link:
            el = entry.find("atom:link", namespace)
            link = el.get("href", "") if el is not None else ""
        if not description:
            el = entry.find("atom:summary", namespace) or entry.find("atom:content", namespace)
            description = el.text if el is not None else ""
        if not pub_date:
            el = entry.find("atom:updated", namespace) or entry.find("atom:published", namespace)
            pub_date = el.text if el is not None else ""

        description = re.sub(r'<[^>]+>', '', description)[:500]

        return {
            "title": title.strip(),
            "url": link.strip(),
            "summary": description.strip(),
            "source": feed["name"],
            "source_type": "rss",
            "category_hint": feed.get("category", ""),
            "published": pub_date,
            "scraped_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        }
    except Exception:
        return None


def scrape_github(budget):
    config = load_yaml("github_trending.yaml")
    queries = config.get("search_queries", [])
    settings = config.get("settings", {})
    timeout = settings.get("timeout", 10)
    max_results = settings.get("max_results_per_query", 20)
    items = []

    for qc in queries:
        if not budget.can_make_request():
            break
        query = qc["query"]
        category = qc.get("category", "")
        print(f"[github] Searching: {query}...")
        url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page={max_results}"
        resp = make_request(url, budget, timeout=timeout)
        if resp is None:
            continue
        try:
            data = resp.json()
            repos = data.get("items", [])
            for repo in repos[:max_results]:
                items.append({
                    "title": f"{repo['full_name']}: {repo.get('description', '')[:100]}",
                    "url": repo["html_url"],
                    "summary": repo.get("description", ""),
                    "source": "github",
                    "source_type": "github",
                    "category_hint": category,
                    "published": repo.get("created_at", ""),
                    "stars": repo.get("stargazers_count", 0),
                    "language": repo.get("language", ""),
                    "scraped_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                })
            print(f"[github] Got {len(repos)} for '{query}'")
        except Exception as exc:
            print(f"[github] Failed: {exc}")
    return items


def scrape_arxiv(budget):
    config = load_yaml("arxiv_categories.yaml")
    categories = config.get("categories", [])
    settings = config.get("settings", {})
    timeout = settings.get("timeout", 15)
    max_results = settings.get("max_results_per_category", 15)
    items = []

    for cat_config in categories:
        if not budget.can_make_request():
            break
        cat_id = cat_config["id"]
        category = cat_config.get("category", "")
        print(f"[arxiv] {cat_id}...")
        url = f"http://export.arxiv.org/api/query?search_query=cat:{cat_id}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
        resp = make_request(url, budget, timeout=timeout)
        if resp is None:
            continue
        try:
            root = ET.fromstring(resp.content)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            entries = root.findall("atom:entry", ns)
            for entry in entries:
                item = parse_arxiv_entry(entry, ns)
                if item:
                    item["category_hint"] = category
                    item["source"] = "arxiv"
                    item["source_type"] = "arxiv"
                    item["scraped_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
                    items.append(item)
            print(f"[arxiv] Got {len(entries)} from {cat_id}")
        except Exception as exc:
            print(f"[arxiv] Failed: {exc}")
    return items


def parse_arxiv_entry(entry, ns):
    try:
        title = entry.findtext("atom:title", namespaces=ns) or ""
        summary = entry.findtext("atom:summary", namespaces=ns) or ""
        published = entry.findtext("atom:published", namespaces=ns) or ""
        link_el = entry.find("atom:link[@type='text/html']", ns)
        if link_el is None:
            link_el = entry.find("atom:link", ns)
        link = link_el.get("href", "") if link_el is not None else ""
        return {
            "title": " ".join(title.split()),
            "url": link,
            "summary": " ".join(summary.split())[:500],
            "published": published,
        }
    except Exception:
        return None


def scrape_hackernews(budget):
    items = []
    print("[hn] Fetching top stories...")
    resp = make_request("https://hacker-news.firebaseio.com/v0/topstories.json", budget, timeout=10)
    if resp is None:
        return items
    try:
        story_ids = resp.json()[:30]
        for sid in story_ids:
            if not budget.can_make_request():
                break
            resp = make_request(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", budget, timeout=10)
            if resp is None:
                continue
            story = resp.json()
            if story and story.get("type") == "story":
                items.append({
                    "title": story.get("title", ""),
                    "url": story.get("url", f"https://news.ycombinator.com/item?id={sid}"),
                    "summary": (story.get("text", "") or "")[:500],
                    "source": "hackernews",
                    "source_type": "hackernews",
                    "category_hint": "",
                    "published": dt.datetime.fromtimestamp(story.get("time", 0), tz=dt.timezone.utc).isoformat(),
                    "score": story.get("score", 0),
                    "scraped_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                })
        print(f"[hn] Got {len(items)} stories")
    except Exception as exc:
        print(f"[hn] Failed: {exc}")
    return items


def deduplicate(items):
    seen_urls = set()
    seen_titles = set()
    unique = []
    for item in items:
        url = item.get("url", "")
        title = item.get("title", "").lower().strip()[:50]
        url_hash = hashlib.md5(url.encode()).hexdigest() if url else None
        if url_hash in seen_urls or title in seen_titles:
            continue
        if url_hash:
            seen_urls.add(url_hash)
        if title:
            seen_titles.add(title)
        unique.append(item)
    return unique


def scrape_all(budget_total=200):
    budget = RequestBudget(budget_total)
    print(f"\n{'='*60}")
    print(f"PHASE 1: SCRAPING (Budget: {budget_total} requests)")
    print(f"{'='*60}\n")

    all_items = []
    all_items.extend(scrape_rss(budget))
    all_items.extend(scrape_github(budget))
    all_items.extend(scrape_arxiv(budget))
    all_items.extend(scrape_hackernews(budget))

    unique = deduplicate(all_items)
    print(f"\n{'='*60}")
    print(f"SCRAPED: {len(unique)} unique items from {budget.used} requests")
    print(f"{'='*60}\n")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_file = DATA_DIR / f"raw_{dt.date.today().isoformat()}.json"
    output_file.write_text(json.dumps(unique, indent=2))
    print(f"Saved to {output_file}")
    return unique


if __name__ == "__main__":
    items = scrape_all()
    print(f"\nTotal: {len(items)} items")
