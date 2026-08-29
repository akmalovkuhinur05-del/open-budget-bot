import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiohttp import web

# PASTDAGI QATORGA BOTFATHER'DAN OLGAN YANGI TOKENINGIZNI QO'YING
API_TOKEN ='8996873868:AAENvvc_wP09BaKKsBu-sbtusMHwY-KRylo'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Salom! Open Budget botiga xush kelibsiz!")

# Render port talab qilgani uchun soxta veb-server
async def handle(request):
    return web.Response(text="Bot ishlayapti!")

async def main():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
