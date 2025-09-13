# Imagem base
FROM python:3.11-slim

# Diretório de trabalho
WORKDIR /app

# Copiar arquivos
COPY bot_instagram.py .
COPY requirements.txt .
COPY cookies_instagram.txt .

# Atualizar pip e instalar dependências
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expor a porta do Render
ARG PORT
ENV PORT=$PORT
EXPOSE $PORT

# Variáveis de ambiente do Telegram e Instagram
ENV TOKEN=""
ENV IG_USERNAME=""
ENV COOKIE_FILE="cookies_instagram.txt"
ENV WEBHOOK_URL=""

# Comando para rodar o bot
CMD ["python", "bot_instagram.py"]
