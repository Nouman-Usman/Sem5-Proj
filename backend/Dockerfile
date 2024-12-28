FROM python:3.12.6-slim as builder
RUN apt-get update && apt-get install -y pkg-config libssl-dev
WORKDIR /wheels

# Install build dependencies and Rust
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get install -y \
    build-essential \
    unixodbc \
    unixodbc-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && . $HOME/.cargo/env

# Add cargo to PATH
ENV PATH="/root/.cargo/bin:${PATH}"

# Upgrade pip and install build tools
RUN pip install --upgrade pip setuptools wheel

# Enhanced pip configurations
ENV PIP_DEFAULT_TIMEOUT=500 \
    PIP_TIMEOUT=500 \
    PIP_RETRIES=5 \
    PIP_NO_CACHE_DIR=0 \
    PIP_PREFER_BINARY=1 \
    MAKEFLAGS="-j$(nproc)"

# Create wheels directory
RUN mkdir -p /wheels

# Copy and build requirements in stages
COPY requirements.txt .

# Build wheels in smaller groups with explicit numpy version
RUN --mount=type=cache,target=/root/.cache/pip \
    pip wheel --no-deps numpy==1.26.4 -w /wheels/

# Build pandas and other data processing packages
RUN --mount=type=cache,target=/root/.cache/pip \
    pip wheel --no-deps \
    pandas==2.2.3 nltk==3.9.1 scikit-learn==1.5.2 \
    -w /wheels/

# Build basic requirements
RUN --mount=type=cache,target=/root/.cache/pip \
    pip wheel --no-deps \
    flask==2.3.2 flask-cors==5.0.0 flask-sqlalchemy==3.1.1 \
    flask-bcrypt==1.0.1 flask-jwt-extended==4.7.1 \
    waitress==2.1.2 pydantic==2.10.3 \
    -w /wheels/

# Build Azure packages
RUN --mount=type=cache,target=/root/.cache/pip \
    pip wheel --no-deps \
    azure-storage-blob==12.23.1 azure-data-tables==12.1.0 \
    azure-identity==1.10.0 python-multipart==0.0.9 \
    -w /wheels/

# Build transformer packages
RUN --mount=type=cache,target=/root/.cache/pip \
    pip wheel --no-deps \
    transformers==4.44.2 sentence-transformers==3.1.0 \
    tokenizers==0.13.3 \
    -w /wheels/

# Build LangChain packages
RUN --mount=type=cache,target=/root/.cache/pip \
    pip wheel --no-deps \
    langchain==0.3.3 langchain-community==0.3.2 \
    langchain-core==0.3.19 langchain-groq==0.2.0 \
    langchain-huggingface==0.1.0 langchain-pinecone==0.2.0 \
    langgraph==0.2.38 pinecone-client==5.0.1 \
    -w /wheels/

# Build PyTorch packages
RUN pip wheel --no-deps \
    torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1 \
    --index-url https://download.pytorch.org/whl/cpu \
    -w /wheels/

# Final stage
FROM python:3.12.6-slim

WORKDIR /app

# Copy wheels from builder
COPY --from=builder /wheels /wheels

# Install system dependencies
RUN apt-get update && apt-get install -y \
    unixodbc \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Install wheels in specific order
RUN pip install --no-index --find-links=/wheels/ /wheels/numpy* && \
    pip install --no-index --find-links=/wheels/ /wheels/pandas* && \
    pip install --no-index --find-links=/wheels/ /wheels/*.whl && \
    rm -rf /wheels

COPY . .

RUN mkdir -p uploads/profile_images

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

EXPOSE 5000
CMD ["waitress-serve", "--host=127.0.0.1", "--port=5000", "app:app"]
