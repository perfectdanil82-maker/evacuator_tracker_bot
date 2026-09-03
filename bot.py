import os
import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ========== НАСТРОЙКИ ==========
BOT_TOKEN = "8883025545:AAE5VELjViC6hgJsS6VthwlWNt0LOW8QdjQ"
PRODAMUS_LINK = "https://ВСТАВЬ_ССЫЛКУ_PRODAMUS_ЗДЕСЬ"  # вставь свою ссылку
PRICE = 129

# Коды активации — те же что в приложении
CODES = [
    "EVA-TRUCK-0001","EVA-TRUCK-0002","EVA-TRUCK-0003","EVA-TRUCK-0004","EVA-TRUCK-0005",
    "EVA-TRUCK-0006","EVA-TRUCK-0007","EVA-TRUCK-0008","EVA-TRUCK-0009","EVA-TRUCK-0010",
    "EVA-TRUCK-0011","EVA-TRUCK-0012","EVA-TRUCK-0013","EVA-TRUCK-0014","EVA-TRUCK-0015",
    "EVA-TRUCK-0016","EVA-TRUCK-0017","EVA-TRUCK-0018","EVA-TRUCK-0019","EVA-TRUCK-0020",
    "EVA-TRUCK-0021","EVA-TRUCK-0022","EVA-TRUCK-0023","EVA-TRUCK-0024","EVA-TRUCK-0025",
    "EVA-TRUCK-0026","EVA-TRUCK-0027","EVA-TRUCK-0028","EVA-TRUCK-0029","EVA-TRUCK-0030",
    "EVA-TRUCK-0031","EVA-TRUCK-0032","EVA-TRUCK-0033","EVA-TRUCK-0034","EVA-TRUCK-0035",
    "EVA-TRUCK-0036","EVA-TRUCK-0037","EVA-TRUCK-0038","EVA-TRUCK-0039","EVA-TRUCK-0040",
    "EVA-TRUCK-0041","EVA-TRUCK-0042","EVA-TRUCK-0043","EVA-TRUCK-0044","EVA-TRUCK-0045",
    "EVA-TRUCK-0046","EVA-TRUCK-0047","EVA-TRUCK-0048","EVA-TRUCK-0049","EVA-TRUCK-0050",
]

CODES_FILE = "used_codes.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== РАБОТА С КОДАМИ ==========
def load_used():
    try:
        with open(CODES_FILE) as f:
            return json.load(f)
    except:
        return []

def save_used(used):
    with open(CODES_FILE, "w") as f:
        json.dump(used, f)

def get_next_code():
    used = load_used()
    for code in CODES:
        if code not in used:
            used.append(code)
            save_used(used)
            return code
    return None

# ========== ХЭНДЛЕРЫ ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚗 Купить активацию — 129 ₽", url=PRODAMUS_LINK)],
        [InlineKeyboardButton("✅ Я оплатил — получить код", callback_data="get_code")],
    ]
    text = (
        "🚗 *Эвакуатор Трекер*\n\n"
        "Приложение для учёта перевозок и расходов.\n\n"
        "📊 *Что умеет:*\n"
        "• Учёт перевозок по месяцам\n"
        "• Учёт расходов — топливо, обслуживание\n"
        "• Чистая прибыль = доходы минус расходы\n"
        "• Работает без интернета\n"
        "• Экспорт и импорт данных\n\n"
        "🆓 *Бесплатно:* 10 записей\n"
        f"♾ *Полная версия:* {PRICE} ₽ — безлимит навсегда\n\n"
        "Нажми кнопку ниже чтобы оплатить, затем вернись и нажми «Я оплатил»."
    )
    await update.message.reply_text(text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "get_code":
        # Проверяем не получал ли этот пользователь уже код
        user_id = str(query.from_user.id)
        used = load_used()

        # Ищем код этого пользователя
        user_codes_file = "user_codes.json"
        try:
            with open(user_codes_file) as f:
                user_codes = json.load(f)
        except:
            user_codes = {}

        if user_id in user_codes:
            code = user_codes[user_id]
            await query.edit_message_text(
                f"✅ *Твой код активации:*\n\n`{code}`\n\n"
                "Введи его в приложении в поле активации.",
                parse_mode="Markdown"
            )
            return

        code = get_next_code()
        if not code:
            await query.edit_message_text(
                "😔 Коды временно закончились. Напиши нам — выдадим вручную."
            )
            return

        # Сохраняем код за пользователем
        user_codes[user_id] = code
        with open(user_codes_file, "w") as f:
            json.dump(user_codes, f)

        await query.edit_message_text(
            f"✅ *Твой код активации:*\n\n`{code}`\n\n"
            "Скопируй и введи в приложении в поле активации.\n\n"
            "Код привязан к тебе — работает на одном устройстве.",
            parse_mode="Markdown"
        )

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Нажми /start чтобы начать."
    )

# ========== ЗАПУСК ==========
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))
    logger.info("Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    main()
