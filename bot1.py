import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ChatAction
from google import genai

# Получаем токены из окружения Render
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
ai_client = genai.Client(api_key=GEMINI_API_KEY)

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Здарова! Я твой ИИ-бот, запущенный в облаке 24/7. Спроси меня о чем угодно!")

@dp.message()
async def handle_message(message: types.Message):
    # Показываем статус "печатает..."
    try:
        await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
        
        # Запрос к Gemini (используем стабильную актуальную модель)
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=message.text,
        )
        await message.answer(response.text)
    except Exception as e:
        print(f"Error: {e}")
        await message.answer("Ой, что-то пошло не так при обращении к ИИ.")

# Простейший веб-сервер для Render, чтобы порт был занят и сервис не падал
async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Render передает порт через переменную окружения PORT
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    # Запускаем веб-сервер и бота одновременно
    await web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
