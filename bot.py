import asyncio
import logging
import os
import sys
from aiohttp import web
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode

# Импорт твоей логики
from ai_spy import get_quotes, ai_analyze_raw

# Логирование в консоль (важно для облака)
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    print("❌ ОШИБКА: Токен бота не найден в .env")
    exit()

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- КЛАВИАТУРА ---
kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🕵️ Запустить сканирование")]],
    resize_keyboard=True
)

# --- ЛОГИКА БОТА (ТВОЯ) ---

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

    quotes = get_quotes()
    if not quotes:
        await status_msg.edit_text("❌ Ошибка: Не удалось пробить защиту сайта.")
        return

    await status_msg.edit_text(f"✅ Найдено цитат: {len(quotes)}. \n🧠 **Отправляю в нейросеть Gemini...**")

    report = ai_analyze_raw(quotes)
    
    if not report:
        await status_msg.edit_text("⚠️ ИИ не ответил. Попробуйте еще раз.")
        return

    await status_msg.delete() 
    
    for item in report:
        card = (
            f"👤 **Автор:** {item.get('author', 'Неизвестен')}\n"
            f"🇷🇺 **Перевод:** {item.get('russian', 'Нет перевода')}\n"
            f"✨ **Vibe:** {item.get('vibe', 'Норм')}\n"
            f"💡 **Совет:** {item.get('marketing_tip', 'Думай')}\n"
            f"{'-'*20}"
        )
        await message.answer(card, parse_mode=ParseMode.MARKDOWN)
    
    await message.answer("💰 **Отчет готов!** С вас 5000 рублей. (Шутка, пока бесплатно).")

# --- ВЕБ-СЕРВЕР ДЛЯ HUGGING FACE (ОБЯЗАТЕЛЬНО) ---
async def health_check(request):
    return web.Response(text="I am alive. Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    # Hugging Face слушает ТОЛЬКО порт 7860
    site = web.TCPSite(runner, '0.0.0.0', 7860)
    await site.start()

# --- ЗАПУСК ВСЕГО ВМЕСТЕ ---
async def main():
    print("🚀 Бот запускается в режиме Web + Polling...")
    # Запускаем и сервер (чтобы не умереть), и бота (чтобы отвечать)
    await asyncio.gather(
        start_web_server(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен.")