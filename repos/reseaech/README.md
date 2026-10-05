# Qwen Coder Next Research

![Research Progress](progress.png)

> "Scaling is not just about more parameters, but about smarter components. We are hunting for the hybrid architecture of the next generation." — *The Autonomous Researcher*

## 🚀 The Mission: 24-Hour Autonomous Loop
This repository is currently running a **24-hour autonomous research campaign** to discover optimized hybrid architectures inspired by the **Qwen Coder Next 80B** design.

The goal is to find the most efficient combination of **Gated DeltaNet**, **Gated Attention**, and **Mixture of Experts (MoE)** that can fit within a consumer-grade **8GB VRAM** envelope (AMD RX 7600) while maximizing performance.

### Reference Architecture: Qwen Coder Next 80B
*   **Total Parameters**: 80B (3B activated)
*   **Components**: Hybrid MoE + Gated DeltaNet + Gated Attention
*   **Performance Targets**: SWE-bench Pro: 44.3, SWE-bench Verified: 70.6

## 🛠️ Current Research Setup
*   **Hardware**: AMD Radeon RX 7600 (8GB VRAM) 
*   **Platform**: Windows + ROCm 7.2 + PyTorch (BF16)
*   **Autonomous Agent**: Research Loop driven by `qwen3.5-18b-reap-a3b` guidance.
*   **Time Budget**: 300s (5-minute) training windows.
*   **Metric**: `val_bpb` (Bits per Byte) — lower is better.

## 🔬 How to Monitor
Experiments are pushed live to the repository. You can track progress via:
1.  **`results.tsv`**: A complete history of all architectural mutations and their scores.
2.  **`run.log`**: Live training output from the current experiment.
3.  **`backups/`**: Historically significant versions of the architecture.

## 🧱 Architectural Components being Researched

### 1. Gated DeltaNet
A linear attention mechanism utilizing the Delta rule for weight updates, integrated with a gating unit for controlled information flow. High efficiency for long-context reasoning.

### 2. Gated GQA (Grouped Query Attention)
Standard high-performance attention augmented with a learnable gating mechanism to modulate the attention heads, mirroring the density of much larger models.

### 3. Sparse MoE (Mixture of Experts)
Implementing Top-K routing with a shared expert. The research agent is currently iterating on the optimal ratio of experts vs. shared capacity for 8GB constraints.

---

## Progress Tracking
We are targeting **~100-150 experiments** in this 24-hour window. Each experiment evolves the `train.py` file to test new hypotheses suggested by the LLM researcher.

**Current Record Holder:** Check [`results.tsv`](results.tsv) for the latest `val_bpb` champion.

---
*Results published and reused at [github.com/muxd22-alt/reseaech](https://github.com/muxd22-alt/reseaech)*
