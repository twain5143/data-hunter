# Используем легкий, но свежий Python
FROM python:3.11-slim

# 1. Устанавливаем системные утилиты для работы сети (DNS + HTTPS)
# netbase - критически важен для разрешения адресов!
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    netbase \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 2. Создаем пользователя 1000 (требование Hugging Face)
RUN useradd -m -u 1000 user

# 3. Переключаемся на пользователя. Дальше все действия только от него.
USER user

# Настраиваем путь, чтобы Python видел библиотеки пользователя
ENV PATH="/home/user/.local/bin:$PATH"

# 4. Создаем рабочую папку прямо в доме пользователя
WORKDIR /home/user/app

# 5. Копируем файлы и СРАЗУ отдаем права пользователю
COPY --chown=user requirements.txt .
COPY --chown=user . .

# 6. Устанавливаем библиотеки в папку пользователя (флаг --user)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt

# 7. Запускаем
CMD ["python", "bot.py"]