#!/bin/bash
# Swap the localhost vLLM container from 32B-AWQ to Qwen3-8B (sequential).
# Run via: python3 serve/remote.py ssh 'bash -s' < serve/swap_to_8b.sh
set -euo pipefail
LOG=/var/log/tasan-extract-vllm.log
READY=/root/tasan-vllm.ready
rm -f "$READY"
docker rm -f tasan-extract-vllm 2>/dev/null || true
docker run --gpus all --name tasan-extract-vllm --restart no \
  -p 127.0.0.1:8000:8000 \
  -v /root/.cache/huggingface:/root/.cache/huggingface \
  vllm/vllm-openai:latest \
  --model Qwen/Qwen3-8B \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.90 \
  --enforce-eager \
  --host 0.0.0.0 --port 8000 \
  >>"$LOG" 2>&1 &
for i in $(seq 1 180); do
  if curl -sf http://127.0.0.1:8000/v1/models >/dev/null 2>&1; then
    echo "venv-or-docker 8B ready after $i checks $(date -Is)" | tee -a "$LOG"
    echo "docker $(date -Is) Qwen/Qwen3-8B" > "$READY"
    exit 0
  fi
  sleep 5
done
echo "8B vllm failed to become ready" | tee -a "$LOG"
exit 1
