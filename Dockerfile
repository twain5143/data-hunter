FROM python:3.11-slim

# Ставим netbase (для DNS) и сертификаты
RUN apt-get update && \
    apt-get install -y --no-install-recommends netbase ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Создаем пользователя user (ID 1000) с домашней папкой
RUN useradd -m -u 1000 user

# Переключаемся на пользователя
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Рабочая папка внутри дома пользователя
WORKDIR $HOME/app

# Копируем и ставим зависимости (с правами пользователя)
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Копируем код
COPY --chown=user . .

# Запуск
CMD ["python", "bot.py"]