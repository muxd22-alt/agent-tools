"""
Autonomous Research Agent for autoresearch.
Uses a local LLM (Nemotron 3 Nano 4B) to generate experiment ideas,
modify train.py, run training, and iterate.

Usage: python research_agent.py [--api-url URL] [--max-experiments N]
"""

import os
import sys
import re
import json
import time
import argparse
import subprocess
import datetime
import shutil
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_API_URL = "http://100.67.202.80:3003"
TRAIN_FILE = "train.py"
RESULTS_FILE = "results.tsv"
RUN_LOG = "run.log"
PROGRAM_FILE = "program.md"
PREPARE_FILE = "prepare.py"
BACKUP_DIR = "backups"
MAX_RUN_TIMEOUT = 1800  # 30 minutes max per run

# ---------------------------------------------------------------------------
# LLM API Client
# ---------------------------------------------------------------------------

class NemotronClient:
    """Client for the local Nemotron 3 Nano 4B API (OpenAI-compatible)."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.chat_url = f"{self.base_url}/v1/chat/completions"
        self.model = self._detect_model()
        print(f"[Agent] Connected to model: {self.model} at {self.base_url}")

    def _detect_model(self) -> str:
        """Auto-detect the model name from the API."""
        try:
            resp = requests.get(f"{self.base_url}/v1/models", timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if "data" in data and len(data["data"]) > 0:
                return data["data"][0]["id"]
        except Exception as e:
            print(f"[Agent] Warning: Could not detect model name: {e}")
        return "nvidia/nemotron-3-nano-4b"

    def chat(self, messages: list, temperature: float = 0.7, max_tokens: int = 4096) -> str:
        """Send a chat completion request and return the response text."""
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        try:
            resp = requests.post(self.chat_url, json=payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"[Agent] LLM API error: {e}")
            return ""

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def read_file(path: str) -> str:
    """Read a file and return its contents."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_file(path: str, content: str):
    """Write content to a file."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def backup_file(path: str, backup_dir: str = BACKUP_DIR):
    """Create a timestamped backup of a file."""
    os.makedirs(backup_dir, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    name = Path(path).stem
    ext = Path(path).suffix
    backup_path = os.path.join(backup_dir, f"{name}_{ts}{ext}")
    shutil.copy2(path, backup_path)
    return backup_path

def git_commit(message: str) -> str:
    """Stage all changes and commit, return short hash."""
    try:
        subprocess.run(["git", "add", "."], check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", message], check=True, capture_output=True)
        # Push to origin
        subprocess.run(["git", "push", "origin", "HEAD"], check=False, capture_output=True)
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            check=True, capture_output=True, text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"[Agent] Git operation failed: {e}")
        return "unknown"

def git_reset_hard(commit_hash: str):
    """Reset to a specific commit."""
    try:
        subprocess.run(["git", "reset", "--hard", commit_hash], check=True, capture_output=True)
        print(f"[Agent] Reset to {commit_hash}")
    except subprocess.CalledProcessError as e:
        print(f"[Agent] Git reset failed: {e}")

def git_current_hash() -> str:
    """Get current short commit hash."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            check=True, capture_output=True, text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "unknown"

def run_training() -> dict:
    """
    Run `uv run train.py > run.log 2>&1` and parse results.
    Returns dict with val_bpb, peak_vram_mb, status, or crash info.
    """
    print("[Agent] Starting training run...")
    t0 = time.time()

    try:
        with open(RUN_LOG, "w") as log_file:
            process = subprocess.run(
                ["uv", "run", "train.py"],
                stdout=log_file,
                stderr=subprocess.STDOUT,
                timeout=MAX_RUN_TIMEOUT,
                cwd=os.getcwd(),
            )
        elapsed = time.time() - t0
        print(f"[Agent] Training completed in {elapsed:.1f}s (exit code: {process.returncode})")

        if process.returncode != 0:
            # Read tail of log for error
            log_content = read_file(RUN_LOG)
            tail = "\n".join(log_content.strip().split("\n")[-50:])
            return {"status": "crash", "error": tail, "val_bpb": 0.0, "peak_vram_mb": 0.0}

    except subprocess.TimeoutExpired:
        print(f"[Agent] Training TIMED OUT after {MAX_RUN_TIMEOUT}s")
        return {"status": "crash", "error": "Timeout exceeded", "val_bpb": 0.0, "peak_vram_mb": 0.0}

        # Parse results from log
        log_content = read_file(RUN_LOG)
        results = {"status": "ok", "val_bpb": 0.0, "peak_vram_mb": 0.0, "tok_sec": 0.0, "error": ""}

        for line in log_content.split("\n"):
            line = line.strip()
            if line.startswith("val_bpb:"):
                try: results["val_bpb"] = float(line.split(":")[1].strip())
                except: pass
            elif line.startswith("peak_vram_mb:"):
                try: results["peak_vram_mb"] = float(line.split(":")[1].strip())
                except: pass
            elif "tok/sec:" in line:
                try:
                    parts = line.split("|")
                    for p in parts:
                        if "tok/sec:" in p:
                            val = p.split(":")[1].strip().replace(",", "")
                            results["tok_sec"] = float(val)
                except: pass

        if results["val_bpb"] == 0.0:
            tail = "\n".join(log_content.strip().split("\n")[-50:])
            results["status"] = "crash"
            results["error"] = tail

        return results

