FROM node:24-alpine AS frontend-builder

WORKDIR /build/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build


FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN useradd --create-home --uid 1000 user

WORKDIR /home/user/app

COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r backend/requirements.txt

COPY --chown=user:user backend/ ./backend/
COPY --chown=user:user sdoh_screener_eu_gr_v2.json ./
COPY --chown=user:user sdoh_screener_response_schema_eu_gr_v2.json ./
COPY --chown=user:user healie_indicator_export_schema_v1.json ./
COPY --from=frontend-builder --chown=user:user /build/frontend/dist ./frontend/dist

USER user

EXPOSE 7860

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "7860"]
