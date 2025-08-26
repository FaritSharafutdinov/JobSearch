# Используем официальный образ Python
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./nltk_data /root/nltk_data

# Копируем исходники
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Указываем рабочую директорию для запуска
WORKDIR /app/backend

# Flask запускается на 0.0.0.0 внутри контейнера
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

EXPOSE 5000

# Запуск приложения
CMD ["python", "main.py"]
