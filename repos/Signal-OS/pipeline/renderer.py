"""
Phase 4: Renderer - Generates final HTML page for GitHub Pages.
Outputs to docs/index.html.
"""
import datetime as dt
import html
import json
import base64
from pathlib import Path
from typing import List, Dict, Any

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
DEFAULT_OUTPUT_DIR = ROOT / "docs"


def get_category_meta():
    return {
        "frontier_intelligence": {"label": "AI & Frontier Tech", "color": "#8E6FE0", "gradient": "linear-gradient(135deg, #8E6FE0, #6366f1)"},
        "saudi_global_economy": {"label": "Saudi & Economy", "color": "#4C9A6A", "gradient": "linear-gradient(135deg, #4C9A6A, #22c55e)"},
        "financial_markets": {"label": "Markets & Finance", "color": "#4A90D9", "gradient": "linear-gradient(135deg, #4A90D9, #3b82f6)"},
        "products_platforms": {"label": "Products & Apps", "color": "#E67E22", "gradient": "linear-gradient(135deg, #E67E22, #f97316)"},
        "mobile_infrastructure": {"label": "Mobile & Infra", "color": "#E74C3C", "gradient": "linear-gradient(135deg, #E74C3C, #ef4444)"},
        "news_dashboards": {"label": "News & Geopolitics", "color": "#F1C40F", "gradient": "linear-gradient(135deg, #F1C40F, #eab308)"},
        "uncategorized": {"label": "Tech News", "color": "#64748b", "gradient": "linear-gradient(135deg, #64748b, #475569)"},
    }


def get_image_base64(image_path):
    try:
        with open(image_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
            ext = Path(image_path).suffix.lower()
            mime = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}.get(ext, "image/jpeg")
            return f"data:{mime};base64,{data}"
    except Exception:
        return None


def fmt(content):
    paras = content.split("\n\n")
    return "\n".join(f"<p>{html.escape(p.strip())}</p>" for p in paras if p.strip())


def trunc(text, mx=220):
    text = text.strip()
    return text if len(text) <= mx else text[:mx].rsplit(" ", 1)[0] + "..."


def gen_hero(a, cm):
    cat = cm.get(a.get("category", ""), cm["uncategorized"])
    img = ""
    if a.get("image") and a["image"].get("path"):
        d = get_image_base64(a["image"]["path"])
        if d:
            img = f'<div class="hero-img"><img src="{d}" alt="" loading="eager"></div>'
    tp = a.get("article_type", "news").replace("_", " ").upper()
    return f"""
    <section class="hero">
      <a href="{html.escape(a.get('original_url', '#'))}" target="_blank" rel="noopener" class="hero-link">
        {img}
        <div class="hero-overlay">
          <div class="hero-meta">
            <span class="badge" style="background: {cat['gradient']}">{cat['label']}</span>
            <span class="badge badge-type">{tp}</span>
            <span class="score-pill">{a.get('score', 0):.1f}</span>
          </div>
          <h1 class="hero-title">{html.escape(a.get('headline', ''))}</h1>
          <p class="hero-excerpt">{html.escape(trunc(a.get('content', ''), 200))}</p>
          <div class="hero-source"><span class="src-dot" style="background:{cat['color']}"></span>{html.escape(a.get('original_source', ''))}</div>
        </div>
      </a>
    </section>"""


def gen_card(a, cm):
    cat = cm.get(a.get("category", ""), cm["uncategorized"])
    img = ""
    if a.get("image") and a["image"].get("path"):
        d = get_image_base64(a["image"]["path"])
        if d:
            img = f'<div class="card-img"><img src="{d}" alt="" loading="lazy"></div>'
    tp = a.get("article_type", "news").replace("_", " ").upper()

    comments_html = ""
    for c in a.get("comments", [])[:2]:
        t = c.get("text", "")[:120]
        if t and not t.startswith("("):
            comments_html += f'<div class="cc"><span class="cc-p">{html.escape(c.get("persona",""))}</span><span class="cc-t">{html.escape(t)}{"..." if len(c.get("text",""))>120 else ""}</span></div>'

    return f"""
    <article class="card" data-cat="{html.escape(a.get('category',''))}">
      <a href="{html.escape(a.get('original_url','#'))}" target="_blank" rel="noopener">
        {img}
        <div class="card-body">
          <div class="card-meta">
            <span class="badge badge-sm" style="background:{cat['gradient']}">{cat['label']}</span>
            <span class="score-pill score-sm">{a.get('score',0):.1f}</span>
          </div>
          <h2 class="card-title">{html.escape(a.get('headline',''))}</h2>
          <p class="card-excerpt">{html.escape(trunc(a.get('content',''), 150))}</p>
          <div class="card-foot"><span>{html.escape(a.get('original_source',''))}</span><span class="card-type">{tp}</span></div>
        </div>
      </a>
      {f'<div class="card-comments">{comments_html}</div>' if comments_html else ''}
    </article>"""


