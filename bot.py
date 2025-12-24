import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode

# 1. Импортируем наши "Мозги" из соседнего файла
# (Если подчеркивает красным - не бойтесь, при запуске сработает)
from ai_spy import get_quotes, ai_analyze_raw

# 2. Настройки
logging.basicConfig(level=logging.INFO)
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Проверка токена
if not TOKEN:
    print("❌ ОШИБКА: Токен бота не найден в .env")
    exit()

# Инициализация бота
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- КЛАВИАТУРА ---
# Создаем красивую кнопку, чтобы клиенту не писать команды руками
kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🕵️ Запустить сканирование")]],
    resize_keyboard=True
)

# --- ЛОГИКА БОТА ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Встречаем нового клиента"""
    await message.answer(
        "👋 **Привет! Я — AI-Маркетолог.**\n\n"
        "Я умею шпионить за сайтами конкурентов и анализировать их контент с помощью нейросетей.\n"
        "Нажми кнопку внизу, чтобы я показал, на что способен.",
        reply_markup=kb,
        parse_mode=ParseMode.MARKDOWN
    )

@dp.message(F.text == "🕵️ Запустить сканирование")
async def start_scan(message: types.Message):
    """Главная функция: Связь с AI"""
    status_msg = await message.answer("⏳ **Подключаюсь к спутникам...**\n_(Это займет 10-15 секунд)_", parse_mode=ParseMode.MARKDOWN)

    # 1. Запускаем парсер (функция из ai_spy.py)
    quotes = get_quotes()
    if not quotes:
        await status_msg.edit_text("❌ Ошибка: Не удалось пробить защиту сайта.")
        return

    await status_msg.edit_text(f"✅ Найдено цитат: {len(quotes)}. \n🧠 **Отправляю в нейросеть Gemini...**")

    # 2. Запускаем анализ (функция из ai_spy.py)
    # Важно: это синхронная функция, в продакшене лучше делать асинхронно, но для теста сойдет
    report = ai_analyze_raw(quotes)
    
    if not report:
        await status_msg.edit_text("⚠️ ИИ не ответил. Попробуйте еще раз.")
        return

    # 3. Формируем красивый отчет прямо в чат
    await status_msg.delete() # Удаляем сообщение "Загрузка"
    
    for item in report:
        # Красивая карточка для каждого инсайта
        card = (
            f"👤 **Автор:** {item.get('author', 'Неизвестен')}\n"
            f"🇷🇺 **Перевод:** {item.get('russian', 'Нет перевода')}\n"
            f"✨ **Vibe:** {item.get('vibe', 'Норм')}\n"
            f"💡 **Совет:** {item.get('marketing_tip', 'Думай')}\n"
            f"{'-'*20}"
        )
        await message.answer(card, parse_mode=ParseMode.MARKDOWN)
    
    await message.answer("💰 **Отчет готов!** С вас 5000 рублей. (Шутка, пока бесплатно).")

# --- ЗАПУСК ---
async def main():
    print("🚀 Бот запущен! Идите в Telegram.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен.")