def init_results_tsv():
    """Create results.tsv with header if it doesn't exist."""
    if not os.path.exists(RESULTS_FILE):
        write_file(RESULTS_FILE, "commit\tval_bpb\tmemory_gb\ttok_sec\tstatus\tdescription\n")
        print(f"[Agent] Created {RESULTS_FILE}")

def append_result(commit: str, val_bpb: float, memory_gb: float, tok_sec: float, status: str, description: str):
    """Append a result row to results.tsv."""
    with open(RESULTS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{commit}\t{val_bpb:.6f}\t{memory_gb:.1f}\t{tok_sec:.1f}\t{status}\t{description}\n")

def get_results_history() -> str:
    """Read the full results.tsv contents."""
    if os.path.exists(RESULTS_FILE):
        return read_file(RESULTS_FILE)
    return "commit\tval_bpb\tmemory_gb\tstatus\tdescription\n"

def get_best_val_bpb() -> float:
    """Get the best (lowest) val_bpb from results history."""
    best = float("inf")
    if os.path.exists(RESULTS_FILE):
        for line in read_file(RESULTS_FILE).strip().split("\n")[1:]:  # skip header
            parts = line.split("\t")
            if len(parts) >= 4 and parts[3] == "keep":
                try:
                    bpb = float(parts[1])
                    if bpb > 0 and bpb < best:
                        best = bpb
                except ValueError:
                    pass
    return best


# ---------------------------------------------------------------------------
# Experiment Proposal via LLM
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an autonomous AI researcher working on optimizing a small GPT language model.
You are running experiments on a constrained setup:
- AMD RX 7600 GPU with 8GB VRAM (ROCm/HIP)
- 32GB system RAM
- Each experiment trains for exactly 5 minutes
- The metric is val_bpb (validation bits per byte) — LOWER is better

Your job is to propose ONE specific change to train.py that might improve val_bpb.
You should focus on things like:
- Hyperparameter tuning (learning rates, batch sizes, weight decay, warmup/warmdown)
- Architecture changes (depth, aspect ratio, head dim, window pattern)
- Optimizer tweaks (Muon parameters, momentum, betas)
- Activation functions, normalization changes
- Any other creative ideas that could help within the 8GB VRAM constraint

CRITICAL CONSTRAINTS:
- You can ONLY modify train.py. Never modify prepare.py.
- The model MUST fit in 8GB VRAM. Be conservative.
- torch.compile is DISABLED (ROCm). Don't rely on compilation.
- Flash Attention 3 is NOT available. Using PyTorch SDPA instead.
- Keep changes simple and focused. ONE idea per experiment.
- Do NOT install new packages. Only use what's in pyproject.toml.

When proposing a change, respond in this EXACT format:

DESCRIPTION: <one-line description of what you're changing>
REASONING: <brief explanation of why this might help>
CHANGES:
```python
# Show the exact lines to find and replace in train.py
# Use FIND/REPLACE blocks:

### FIND ###
<exact lines from train.py to find>
### REPLACE ###
<replacement lines>
### END ###
```
"""

def propose_experiment(llm: NemotronClient, train_code: str, results_history: str, attempt: int = 0) -> dict:
    """
    Ask the LLM for a new experiment idea.
    Returns dict with 'description', 'reasoning', and 'changes' (list of find/replace pairs).
    """
    user_msg = f"""Here is the current train.py code:

```python
{train_code}
```

Here are the experiment results so far:

```
{results_history}
```

Current best val_bpb: {get_best_val_bpb():.6f}

{"This is experiment #" + str(attempt + 1) + ". " if attempt > 0 else ""}Please propose ONE specific change to try next. Remember: 8GB VRAM limit, no torch.compile, no FA3.
Give a focused, surgical change — not a complete rewrite."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_msg},
    ]

    response = llm.chat(messages, temperature=0.8, max_tokens=4096)
    if not response:
        return None

    # Parse the response
    result = {"description": "", "reasoning": "", "changes": []}

    # Extract description
    desc_match = re.search(r"DESCRIPTION:\s*(.+?)(?:\n|$)", response)
    if desc_match:
        result["description"] = desc_match.group(1).strip()

    # Extract reasoning
    reason_match = re.search(r"REASONING:\s*(.+?)(?:\nCHANGES:|$)", response, re.DOTALL)
    if reason_match:
        result["reasoning"] = reason_match.group(1).strip()

    # Extract FIND/REPLACE blocks
    find_replace_pattern = r"### FIND ###\s*\n(.*?)\n### REPLACE ###\s*\n(.*?)\n### END ###"
    for match in re.finditer(find_replace_pattern, response, re.DOTALL):
        result["changes"].append({
            "find": match.group(1).strip(),
            "replace": match.group(2).strip(),
        })

    # Fallback: try to extract from code block if no FIND/REPLACE found
    if not result["changes"]:
        code_match = re.search(r"```python\s*\n(.*?)```", response, re.DOTALL)
        if code_match:
            # In this case we'll try to apply the whole block as a diff
            result["raw_code"] = code_match.group(1).strip()

    return result

