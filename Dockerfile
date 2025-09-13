# Base image
FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Copia arquivos
COPY . .

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Define variável de ambiente para render
ENV PORT=8000

# Comando de execução
CMD ["python", "bot_instagram.py"]
