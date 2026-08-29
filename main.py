import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

API_TOKEN = 8996873868:AAHtwvuXhsAkmW0n-B376wH25pgfQeCurp0

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Salom! Open Budget botiga xush kelibsiz!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

