---
description: Run the autonomous research loop on local AMD ROCm hardware with Nemotron 3 Nano 4B guidance
---

# AutoResearch Local Workflow (AMD ROCm + Nemotron)

This workflow runs Karpathy's autoresearch experiment loop on local hardware:
- **GPU**: AMD RX 7600 (8GB VRAM, ROCm/HIP)
- **RAM**: 32GB
- **LLM Guide**: nvidia/nemotron-3-nano-4b at http://100.67.202.80:3003

## Prerequisites

1. ROCm 6.0+ installed with `gfx1102` target (RX 7600)
2. Python 3.10+ with `uv` package manager
3. Nemotron model running and accessible at http://100.67.202.80:3003

## Setup Steps

### 1. Verify ROCm & GPU Detection
// turbo
```powershell
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'ROCm/HIP: {torch.version.hip}'); print(f'GPU: {torch.cuda.get_device_name(0)}'); print(f'VRAM: {torch.cuda.get_device_properties(0).total_mem / 1024**3:.1f} GB')"
```

### 2. Verify Nemotron API is reachable
// turbo
```powershell
curl http://100.67.202.80:3003/v1/models
```

### 3. Install dependencies
```powershell
cd d:\autoresearch && uv sync
```

### 4. Prepare data (one-time, downloads TinyStories + trains tokenizer)
```powershell
cd d:\autoresearch && uv run prepare.py --num-shards 8
```

### 5. Test a single baseline training run (~5 min)
```powershell
cd d:\autoresearch && uv run train.py > run.log 2>&1
```

### 6. Check training results
// turbo
```powershell
cd d:\autoresearch && Select-String -Path run.log -Pattern "^val_bpb:|^peak_vram_mb:"
```

### 7. Start the autonomous research agent
```powershell
cd d:\autoresearch && python research_agent.py
```
The agent will loop indefinitely:
- Read current code and results
- Ask Nemotron for experiment ideas
- Modify train.py
- Run training (5 min)
- Log results
- Keep improvements, discard regressions

Press Ctrl+C to stop the agent.

## Key Files

| File | Purpose |
|------|---------|
| `train.py` | Model/training code (agent modifies this) |
| `prepare.py` | Data prep & eval (DO NOT modify) |
| `program.md` | Agent instructions |
| `research_agent.py` | Autonomous loop powered by Nemotron |
| `results.tsv` | Experiment log |
| `run.log` | Latest training output |

## Hardware Tuning Notes

- **DEPTH**: Start with 4 (vs default 8) to fit in 8GB VRAM
- **DEVICE_BATCH_SIZE**: Start with 16 (vs default 128)
- **WINDOW_PATTERN**: Use "L" (full attention only, no sliding window)
- **TOTAL_BATCH_SIZE**: Use 2**15 (~32K tokens)
- If OOM: reduce DEPTH to 2, DEVICE_BATCH_SIZE to 8
- torch.compile is disabled on ROCm (enable with PyTorch 2.9+ ROCm)
