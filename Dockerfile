FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies (requirements.txt lives in .vscode/)
COPY .vscode/requirements.txt ./
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy app sources from the .vscode subfolder
COPY .vscode /app

# Create a non-root user and switch to it
RUN useradd -m appuser || true
USER appuser

# Default app module (override with APP env var)
ENV APP=github_app_auth

# Expose primary HTTP port
EXPOSE 5000

# Use gunicorn for production serving; allow APP override
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:5000 ${APP}:app"]
