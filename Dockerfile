FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Porta do webhook
ENV PORT=10000
EXPOSE 10000

CMD ["python", "bot_instagram.py"]
