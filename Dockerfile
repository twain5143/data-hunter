# ИСПОЛЬЗУЕМ ПОЛНУЮ ВЕРСИЮ DEBIAN (НЕ SLIM)
# Это включает полные библиотеки glibc и DNS, которые нужны aiohttp
FROM python:3.10

# 1. Создаем пользователя (требование Hugging Face)
RUN useradd -m -u 1000 user

# 2. Настраиваем окружение
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# 3. Рабочая папка внутри дома пользователя
WORKDIR $HOME/app

# 4. Копируем и ставим зависимости (от имени пользователя)
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# 5. Копируем код
COPY --chown=user . .

# 6. Запуск
CMD ["python", "bot.py"]