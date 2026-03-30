import asyncio
import logging
from collections import Counter
from datetime import datetime
import gspread
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)

BOT_TOKEN = "8556774074:AAGtLr42OIBF0i07HG0sMmfqKO-ICaGM28A"
GOOGLE_SHEET_KEY = "1dpPyq8kB4YI0R40O3oRmpWSWrWY-_ZiQphENaAYaz_k"

router = Router()
search_users = {}
flota_users = {}

def get_client():
    return gspread.service_account(filename="service_account.json")

# ================= DRIVER =================
def find_driver(plate):
    sh = get_client().open_by_key(GOOGLE_SHEET_KEY)
    plate = plate.strip().lower()

    for sheet in ["CITI", "Toyoty", "skutery"]:
        ws = sh.worksheet(sheet)
        rows = ws.get_all_values()

        for row in rows[1:]:
            if len(row) > 5:
                if row[5].lower() == "zakończony":
                    continue

                if row[2].strip().lower() == plate:
                    return "👤 " + row[0] + "\n📞 " + row[1]

    return None

# ================= FLOTA =================
def find_flota(plate):
    sh = get_client().open_by_key(GOOGLE_SHEET_KEY)
    plate = plate.strip().lower()

    ws = sh.worksheet("flota")
    rows = ws.get_all_values()

    for row in rows[1:]:
        if row[0].strip().lower() == plate:

            vin = row[1]
            company = row[2]
            model = row[3]
            marka = row[4]

            name = krs = nip = regon = addr = ""

            for ws_name in ["spółki", "Spółki", "spolki", "SPOLKI"]:
                try:
                    ws2 = sh.worksheet(ws_name)
                    rows2 = ws2.get_all_values()

                    for r in rows2[1:]:
                        if len(r) > 1 and r[1].strip().lower() == company.strip().lower():
                            name = r[0]
                            krs = r[2] if len(r) > 2 else ""
                            nip = r[3] if len(r) > 3 else ""
                            regon = r[4] if len(r) > 4 else ""
                            addr = r[5] if len(r) > 5 else ""
                            break
                    break
                except:
                    continue

            line = "──────────────"

            text = "🚗 " + plate.upper() + "\n\n"
            text += line + "\n📌 POJAZD\n" + line + "\n"
            text += "VIN: " + vin + "\n"
            text += "Model: " + model + "\n"
            text += "Marka: " + marka + "\n"

            if name:
                text += "\n" + line + "\n🏢 SPÓŁKA\n" + line + "\n"
                text += name + "\n\n"
                if krs:
                    text += "KRS: " + krs + "\n"
                if nip:
                    text += "NIP: " + nip + "\n"
                if regon:
                    text += "REGON: " + regon + "\n"

            if addr:
                text += "\n📍 " + addr

            return text

    return None

# ================= REPORT =================
def normalize_status(v):
    v = v.strip().lower()
    if v == "zakończony":
        return None
    return v.capitalize()

def build_report():
    sh = get_client().open_by_key(GOOGLE_SHEET_KEY)

    sheets = {
        "CITI": "🚗 Samochody kurierskie",
        "Toyoty": "🚖 Samochody taxi",
        "rowery": "🚲 Rowery",
        "skutery": "🛵 Skutery",
    }

    result = "📊 Raport — " + datetime.now().strftime("%d.%m.%Y") + "\n\n"
    total = Counter()

    for s, title in sheets.items():
        ws = sh.worksheet(s)
        rows = ws.get_all_values()

        counts = Counter()

        for r in rows[1:]:
            if len(r) > 5:
                st = normalize_status(r[5])
                if st:
                    counts[st] += 1

        result += title + "\n"
        for k, v in counts.items():
            result += "• " + k + ": " + str(v) + "\n"
            total[k] += v
        result += "\n"

    result += "📌 RAZEM\n"
    for k, v in total.items():
        result += "• " + k + ": " + str(v) + "\n"

    return result

# ================= ACCESS =================
def allowed(user_id):
    ws = get_client().open_by_key(GOOGLE_SHEET_KEY).worksheet("users")
    for r in ws.get_all_values()[1:]:
        if r[0].isdigit() and int(r[0]) == user_id and r[2] == "TRUE":
            return True
    return False

# ================= UI =================

def keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📊 Raport"),
                KeyboardButton(text="🚗 Flota"),
            ],
            [
                KeyboardButton(text="🔧 Serwis samochodów"),
                KeyboardButton(text="👤 Kto jeździ"),
            ],
        ],
        resize_keyboard=True,
    )


# ================= HANDLERS =================
@router.message(CommandStart())
async def start(m: Message):
    if not allowed(m.from_user.id):
        return await m.answer("⛔ Brak dostępu")
    await m.answer("Cześć!", reply_markup=keyboard())

@router.message(lambda m: m.text == "📊 Raport")
async def report(m: Message):
    await m.answer(build_report())

@router.message(lambda m: m.text == "👤 Kto jeździ")
async def driver(m: Message):
    search_users[m.from_user.id] = True
    await m.answer("Podaj numer rejestracyjny:")

@router.message(lambda m: m.text == "🚗 Flota")
async def flota(m: Message):
    flota_users[m.from_user.id] = True
    await m.answer("Podaj numer rejestracyjny:")

@router.message(lambda m: m.text == "🔧 Serwis samochodów")
async def serwis(m: Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➡️ Otwórz", url="https://t.me/serwiswwa_bot")]
        ]
    )
    await m.answer("Serwis:", reply_markup=kb)

@router.message()
async def handle(m: Message):
    uid = m.from_user.id

    if uid in flota_users:
        res = find_flota(m.text)
        await m.answer(res if res else "❌ Nie znaleziono")
        del flota_users[uid]
        return

    if uid in search_users:
        res = find_driver(m.text)
        await m.answer(res if res else "❌ Nie znaleziono")
        del search_users[uid]
        return

    await m.answer("Wybierz opcję 👇", reply_markup=keyboard())

async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
