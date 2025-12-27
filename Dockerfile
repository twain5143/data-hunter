# Используем ПОЛНУЮ версию Python (Debian-based)
# В ней есть все сетевые утилиты и DNS "из коробки"
FROM python:3.11

# Создаем рабочую папку
WORKDIR /app

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

# ВАЖНО: Даем полные права на папку для любого пользователя
# (Hugging Face запускает бота под случайным ID, это спасет от ошибок доступа)
RUN chmod -R 777 /app

# Запускаем
CMD ["python", "bot.py"]