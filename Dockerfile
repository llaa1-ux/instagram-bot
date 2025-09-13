# Imagem base oficial do Python
FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    libz-dev libjpeg-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia arquivos do projeto
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expõe a porta usada pelo Render
EXPOSE 8443

# Comando de execução
CMD ["python", "bot_instagram.py"]
