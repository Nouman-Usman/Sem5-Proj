FROM python:3.12.6-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    unixodbc \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN pip install torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1 --index-url https://download.pytorch.org/whl/cpu

COPY . .

RUN mkdir -p uploads/profile_images

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

EXPOSE 5000
CMD ["waitress-serve", "--host=127.0.0.1", "--port=5000", "app:app"]
