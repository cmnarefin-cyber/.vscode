FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

ENV PYTHONUNBUFFERED=1
# Default app to run (github_app_auth or file_validator)
ENV APP=github_app_auth

EXPOSE 5000 5001

# Run chosen app
CMD ["sh", "-c", "python ${APP}.py"]
