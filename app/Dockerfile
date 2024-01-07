FROM python:3.11-slim

COPY ../requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /tmp/requirements.txt

COPY ./app /app

COPY .env /app/.env

WORKDIR /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