def generate_page(articles, date=None):
    if not date:
        date = dt.date.today().isoformat()
    cm = get_category_meta()

    hero = articles[0] if articles else None
    cards = articles[1:] if len(articles) > 1 else []

    hero_html = gen_hero(hero, cm) if hero else ""
    cards_html = "\n".join(gen_card(a, cm) for a in cards)

    cats_used = sorted(set(a.get("category", "uncategorized") for a in articles))
    chips = '<button class="chip active" data-cat="all">All</button>'
    for cid in cats_used:
        c = cm.get(cid, cm["uncategorized"])
        chips += f'<button class="chip" data-cat="{cid}">{c["label"]}</button>'

    total = len(articles)
    avg = sum(a.get("score", 0) for a in articles) / max(total, 1)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Signal Daily &mdash; {date}</title>
<meta name="description" content="AI-curated tech news. Articles, images, and commentary generated entirely by AI.">
<meta name="theme-color" content="#000000">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{--bg:#000;--card:#111;--border:#222;--text:#f5f5f7;--dim:#a1a1a6;--muted:#6e6e73;--accent:#2997ff;--green:#30d158;--r:16px;--rs:12px;--max:1120px}}
html{{scroll-behavior:smooth}}
body{{font-family:'Inter',-apple-system,BlinkMacSystemFont,sans-serif;background:var(--bg);color:var(--text);line-height:1.5;-webkit-font-smoothing:antialiased}}
a{{color:inherit;text-decoration:none}}
.wrap{{max-width:var(--max);margin:0 auto;padding:0 20px}}

nav{{position:sticky;top:0;z-index:100;background:rgba(0,0,0,.72);backdrop-filter:saturate(180%) blur(20px);-webkit-backdrop-filter:saturate(180%) blur(20px);border-bottom:1px solid var(--border)}}
.nav-in{{max-width:var(--max);margin:0 auto;padding:0 20px;height:52px;display:flex;align-items:center;justify-content:space-between}}
.nav-brand{{font-weight:700;font-size:17px;letter-spacing:-.02em;display:flex;align-items:center;gap:8px}}
.nav-dot{{width:8px;height:8px;border-radius:50%;background:var(--green);box-shadow:0 0 6px rgba(48,209,88,.6)}}
.nav-date{{font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--muted);letter-spacing:.04em}}

