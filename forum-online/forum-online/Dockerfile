# Imagem base oficial Python slim para reduzir tamanho
FROM python:3.12-slim

# Boas praticas: nao gerar .pyc e enviar logs sem buffer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Diretorio de trabalho dentro do container
WORKDIR /app

# Instalar dependencias do sistema necessarias para psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro para aproveitar cache de layers do Docker
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o codigo da aplicacao
COPY app/ .

# Criar usuario nao-root por seguranca
RUN useradd -m -u 1000 forumuser && chown -R forumuser:forumuser /app
USER forumuser

# Porta exposta pelo Flask
EXPOSE 5000

# Healthcheck interno do container
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# Executar a aplicacao com Gunicorn em producao
CMD ["sh", "-c", "python -c 'from app import init_db; init_db()' && gunicorn --bind 0.0.0.0:5000 --workers 2 --access-logfile - --error-logfile - app:app"]
