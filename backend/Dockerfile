FROM python:3.12-slim

WORKDIR /app

# Instalamos dependencias de sistema necesarias
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# 1. Instalar PyTorch versión CPU explícitamente para ahorrar gigas de peso
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 2. Instalar el resto de requerimientos
RUN pip install --no-cache-dir -r requirements.txt

# 3. Descargar NLTK Stopwords dentro de la imagen
RUN python -m nltk.downloader stopwords

# 4. Descargar el modelo de IA localmente en la imagen
# Configuramos la variable de entorno para que SentenceTransformers use caché local
ENV SENTENCE_TRANSFORMERS_HOME=/app/model_cache
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')"

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]