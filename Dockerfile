FROM python:3.11-slim

WORKDIR /app

# Copia tudo
COPY . /app

# Instala as dependências do requirements
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Porta (Render define PORT também em env)
EXPOSE 8443

CMD ["python", "bot_instagram.py"]
