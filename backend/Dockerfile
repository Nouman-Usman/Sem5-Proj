FROM python:3.12.6-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    build-essential \
    unixodbc \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*
RUN pip install langchain>=0.3.3 
RUN pip install langchain-community>=0.3.2 
RUN pip install langchain-core>=0.3.10 
RUN pip install langchain-groq>=0.2.0 
RUN pip install langchain-huggingface>=0.1.0 
RUN pip install langchain-pinecone>=0.2.0 
RUN pip install langgraph>=0.2.38 
RUN pip install pinecone-client>=5.0.1 
RUN pip install transformers>=4.44.2 
RUN pip install python-dotenv>=1.0.1 
RUN pip install numpy>=1.26.4 
RUN pip install pandas>=2.2.3 
RUN pip install nltk>=3.9.1 
RUN pip install scikit-learn>=1.5.2 
RUN pip install sentence-transformers>=3.1.0 
RUN pip install uvicorn>=0.25.0 
RUN pip install azure-storage-blob>=12.23.1 
RUN pip install python-multipart>=0.0.9 
RUN pip install pydantic>=2.9.2 
RUN pip install beautifulsoup4>=4.12.3 
RUN pip install flask>=2.3.2 
RUN pip install flask-cors>=3.1.1 
RUN pip install httpx>=0.23.0 
RUN pip install azure-data-tables>=12.1.0 
RUN pip install azure-identity>=1.10.0 
RUN pip install pyodbc>=4.0.32 
RUN pip install flask-sqlalchemy==3.1.1 
RUN pip install flask-bcrypt==1.0.1 
RUN pip install flask-jwt-extended==4.7.1 
RUN pip install waitress
RUN pip install torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1 --index-url https://download.pytorch.org/whl/cpu

COPY . .

RUN mkdir -p uploads/profile_images

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

EXPOSE 5000
CMD ["waitress-serve", "--host=127.0.0.1", "--port=5000", "app:app"]
