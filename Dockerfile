# Imagem base
FROM python:3.11-slim

# Configura diretório de trabalho
WORKDIR /app

# Copia arquivos do projeto
COPY . /app

# Atualiza pip e instala dependências
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expondo porta (Render vai usar essa porta)
EXPOSE 8443

# Comando para iniciar o bot
CMD ["python", "bot_instagram.py"]
