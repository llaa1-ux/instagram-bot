# Escolhendo imagem base do Python
FROM python:3.10-slim

# Diretório de trabalho
WORKDIR /app

# Copiar arquivos
COPY requirements.txt .
COPY bot_instagram.py .
COPY cookies_instagram.txt .

# Instalar dependências
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expor porta
EXPOSE 8443

# Comando para rodar o bot
CMD ["python", "bot_instagram.py"]