def apply_changes(train_code: str, changes: list) -> str:
    """Apply FIND/REPLACE changes to train.py code."""
    modified = train_code
    for change in changes:
        find_text = change["find"]
        replace_text = change["replace"]
        if find_text in modified:
            modified = modified.replace(find_text, replace_text, 1)
            print(f"[Agent] Applied change: {find_text[:60]}... -> {replace_text[:60]}...")
        else:
            print(f"[Agent] WARNING: Could not find text to replace:")
            print(f"  Looking for: {find_text[:100]}...")
            return None  # Signal that the change couldn't be applied
    return modified


# ---------------------------------------------------------------------------
# Main Agent Loop
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Autonomous Research Agent")
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help="Nemotron API URL")
    parser.add_argument("--max-experiments", type=int, default=-1, help="Max experiments (-1 = unlimited)")
    parser.add_argument("--skip-baseline", action="store_true", help="Skip baseline run if results.tsv has entries")
    args = parser.parse_args()

    # Change to project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    print(f"[Agent] Working directory: {project_dir}")

    # Initialize
    llm = NemotronClient(args.api_url)
    init_results_tsv()

    # Check if we need a baseline
    results_history = get_results_history()
    need_baseline = len(results_history.strip().split("\n")) <= 1  # only header
    if args.skip_baseline and not need_baseline:
        print("[Agent] Skipping baseline (results.tsv already has entries)")
        need_baseline = False

    if need_baseline:
        print("=" * 70)
        print("[Agent] STEP 1: Running baseline experiment")
        print("=" * 70)

        # Backup original
        backup_file(TRAIN_FILE)

        # Git commit current state as baseline
        base_hash = git_current_hash()

        # Run baseline
        result = run_training()
        if result["status"] == "crash":
            print(f"[Agent] BASELINE CRASHED! Error:\n{result.get('error', 'Unknown')}")
            print("[Agent] Fix train.py and re-run. Exiting.")
            sys.exit(1)

        val_bpb = result["val_bpb"]
        memory_gb = result["peak_vram_mb"] / 1024
        tok_sec = result.get("tok_sec", 0.0)
        append_result(base_hash, val_bpb, memory_gb, tok_sec, "keep", "baseline")
        print(f"[Agent] Baseline: val_bpb={val_bpb:.6f}, memory={memory_gb:.1f}GB, throughput={tok_sec:.1f} t/s")

    # Main experiment loop
    experiment_num = 0
    consecutive_failures = 0
    MAX_CONSECUTIVE_FAILURES = 5

    while True:
        if args.max_experiments > 0 and experiment_num >= args.max_experiments:
            print(f"\n[Agent] Reached max experiments ({args.max_experiments}). Stopping.")
            break

        experiment_num += 1
        print("\n" + "=" * 70)
        print(f"[Agent] EXPERIMENT #{experiment_num}")
        print(f"[Agent] TARGET: Qwen Coder Next 80B Reference")
        print("=" * 70)

        # Read current state
        train_code = read_file(TRAIN_FILE)
        results_history = get_results_history()
        best_bpb = get_best_val_bpb()
        pre_experiment_hash = git_current_hash()

        print(f"[Agent] Current best val_bpb: {best_bpb:.6f}")
        print(f"[Agent] Current commit: {pre_experiment_hash}")

        # Get experiment proposal from LLM
        print("[Agent] Asking Nemotron for experiment idea...")
        proposal = propose_experiment(llm, train_code, results_history, experiment_num)

        if not proposal or (not proposal["changes"] and "raw_code" not in proposal):
            print("[Agent] LLM returned no actionable proposal. Retrying...")
            consecutive_failures += 1
            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                print(f"[Agent] {MAX_CONSECUTIVE_FAILURES} consecutive failures. Taking a break and retrying with higher temperature...")
                consecutive_failures = 0
                time.sleep(30)
            continue

        description = proposal.get("description", "unknown change")
        reasoning = proposal.get("reasoning", "")
        print(f"[Agent] Proposal: {description}")
        if reasoning:
            print(f"[Agent] Reasoning: {reasoning[:200]}")

        # Apply changes
        if proposal["changes"]:
            modified_code = apply_changes(train_code, proposal["changes"])
        elif "raw_code" in proposal:
            print("[Agent] Using raw code block (no FIND/REPLACE). Skipping to avoid overwriting entire file.")
            consecutive_failures += 1
            continue
        else:
            print("[Agent] No changes to apply. Skipping.")
            consecutive_failures += 1
            continue

        if modified_code is None:
            print("[Agent] Could not apply changes (text not found). Skipping.")
            consecutive_failures += 1
            continue

        if modified_code == train_code:
            print("[Agent] Changes resulted in no diff. Skipping.")
            consecutive_failures += 1
            continue

        # Write modified code and commit
        backup_file(TRAIN_FILE)
        write_file(TRAIN_FILE, modified_code)
        commit_hash = git_commit(f"experiment: {description[:60]}")
        print(f"[Agent] Committed as {commit_hash}")

        # Run training
        result = run_training()
        tok_sec = result.get("tok_sec", 0.0)

        if result["status"] == "crash":
            print(f"[Agent] CRASH! Error (tail):")
            error_lines = result.get("error", "Unknown error")
            for line in error_lines.strip().split("\n")[-10:]:
                print(f"  {line}")

            append_result(commit_hash, 0.0, 0.0, 0.0, "crash", description)
            git_reset_hard(pre_experiment_hash)
            print(f"[Agent] Reverted to {pre_experiment_hash}")
            consecutive_failures += 1
            continue

        val_bpb = result["val_bpb"]
        memory_gb = result["peak_vram_mb"] / 1024

        print(f"[Agent] Result: val_bpb={val_bpb:.6f}, memory={memory_gb:.1f}GB, tok/sec={tok_sec:.1f}")

        if val_bpb < best_bpb:
            # Improvement! Keep it.
            improvement = best_bpb - val_bpb
            print(f"[Agent] *** IMPROVEMENT: {improvement:.6f} lower! Keeping. ***")
            append_result(commit_hash, val_bpb, memory_gb, tok_sec, "keep", description)
            consecutive_failures = 0
            best_bpb = val_bpb
        else:
            # No improvement, discard
            regression = val_bpb - best_bpb
            print(f"[Agent] No improvement (+{regression:.6f}). Discarding.")
            append_result(commit_hash, val_bpb, memory_gb, tok_sec, "discard", description)
            git_reset_hard(pre_experiment_hash)
            print(f"[Agent] Reverted to {pre_experiment_hash}")

        consecutive_failures = 0  # successful run resets counter

    # Print final summary
    print("\n" + "=" * 70)
    print("[Agent] FINAL SUMMARY")
    print("=" * 70)
    print(get_results_history())
    print(f"Best val_bpb: {get_best_val_bpb():.6f}")


if __name__ == "__main__":
    main()
