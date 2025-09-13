# Dockerfile para o bot Telegram + Instaloader

# 1. Imagem base com Python 3.11
FROM python:3.11-slim

# 2. Definir diretório de trabalho
WORKDIR /app

# 3. Copiar arquivos do projeto para dentro do container
COPY . /app

# 4. Atualizar pip e instalar dependências
RUN pip install --upgrade pip

# Instalar versões compatíveis dos pacotes
RUN pip install \
    python-telegram-bot==20.3 \
    instaloader==4.14 \
    httpx==0.28.1

# 5. Expor porta (para webhook do Telegram, se necessário)
EXPOSE 8443

# 6. Variáveis de ambiente (adicione seu TOKEN e WEBHOOK_URL aqui ou defina no Render)
# ENV TOKEN=<seu_token_aqui>
# ENV WEBHOOK_URL=<sua_webhook_url_aqui>

# 7. Comando para iniciar o bot
CMD ["python", "bot_instagram.py"]
