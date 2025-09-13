FROM python:3.11-slim

WORKDIR /app

COPY . /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "bot_instagram.py"]
