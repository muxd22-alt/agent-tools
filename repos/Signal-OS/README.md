# Signal OS

AI-first tech news site. Articles, images, and commentary generated entirely by AI every morning.

**Live site:** `https://<your-username>.github.io/<repo>/`

## How It Works

```
GitHub Actions (7 AM UTC daily)
    |
    v
Scrape (150+ items) --> Score (AI) --> Write Articles (AI) --> Generate Images (AI) --> Add Comments (AI)
    |
    v
docs/index.html --> GitHub Pages --> You read it at 8 AM
```

## Setup

### 1. Enable GitHub Pages

1. Go to your repo **Settings** > **Pages**
2. Source: **Deploy from a branch**
3. Branch: **gh-pages** / **root**
4. Save

### 2. Add Secrets

Go to **Settings** > **Secrets and variables** > **Actions** > **New repository secret**

| Name | Value |
|------|-------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key (free tier works) |

### 3. Enable Actions

Go to **Actions** > **General** > Select **"Allow all workflows"** > Save

The workflow runs automatically at **7:00 UTC daily** (8 AM Arabia Standard Time).

### Manual Trigger

Go to **Actions** > **Daily AI Signal** > **Run workflow** > **Run workflow**

## What Gets Generated

Each daily run produces:

- **15 AI-written articles** (news, analysis, quick takes)
- **AI-generated images** for each article
- **3 AI comments** per article (Expert, Skeptic, Optimist)
- **Beautiful HTML page** at `docs/index.html`

## Budget: 500 Requests/Day

| Phase | Requests | Description |
|-------|----------|-------------|
| Scrape | 200 | RSS, GitHub, ArXiv, HackerNews |
| Score | 50 | AI categorization & relevance scoring |
| Write | 200 | AI article generation |
| Images | 30 | AI image generation (Pollinations.ai) |
| Comments | 20 | AI perspective comments |

## Categories

- AI & Frontier Tech
- Saudi & Economy
- Markets & Finance
- Products & Apps
- Mobile & Infra
- News & Geopolitics

## Local Development

```bash
# Install
pip install -r requirements.txt

# Set API key
export OPENROUTER_API_KEY="sk-or-..."

# Run full pipeline (outputs to docs/)
python main.py --output-dir docs

# Dry run (no AI calls)
python main.py --skip-ai --output-dir docs

# Open locally
open docs/index.html
```

## File Structure

```
.github/workflows/daily.yml   # GitHub Actions (7 AM UTC)
config/
  settings.yaml               # Pipeline config
  categories.yaml             # Scoring categories
sources/
  rss_feeds.yaml              # 15 RSS feeds
  github_trending.yaml        # GitHub search queries
  arxiv_categories.yaml       # ArXiv categories
pipeline/
  scraper.py                  # Phase 1: Scrape
  scorer.py                   # Phase 2: Score + categorize
  writer.py                   # Phase 3a: Write articles
  image_gen.py                # Phase 3b: Generate images
  commenter.py                # Phase 3c: Add AI comments
  renderer.py                 # Phase 4: Render HTML
  free_models.py              # OpenRouter free model picker
docs/
  index.html                  # GitHub Pages (generated daily)
  archive/                    # Past issues
main.py                       # Pipeline orchestrator
```

## Tech Stack

- Python 3.11 (GitHub Actions)
- OpenRouter free-tier LLMs
- Pollinations.ai (free image generation)
- GitHub Pages (hosting)
- GitHub Actions (scheduling)
