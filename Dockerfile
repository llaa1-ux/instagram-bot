FROM python:3.11-slim

WORKDIR /app

# Copia arquivos
COPY . /app

# Atualiza pip e instala dependências
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Executa o bot
CMD ["python", "bot_instagram.py"]
