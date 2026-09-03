FROM python:3.11.15-slim-bookworm@sha256:77923445c077d8eb971b14b2b114a1d9cd4a87edb4c75654820ca4832ee8cb15 AS builder

WORKDIR /build
COPY requirements.lock ./
RUN pip install --no-cache-dir --require-hashes --prefix=/install -r requirements.lock


FROM python:3.11.15-slim-bookworm@sha256:77923445c077d8eb971b14b2b114a1d9cd4a87edb4c75654820ca4832ee8cb15 AS production

ARG VERSION=dev
ARG REVISION=unknown

LABEL org.opencontainers.image.source="https://github.com/raydevkit/kerykeion" \
      org.opencontainers.image.licenses="AGPL-3.0" \
      org.opencontainers.image.revision="${REVISION}" \
      org.opencontainers.image.version="${VERSION}"

RUN useradd --system --uid 10001 --no-create-home --home-dir /nonexistent appuser

WORKDIR /app
COPY --from=builder /install /usr/local
COPY app ./app
COPY kerykeion ./kerykeion
COPY LICENSE ./LICENSE

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENVIRONMENT=production \
    APP_VERSION=${VERSION} \
    GIT_REVISION=${REVISION} \
    HOME=/tmp \
    XDG_CACHE_HOME=/tmp

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=5).read()"]

CMD ["python", "-m", "app.main"]
