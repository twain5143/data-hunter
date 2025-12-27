# ОТКАТ НА 3.10 (Решает проблему DNS)
FROM python:3.10-slim

# 1. Устанавливаем системные утилиты
RUN apt-get update && \
    apt-get install -y --no-install-recommends netbase ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# 2. Создаем пользователя
RUN useradd -m -u 1000 user

# 3. Настраиваем окружение
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# 4. Рабочая папка
WORKDIR $HOME/app

# 5. Копируем и устанавливаем (сначала requirements для кэша)
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# 6. Копируем код
COPY --chown=user . .

# 7. Запуск
CMD ["python", "bot.py"]