.hero{{margin:24px 0 32px}}
.hero-link{{display:block;position:relative;border-radius:var(--r);overflow:hidden;background:var(--card);transition:transform .25s,box-shadow .25s}}
.hero-link:hover{{transform:translateY(-2px);box-shadow:0 12px 40px rgba(0,0,0,.5)}}
.hero-img{{width:100%;aspect-ratio:16/7;overflow:hidden;background:#1c1c1e}}
.hero-img img{{width:100%;height:100%;object-fit:cover;display:block}}
.hero-overlay{{padding:28px 32px 32px;background:linear-gradient(0deg,rgba(0,0,0,.95) 0%,rgba(0,0,0,.6) 60%,transparent 100%);position:absolute;bottom:0;left:0;right:0}}
.hero-meta{{display:flex;gap:8px;margin-bottom:14px;flex-wrap:wrap;align-items:center}}
.hero-title{{font-size:clamp(24px,4vw,36px);font-weight:800;line-height:1.15;letter-spacing:-.03em;margin-bottom:10px}}
.hero-excerpt{{font-size:15px;color:var(--dim);line-height:1.55;max-width:640px;margin-bottom:12px}}
.hero-source{{font-size:13px;color:var(--muted);display:flex;align-items:center;gap:6px}}
.src-dot{{width:6px;height:6px;border-radius:50%;flex-shrink:0}}

.badge{{display:inline-flex;align-items:center;font-size:11px;font-weight:600;letter-spacing:.03em;padding:4px 10px;border-radius:20px;color:#fff;text-transform:uppercase;white-space:nowrap}}
.badge-type{{background:rgba(255,255,255,.15);backdrop-filter:blur(4px)}}
.badge-sm{{font-size:10px;padding:3px 8px}}
.score-pill{{font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:600;background:rgba(41,151,255,.15);color:var(--accent);padding:4px 10px;border-radius:20px}}
.score-sm{{font-size:10px;padding:3px 8px}}

.chips{{display:flex;gap:8px;padding:0 0 28px;overflow-x:auto;scrollbar-width:none}}
.chips::-webkit-scrollbar{{display:none}}
.chip{{flex-shrink:0;background:#1c1c1e;border:1px solid var(--border);color:var(--dim);font-size:13px;font-weight:500;padding:8px 18px;border-radius:20px;cursor:pointer;transition:all .2s}}
.chip:hover{{background:#1a1a1a;color:var(--text)}}
.chip.active{{background:#fff;color:#000;border-color:#fff}}

.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:20px;padding-bottom:48px}}

.card{{background:var(--card);border-radius:var(--rs);overflow:hidden;border:1px solid var(--border);transition:transform .2s,box-shadow .2s}}
.card:hover{{transform:translateY(-2px);box-shadow:0 8px 24px rgba(0,0,0,.4)}}
.card-img{{width:100%;aspect-ratio:16/9;overflow:hidden;background:#1c1c1e}}
.card-img img{{width:100%;height:100%;object-fit:cover;display:block;transition:transform .3s}}
.card:hover .card-img img{{transform:scale(1.03)}}
.card-body{{padding:18px 20px 16px}}
.card-meta{{display:flex;gap:6px;margin-bottom:10px;align-items:center}}
.card-title{{font-size:17px;font-weight:700;line-height:1.3;letter-spacing:-.01em;margin-bottom:8px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}}
.card-excerpt{{font-size:14px;color:var(--dim);line-height:1.5;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;margin-bottom:12px}}
.card-foot{{display:flex;justify-content:space-between;align-items:center;font-size:12px;color:var(--muted)}}
.card-type{{font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:.06em}}

.card-comments{{padding:0 20px 16px;display:flex;flex-direction:column;gap:8px}}
.cc{{background:#1c1c1e;border-radius:8px;padding:10px 12px}}
.cc-p{{display:block;font-size:10px;font-weight:600;color:var(--accent);margin-bottom:2px;font-family:'JetBrains Mono',monospace;letter-spacing:.02em}}
.cc-t{{font-size:12px;color:var(--muted);line-height:1.45}}

footer{{border-top:1px solid var(--border);padding:32px 0;text-align:center}}
footer p{{font-size:13px;color:var(--muted);margin-bottom:4px}}
.ai-tag{{display:inline-flex;align-items:center;gap:6px;font-size:12px;color:var(--muted);background:#1c1c1e;padding:6px 14px;border-radius:20px;margin-top:12px}}
.ai-dot{{width:6px;height:6px;border-radius:50%;background:var(--green);box-shadow:0 0 4px rgba(48,209,88,.5)}}

@media(max-width:768px){{.hero-overlay{{padding:20px 20px 24px}}.hero-title{{font-size:22px}}.grid{{grid-template-columns:1fr}}}}
@media(max-width:480px){{.nav-date{{display:none}}}}

.card,.hero-link{{opacity:0;transform:translateY(16px);animation:fadeUp .5s ease forwards}}
.hero-link{{animation-delay:.05s}}
.card:nth-child(1){{animation-delay:.1s}}
.card:nth-child(2){{animation-delay:.15s}}
.card:nth-child(3){{animation-delay:.2s}}
.card:nth-child(4){{animation-delay:.25s}}
.card:nth-child(5){{animation-delay:.3s}}
.card:nth-child(6){{animation-delay:.35s}}
.card:nth-child(7){{animation-delay:.4s}}
.card:nth-child(8){{animation-delay:.45s}}
.card:nth-child(9){{animation-delay:.5s}}
@keyframes fadeUp{{to{{opacity:1;transform:translateY(0)}}}}
</style>
</head>
<body>
<nav><div class="nav-in"><div class="nav-brand"><span class="nav-dot"></span>AI Signal Daily</div><div class="nav-date">{date}</div></div></nav>
<main class="wrap">
  <div style="padding:20px 0 0;display:flex;gap:20px;flex-wrap:wrap;font-size:13px;color:var(--muted)">
    <span><strong style="color:var(--text)">{total}</strong> stories</span>
    <span><strong style="color:var(--text)">{avg:.1f}</strong> avg score</span>
    <span><strong style="color:var(--text)">{len(cats_used)}</strong> categories</span>
    <span style="color:var(--accent)">100% AI-generated</span>
  </div>
  <div class="chips">{chips}</div>
  {hero_html}
  <div class="grid">{cards_html}</div>
</main>
<footer><div class="wrap"><p>AI Signal Daily &mdash; Curated by AI, for you</p><p>All articles, images, and commentary are AI-generated.</p><div class="ai-tag"><span class="ai-dot"></span>Powered by free-tier LLMs via OpenRouter</div></div></footer>
<script>
var chips = document.querySelectorAll('.chip');
chips.forEach(function(b){{b.addEventListener('click', function(){{chips.forEach(function(x){{x.classList.remove('active')}});b.classList.add('active');var c = b.dataset.cat;document.querySelectorAll('.card').forEach(function(x){{x.style.display = (c === 'all' || x.dataset.cat === c) ? '' : 'none'}})}})}});
</script>
</body>
</html>"""


def render_page(articles, date=None, output_dir=None):
    print(f"\n{'='*60}")
    print(f"PHASE 4: RENDERING")
    print(f"{'='*60}\n")

    if not date:
        date = dt.date.today().isoformat()

    out_dir = Path(output_dir) if output_dir else DEFAULT_OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    page = generate_page(articles, date)
    out = out_dir / "index.html"
    out.write_text(page, encoding="utf-8")
    print(f"[renderer] Saved {len(articles)} articles to {out}")

    archive = out_dir / "archive"
    archive.mkdir(parents=True, exist_ok=True)
    (archive / f"{date}.html").write_text(page, encoding="utf-8")
    print(f"[renderer] Archive: {archive / date}.html")

    print(f"{'='*60}\nRENDERING COMPLETE\n{'='*60}\n")
    return str(out)


if __name__ == "__main__":
    f = DATA_DIR / "articles" / f"articles_{dt.date.today().isoformat()}.json"
    if f.exists():
        render_page(json.loads(f.read_text()))
    else:
        print("No articles found.")
