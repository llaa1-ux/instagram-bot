# Imagem base
FROM python:3.11-slim

# Diretório de trabalho
WORKDIR /app

# Copiar arquivos do projeto
COPY . /app

# Atualizar pip
RUN pip install --upgrade pip

# Instalar pacotes compatíveis
RUN pip install python-telegram-bot==20.3 instaloader==4.14

# Expor porta (para webhook)
EXPOSE 8443

# Variáveis de ambiente (defina no Render)
# ENV TOKEN=<seu_token_telegram>
# ENV WEBHOOK_URL=<sua_webhook_url>
# ENV IG_USERNAME=<usuario_instagram>
# ENV IG_PASSWORD=<senha_instagram>

# Comando para iniciar o bot
CMD ["python", "bot_instagram.py"]
