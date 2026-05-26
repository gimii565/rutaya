FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD python -c "from wsgi import app, db; db.create_all()" && gunicorn wsgi:app --bind 0.0.0.0:8000 --workers 2