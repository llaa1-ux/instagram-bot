# Use Python 3.11
FROM python:3.11-slim

# Evita perguntas durante a instalação de pacotes
ENV DEBIAN_FRONTEND=noninteractive

# Cria diretório do app
WORKDIR /app

# Copia arquivos necessários
COPY bot_instagram.py .
COPY requirements.txt .
COPY cookies_instagram.txt .

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta que Render fornece via $PORT
EXPOSE 5000

# Comando para rodar o bot
CMD ["sh", "-c", "python bot_instagram.py"]
