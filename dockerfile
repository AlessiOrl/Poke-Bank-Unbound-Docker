FROM node:22-alpine AS frontend-builder

WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json ./

RUN npm ci

COPY frontend/ ./

RUN npm run build


FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Build the landing-page changes from source rather than relying on a stale
# checked-in static bundle.
COPY --from=frontend-builder /frontend/dist ./static/dist

VOLUME ["/app/DoNotDelete"]

EXPOSE 5000

CMD ["python", "-c", "from app import app; from waitress import serve; serve(app, host='0.0.0.0', port=5000)"]
