# ── 1단계: React 빌드 ────────────────────────────────────────────
FROM node:22-alpine AS frontend-builder

RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app/frontend

COPY frontend/package.json ./
RUN pnpm install

COPY frontend/ .
RUN pnpm run build

# ── 2단계: Django 실행 ────────────────────────────────────────────
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 시스템 의존성
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
 && rm -rf /var/lib/apt/lists/*

# Python 의존성
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Django 소스
COPY backend/ .

# React 빌드 결과물 (static/index.html, static/assets/)
COPY --from=frontend-builder /app/backend/static ./static

# 정적 파일 수집 (whitenoise용)
RUN SECRET_KEY=build python manage.py collectstatic --noinput

# 비루트 사용자
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

CMD sh -c "gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2"
