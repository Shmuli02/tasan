#!/bin/bash
# Tasan Extract phase 2 wrap-up — SWEEP ONLY (no LoRA).
# LoRA was started on 715c7100 but failed before the first optimizer step
# (transformers 5.20 TrainingArguments rejected warmup_ratio) and is recorded
# as started, not completed. This session finishes the A100 1/8/32/64 sweep
# for 8B base and 32B-AWQ.
# SYNTHETIC data only. Bind vLLM to the docker port published on 127.0.0.1.
# No Cloud API secrets on this box. Controller API-deletes the instance.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
WORK=/root/tasan-work
OUT=/root/tasan-extract-out
LOG=/var/log/tasan-extract-p2.log
DONE=/root/tasan-extract-DONE
FAIL=/root/tasan-extract-FAILED
READY_MARK=/root/tasan-vllm.ready
WATCHDOG_MIN="${TASAN_WATCHDOG_MIN:-90}"
mkdir -p "$WORK" "$OUT" /root/.cache/huggingface
rm -f "$DONE" "$FAIL" "$READY_MARK"
exec > >(tee -a "$LOG") 2>&1
echo "[p2] sweep-only start $(date -Is) watchdog=${WATCHDOG_MIN}m"

if [ "${TASAN_ENABLE_REMOTE_WATCHDOG:-1}" = "1" ]; then
  nohup bash -c "sleep $((WATCHDOG_MIN * 60)); echo watchdog-halt \$(date -Is) >> $LOG; shutdown -h now" \
    >/dev/null 2>&1 &
  echo "[p2] remote halt pid $!"
fi

fail() {
  echo "[p2] FAIL: $*" | tee "$FAIL"
  mkdir -p "$OUT"
  cp -a "$LOG" "$OUT/session.log" 2>/dev/null || true
  docker logs tasan-extract-vllm > "$OUT/vllm.docker.log" 2>&1 || true
  tar -czf /root/tasan-extract-out.tgz -C "$OUT" . || true
  exit 1
}

nvidia-smi -L || fail "no gpu"
export HF_HOME=/root/.cache/huggingface
command -v python3 >/dev/null || apt-get install -y -qq python3 python3-venv python3-pip curl
command -v curl >/dev/null || apt-get install -y -qq curl

if [ -f /root/payload.tgz ]; then
  mkdir -p "$WORK"
  tar -xzf /root/payload.tgz -C "$WORK"
fi
cd "$WORK"
export PYTHONPATH=/work/extract

echo "[p2] docker pull vllm"
docker pull vllm/vllm-openai:latest

serve_vllm() {
  local model="$1"
  local extra="${2:-}"
  docker rm -f tasan-extract-vllm 2>/dev/null || true
  rm -f "$READY_MARK"
  # shellcheck disable=SC2086
  docker run --gpus all --name tasan-extract-vllm --restart no \
    -p 127.0.0.1:8000:8000 \
    -v "$HF_HOME:/root/.cache/huggingface" \
    vllm/vllm-openai:latest \
    --model "$model" \
    --max-model-len 8192 \
    --gpu-memory-utilization 0.90 \
    --enforce-eager \
    --host 0.0.0.0 --port 8000 \
    $extra >>"$LOG" 2>&1 &
  for i in $(seq 1 240); do
    if curl -sf http://127.0.0.1:8000/v1/models >/dev/null 2>&1; then
      echo "[p2] vllm ready model=$model after ${i} checks $(date -Is)"
      echo "docker $(date -Is) $model" > "$READY_MARK"
      return 0
    fi
    sleep 5
  done
  fail "vllm not ready for $model"
}

run_sweep() {
  local model="$1" tag="$2" price="${3:-2.386}"
  python3 -u /work/extract/eval/throughput_sweep.py \
    --corpus /work/extract/corpus/data_v2_test \
    --base-url http://127.0.0.1:8000/v1 \
    --model "$model" \
    --limit 32 --conc 1,8,32,64 \
    --tag "$tag" --price "$price"
  mkdir -p "$OUT/sweep"
  cp -a /work/extract/eval/results/throughput_${tag}_*.json "$OUT/sweep/" 2>/dev/null || true
}

echo "[p2] serve 8B base $(date -Is)"
serve_vllm "Qwen/Qwen3-8B"
echo "[p2] sweep 8B base"
run_sweep "Qwen/Qwen3-8B" "8b_base" 2.386

echo "[p2] swap to 32B AWQ $(date -Is)"
docker rm -f tasan-extract-vllm 2>/dev/null || true
sleep 3
serve_vllm "Qwen/Qwen3-32B-AWQ" "--quantization awq"
echo "[p2] sweep 32B AWQ"
run_sweep "Qwen/Qwen3-32B-AWQ" "32b_awq" 2.386

docker rm -f tasan-extract-vllm 2>/dev/null || true
echo "[p2] packing results"
cp -a "$LOG" "$OUT/session.log" || true
tar -czf /root/tasan-extract-out.tgz -C "$OUT" .
echo "[p2] complete $(date -Is)" | tee "$DONE"
