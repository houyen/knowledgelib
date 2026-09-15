---
id: software/system-design/book-60-days/day-50-serving-ml-models-at-high-throughput
canonical_question: Serving ML Models at High Throughput
aliases:
- System Design Day 50
- Serving ML Models at High Throughput
- Day 50 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 50: Serving ML Models at High Throughput

DAY 50 · SYSTEM DESIGN
Serving ML Models at High Throughput
Your ML team trained a model that hits 94% accuracy in the notebook.
Then you deploy it.
Peak traffic: 3,000 inference requests/second.
P99 latency shoots to 4.2 seconds.
GPU utilization: 23%.
The model works. The serving layer is the bottleneck.
Here's the setup:
• PyTorch model, ~6B params
• Single A100 GPU, 80GB VRAM
• FastAPI wrapper calling model.predict() one request at a time
• No batching, FP32 weights, no quantization
Users are hitting timeouts. GPUs are sitting mostly idle. Your infra bill is climbing.
What do you fix first?

---

DAY 50 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Answer: A — Dynamic Batching ✅
Here's the breakdown:
Why A wins (Dynamic Batching):
The smoking gun is the combination: 3K RPS, P99 = 4.2s, GPU utilization = 23%.
GPU utilization at 23% tells you the GPU is starving. It's not overloaded — it's bored. Every request is
arriving one at a time, paying the full GPU kernel launch overhead, then idling while the next request
trickles in. GPUs are built for parallelism. They want 256 inputs to process simultaneously, not 1.
Dynamic batching buffers requests for a few milliseconds (say, 50ms), collects 32–128 of them, and
fires a single forward pass. That same GPU that was at 23% utilization can jump to 85–90%. Latency
improves because batch throughput dramatically outpaces sequential per-request calls, even with the
small buffer wait.
This is exactly how NVIDIA Triton Inference Server, TorchServe, and vLLM (for LLMs) work by default.
Batching is the first thing you reach for when GPU util is low and RPS is high.
