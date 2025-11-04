# Use Debian slim (versão estável)
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install dependencies and chrome
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget ca-certificates gnupg unzip xz-utils xvfb \
    fonts-liberation libasound2 libxss1 libatk1.0-0 libatk-bridge2.0-0 \
    libgconf-2-4 libnss3 libcups2 libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 libxrandr2 libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome (stable)
RUN wget -q -O /tmp/google-chrome-stable_current_amd64.deb \
    https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get update && apt-get install -y /tmp/google-chrome-stable_current_amd64.deb || apt-get -f install -y \
    && rm -f /tmp/google-chrome-stable_current_amd64.deb

# Install chromedriver matching chrome version
# Get chrome version and download matching chromedriver
RUN CHROME_VER=$(google-chrome --product-version | cut -d. -f1) && \
    echo "Chrome major version: ${CHROME_VER}" && \
    # get latest chromedriver for that major version
    LATEST_URL=$(wget -qO- "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VER}") && \
    wget -q -O /tmp/chromedriver_linux64.zip "https://chromedriver.storage.googleapis.com/${LATEST_URL}/chromedriver_linux64.zip" && \
    apt-get update && apt-get install -y unzip && \
    unzip /tmp/chromedriver_linux64.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver_linux64.zip && chmod +x /usr/local/bin/chromedriver

# Create app dir
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Expose port — Render uses $PORT env var so we bind to it in the start command
ENV PORT=10000

# Use uvicorn to serve the FastAPI app — bind to 0.0.0.0:$PORT
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT} --workers 1"]
