FROM python:3.11-slim

# 1. Устанавливаем сертификаты (чтобы https работал) и DNS-утилиты
RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates netbase && \
    rm -rf /var/lib/apt/lists/*

# 2. Создаем пользователя с ID 1000 (Главное требование Hugging Face)
RUN useradd -m -u 1000 user

# 3. Настраиваем папку
WORKDIR /app

# 4. Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Копируем весь код и СРАЗУ отдаем права нашему пользователю
COPY --chown=user . .

# 6. Переключаемся на пользователя (теперь мы не root)
USER user

# 7. Запускаем
CMD ["python", "bot.py"]