# Gunakan Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Salin file ke dalam container
COPY . .

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Jalankan migrasi dan collect static (opsional kalau ada)
RUN python manage.py migrate
RUN python manage.py collectstatic --noinput

# Jalankan Django pakai Gunicorn
CMD ["gunicorn", "cekresi_project.wsgi:application", "--bind", "0.0.0.0:8000"]
