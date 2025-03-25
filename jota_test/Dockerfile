# Use uma imagem base leve
FROM python:3.12-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia os requirements primeiro para aproveitar o cache de camadas
COPY requirements.txt .

# Instala dependências Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copia todo o projeto
COPY . .

# Permissões para scripts
RUN chmod +x ./scripts/*.py

# Porta exposta
EXPOSE 8000

# Comando de inicialização
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]