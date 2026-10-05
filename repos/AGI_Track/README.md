# AGI Horizon Tracker — Decision Intelligence Platform

A source-grounded **Decision Intelligence Platform** that aggregates, scores, and analyzes daily research signals across three frontier AGI capability pillars: **Autonomous Scientific R&D**, **Formal Mathematical Proofs**, and **Vast Software Systems**.

Designed through the lens of a **Data Product Manager & BI Analyst**, this system transitions from a passive "data display" dashboard to an active **Decision Intelligence Engine** answering 5 strategic questions:

> **What changed? → Why did it change? → So what? → What should we do? → How confident are we?**

---

## 🏛️ Architectural Philosophy: Decision Intelligence Layer

Rather than presenting raw lists of preprints or commits, the platform structures data into an auditable intelligence hierarchy:

```text
  [ Raw Data Sources ]  (arXiv API, GitHub REST API, Hugging Face Daily Papers)
           │
           ▼
  [ Data Fetcher & Normalization ]
           │
           ▼
  [ Signal Scoring & Ranking Engine ]  (Rule-based filtering: Novelty × Quality × Independence)
           │
           ▼
  [ Evidence & Contradiction Engine ]  (Thesis vs. Anti-Thesis / Supporting vs. Contradicting)
           │
           ▼
  [ OpenRouter Analytical Layer ]     (Structured Reasoning via GitHub Secrets OPENROUTER_API_KEY)
           │
           ▼
  [ Executive Decision Brief ]        (Strict JSON Output: Regime, Confidence, Implications)
           │
           ▼
  [ React BI Dashboard UI ]           (High-Contrast Executive Command Center)
```

---

## ⚡ Signal Scoring Engine

Every incoming signal is evaluated against a 6-factor quantitative heuristic before being passed to the analytical engine:

$$\text{Signal Score} = \text{Novelty} \times \text{Evidence Quality} \times \text{Source Independence} \times \text{Magnitude} \times \text{Relevance} \times \text{Persistence}$$

*Normalized to a 0–100 scale.*

```text
AI Inference Efficiency Breakthrough      Score: 91  (Top Priority)
Semiconductor Capacity Expansion           Score: 67  (Medium Priority)
Unverified Startup Announcement            Score: 31  (Filtered Out)
```

This prevents noise and ensures only the top 5–10 high-confidence signals reach executive attention.

---

## 📦 Unified Signal Object Schema

Every signal in `public/data/latest_data.json` adheres to a unified data object schema:

```json
{
  "id": "SIG-2026-00921",
  "timestamp": "2026-09-06T12:00:00Z",
  "pillar": "software_systems",
  "topic": "Inference Efficiency",
  "signal_type": "TECHNICAL",
  "direction": "POSITIVE",
  "magnitude": 0.78,
  "novelty": 0.84,
  "confidence": 0.91,
  "importance": 0.88,
  "source_count": 6,
  "independent_sources": 4,
  "evidence_quality": 0.86,
  "time_horizon": "90D",
  "impact": {
    "technology": 0.90,
    "business": 0.72,
    "market": 0.63
  },
  "title": "A Case Study on Emergent Cheating in Autonomous Research Swarms",
  "summary": "Multi-agent research swarms accelerate scientific literature synthesis...",
  "why_it_matters": "Shifts human scientific role from initial draft generation to high-level peer verification.",
  "supporting_evidence": [
    "http://arxiv.org/abs/2609.04170v1",
    "https://github.com/example/swarm-repo"
  ],
  "contradicting_evidence": [
    "Evaluation on non-synthetic benchmarks shows 14% hallucination rate"
  ],
  "recommended_action": "Increase monitoring weight on multi-agent safety verification tools.",
  "verification": {
    "status": "pending",
    "commands": ["curl -s http://export.arxiv.org/api/query?id_list=2609.04170v1"]
  }
}
```

---

## 🧠 OpenRouter Integration (Analytical Layer)

The system utilizes **OpenRouter** (authenticated via `OPENROUTER_API_KEY` stored securely in **GitHub Secrets**) as an analytical reasoning layer — **never as the source of raw truth**.

### Configuration-Driven Model Routing
```python
MODELS = {
    "extractor": "google/gemini-flash-1.5",
    "classifier": "meta-llama/llama-3.3-70b-instruct",
    "analyst": "anthropic/claude-3.5-sonnet",
    "executive": "openai/gpt-4o-mini"
}
```

### Analytical Prompt Directive
The LLM is strictly constrained:
- **Rule 1:** Do not invent facts or infer missing empirical metrics.
- **Rule 2:** Compare incoming data against the 30-day baseline.
- **Rule 3:** Identify supporting vs. contradicting evidence (thesis vs. anti-thesis).
- **Rule 4:** Output strict JSON conforming to the Executive Decision Brief schema.

---

## ⚖️ Contradiction Engine & Net Confidence

To avoid single-sided hype, the platform tracks both **Supporting Evidence** and **Contradicting Evidence**:

```text
THESIS: Autonomous Coding Agents approaching human baseline on SWE-bench
├── Supporting Evidence (+): 11 new commits in Lean 4 mathlib, 8 coding agent PRs merged
└── Contradicting Evidence (-): Benchmark evaluation indicates edge-case fragility on non-python repos
Net Confidence Score: 82 / 100
```

---

## 📈 Data Product Quality KPIs

As a self-governing Data Product, the system measures its own analytical health:

| Metric | Target | Description |
| :--- | :--- | :--- |
| **Signal Coverage** | > 85% | Percentage of tracked research channels covered daily |
| **Source Diversity** | > 75% | Ratio of independent domain sources (arXiv vs. GitHub vs. Hugging Face) |
| **Evidence Freshness** | < 24 hrs | Mean latency from paper submission to signal ingestion |
| **Duplicate Rate** | < 5% | Deduplication efficiency across aggregated APIs |
| **AI Agreement Score**| > 80% | Heuristic vs. LLM rating alignment |

---

## 🤖 Automated Zero-Maintenance Pipeline

The entire system runs autonomously on GitHub Actions:

```text
.github/workflows/daily-update.yml  (Runs nightly at 00:00 UTC)
     │
     ├── 1. Execute data/scraper.py (Fetch raw signals from arXiv, GitHub, Hugging Face)
     ├── 2. Run Signal Scoring & Deduplication Engine
     ├── 3. Query OpenRouter API (Secrets.OPENROUTER_API_KEY) for Executive Brief Synthesis
     ├── 4. Commit updated JSON payload to main branch
     └── 5. Trigger .github/workflows/deploy.yml to build Vite app & deploy to GitHub Pages
```

---

## 💻 Tech Stack & Design System

- **Frontend:** React, Vite, Tailwind CSS, Recharts, Lucide Icons.
- **Typography:** Inter, IBM Plex Mono, and **Thmanyah Sans** (Native Arabic font support).
- **Backend / Scraper:** Python 3.11 (`requests`, `xml.etree.ElementTree`).
- **AI Analytics:** OpenRouter API (`OPENROUTER_API_KEY`).
- **Hosting:** GitHub Pages.
