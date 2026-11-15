# Tasan Pathway Twin - one container run = one county x scenario job.
# CPU-only numpy; no cloud SDK and no credentials inside the image.
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 TASAN_OUT=/results PORT=8000
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY twin/ twin/
COPY config/ config/
# Built, sourced inputs (make targets calibrate params) - the image does not need junction-new/data.
COPY build/targets.json build/posterior.json build/parameters.json build/calibration_report.json build/
RUN useradd -m tasan && mkdir -p /results && chown tasan /results
USER tasan
EXPOSE 8000
# Default = Verda batch-job HTTP mode (GET /health, one POST /run, then exit).
# Local / plain-batch mode: docker run ... tasan-twin python -m twin.cli run --county 21 --scenario mid --seed 1 --n-runs 1000 --out /results
CMD ["python", "-m", "twin.server"]
