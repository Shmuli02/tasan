#!/bin/bash
# Tasan Extract — start vLLM on this GPU box (32B AWQ first).
# SYNTHETIC eval only. Do not copy real patient notes onto the instance.
# Never export Cloud API secrets here. Bind vLLM to 127.0.0.1 only.
set -euo pipefail

MODEL="${TASAN_MODEL:-Qwen/Qwen3-32B-AWQ}"
PORT="${TASAN_VLLM_PORT:-8000}"
MAX_LEN="${TASAN_MAX_MODEL_LEN:-8192}"
UTIL="${TASAN_GPU_MEM_UTIL:-0.90}"
WATCHDOG_MIN="${TASAN_WATCHDOG_MIN:-150}"
QUANT="${TASAN_QUANT:-awq}"
LOG=/var/log/tasan-extract-vllm.log
READY=/root/tasan-vllm.ready
mkdir -p /root
rm -f "$READY"

echo "[tasan-extract] starting $(date -Is) model=${MODEL} quant=${QUANT}" | tee -a "$LOG"

if [ "${TASAN_ENABLE_REMOTE_WATCHDOG:-1}" = "1" ]; then
  nohup bash -c "sleep $((WATCHDOG_MIN * 60)); echo watchdog-halt \$(date -Is) >> $LOG; shutdown -h now" \
    >/dev/null 2>&1 &
  echo "[tasan-extract] remote halt watchdog ${WATCHDOG_MIN} min pid $!" | tee -a "$LOG"
fi

nvidia-smi -L 2>&1 | tee -a "$LOG" || true

export HF_HOME="${HF_HOME:-/root/.cache/huggingface}"
mkdir -p "$HF_HOME"

have_gpu_docker() {
  command -v docker >/dev/null 2>&1 || return 1
  docker info >/dev/null 2>&1 || return 1
  docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi >/dev/null 2>&1
}

install_docker_if_needed() {
  if command -v docker >/dev/null 2>&1; then
    return 0
  fi
  echo "[tasan-extract] docker missing; installing" | tee -a "$LOG"
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -qq
  apt-get install -y -qq ca-certificates curl gnupg
  curl -fsSL https://get.docker.com | sh
  if ! dpkg -s nvidia-container-toolkit >/dev/null 2>&1; then
    curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
    curl -fsSL https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
      | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
      > /etc/apt/sources.list.d/nvidia-container-toolkit.list
    apt-get update -qq
    apt-get install -y -qq nvidia-container-toolkit || true
    nvidia-ctk runtime configure --runtime=docker || true
    systemctl restart docker || service docker restart || true
  fi
}

start_via_docker() {
  echo "[tasan-extract] pulling vllm image" | tee -a "$LOG"
  docker pull vllm/vllm-openai:latest
  docker rm -f tasan-extract-vllm 2>/dev/null || true
  extra=()
  if [ -n "$QUANT" ] && [ "$QUANT" != "none" ]; then
    extra+=(--quantization "$QUANT")
  fi
  echo "[tasan-extract] launching vllm via docker" | tee -a "$LOG"
  docker run --gpus all --name tasan-extract-vllm --restart no \
    -p 127.0.0.1:${PORT}:8000 \
    -v "${HF_HOME}:/root/.cache/huggingface" \
    -e HUGGING_FACE_HUB_TOKEN="${HUGGING_FACE_HUB_TOKEN:-}" \
    vllm/vllm-openai:latest \
    --model "${MODEL}" \
    "${extra[@]}" \
    --max-model-len "${MAX_LEN}" \
    --gpu-memory-utilization "${UTIL}" \
    --enforce-eager \
    --host 0.0.0.0 --port 8000 \
    >>"$LOG" 2>&1 &
  # Wait until the API answers (download may take a long time)
  for i in $(seq 1 360); do
    if curl -sf "http://127.0.0.1:${PORT}/v1/models" >/dev/null 2>&1; then
      echo "[tasan-extract] ready via docker after ${i} checks $(date -Is)" | tee -a "$LOG"
      echo "docker $(date -Is) ${MODEL}" > "$READY"
      return 0
    fi
    sleep 10
  done
  echo "[tasan-extract] docker vllm failed to become ready" | tee -a "$LOG"
  return 1
}

start_via_venv() {
  echo "[tasan-extract] launching vllm via python venv" | tee -a "$LOG"
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -qq
  apt-get install -y -qq python3 python3-venv python3-pip python3-dev curl
  python3 -m venv /root/vllmenv
  # shellcheck disable=SC1091
  source /root/vllmenv/bin/activate
  pip install -U pip wheel
  pip install vllm
  extra=()
  if [ -n "$QUANT" ] && [ "$QUANT" != "none" ]; then
    extra+=(--quantization "$QUANT")
  fi
  python -m vllm.entrypoints.openai.api_server \
    --model "${MODEL}" \
    "${extra[@]}" \
    --max-model-len "${MAX_LEN}" \
    --gpu-memory-utilization "${UTIL}" \
    --enforce-eager \
    --host 127.0.0.1 --port "${PORT}" \
    >>"$LOG" 2>&1 &
  for i in $(seq 1 360); do
    if curl -sf "http://127.0.0.1:${PORT}/v1/models" >/dev/null 2>&1; then
      echo "[tasan-extract] ready via venv after ${i} checks $(date -Is)" | tee -a "$LOG"
      echo "venv $(date -Is) ${MODEL}" > "$READY"
      return 0
    fi
    sleep 10
  done
  echo "[tasan-extract] venv vllm failed to become ready" | tee -a "$LOG"
  return 1
}

install_docker_if_needed || true
if have_gpu_docker || (command -v docker >/dev/null && docker info >/dev/null 2>&1); then
  if start_via_docker; then
    wait
    exit 0
  fi
fi
start_via_venv
wait
