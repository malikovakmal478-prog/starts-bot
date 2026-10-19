import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    LabeledPrice,
    PreCheckoutQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 8080))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# /start bosilganda yuboriladigan xabar
@dp.message(CommandStart())
async def cmd_start(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⭐ 10 Stars xayriya qilish", callback_data="buy_10_stars")],
            [InlineKeyboardButton(text="⭐ 50 Stars xayriya qilish", callback_data="buy_50_stars")]
        ]
    )
    await message.answer(
        "Assalomu alaykum! Loyihani qo‘llab-quvvatlash uchun Telegram Stars yuborishingiz mumkin:",
        reply_markup=keyboard
    )

# Stars hisob-fakturasini (Invoice) chiqarish
@dp.callback_query(F.data.startswith("buy_"))
async def send_invoice(callback: CallbackQuery):
    amount = 10 if callback.data == "buy_10_stars" else 50
    
    # Telegram Stars uchun valyuta kodi doim "XTR" bo‘ladi
    prices = [LabeledPrice(label=f"{amount} ta Telegram Yulduzi", amount=amount)]
    
    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title="Loyiha uchun xayriya",
        description=f"Loyihani rivojlantirish uchun {amount} XTR yuborish",
        payload=f"stars_donation_{amount}",
        currency="XTR",
        prices=prices,
        provider_token="" # Telegram Stars uchun provider_token bo'sh qoldiriladi
    )
    await callback.answer()

# To'lovdan oldin tekshiruv (pre_checkout_query tasdiqlanishi shart)
@dp.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# Muvaffaqiyatli to'lov qayd etilganda
@dp.message(F.successful_payment)
async def process_successful_payment(message: Message):
    total_stars = message.successful_payment.total_amount
    await message.answer(
        f"To‘lov qabul qilindi! {total_stars} ⭐ uchun katta rahmat!"
    )

# Render bepul rejasida bot ishlab turishi uchun oddiy HTTP server
async def health_check(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

async def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN muhit o'zgaruvchisi topilmadi!")
    
    # HTTP server va Pollingni birgalikda ishga tushirish
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
