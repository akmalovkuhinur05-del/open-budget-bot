 
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Bot tokeningizni shu yerga qo'ying
BOT_TOKEN = "8996873868:AAHtwvuXhsAkmW0n-B376wH25pgfQeCurp0"⁠

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# /start buyrug'i uchun javob
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Salom! Open Budget botiga xush kelibsiz!")

async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
