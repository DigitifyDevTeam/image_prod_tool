FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential default-libmysqlclient-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
COPY django_app/requirements.txt /app/django_app/requirements.txt

RUN pip install --no-cache-dir -r /app/django_app/requirements.txt && \
    pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

WORKDIR /app/django_app

RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


