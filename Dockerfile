FROM quay.io/astronomer/astro-runtime:12.1.1

# Install system dependencies for Tesseract
USER root
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Switch back to astro user
USER astro
