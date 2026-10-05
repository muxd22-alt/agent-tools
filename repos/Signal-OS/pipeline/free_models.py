"""
Picks N distinct-provider, currently-free models from OpenRouter's live catalog.
"""
import random
import requests

OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"
FALLBACK_MODEL = "openrouter/free"


def get_free_models(n=3, timeout=10):
    """Return up to n model IDs, each from a different provider, that are free."""
    try:
        resp = requests.get(OPENROUTER_MODELS_URL, timeout=timeout)
        resp.raise_for_status()
        catalog = resp.json().get("data", [])
    except Exception:
        return [FALLBACK_MODEL] * n

    def is_free(m):
        pricing = m.get("pricing", {})
        try:
            return float(pricing.get("prompt", 1)) == 0.0 and float(pricing.get("completion", 1)) == 0.0
        except (TypeError, ValueError):
            return False

    free = [m for m in catalog if is_free(m) and m.get("id")]
    if not free:
        return [FALLBACK_MODEL] * n

    by_provider = {}
    for m in free:
        provider = m["id"].split("/")[0]
        by_provider.setdefault(provider, []).append(m["id"])

    providers = list(by_provider.keys())
    random.shuffle(providers)

    chosen = []
    for provider in providers:
        if len(chosen) >= n:
            break
        chosen.append(random.choice(by_provider[provider]))

    while len(chosen) < n:
        chosen.append(FALLBACK_MODEL)

    return chosen
