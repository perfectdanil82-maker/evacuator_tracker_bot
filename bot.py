import json
import random
import string
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8883025545:AAE5VELjViC6hgJsS6VthwlWNt0LOW8QdjQ"
APP_URL = "https://inspiring-jalebi-d204c3.netlify.app/"
PRICE = 129

USED_CODES_FILE = "used_codes.json"
USER_CODES_FILE = "user_codes.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f)


def generate_code():
    """Генерирует уникальный случайный код вида EVA-XXXX-XXXX"""
    chars = string.ascii_uppercase + string.digits
    part1 = ''.join(random.choices(chars, k=4))
    part2 = ''.join(random.choices(chars, k=4))
    return f"EVA-{part1}-{part2}"


def get_unique_code():
    """Генерирует код которого ещё нет в базе использованных"""
    used = load_json(USED_CODES_FILE, [])
    for _ in range(100):  # 100 попыток на случай коллизии
        code = generate_code()
        if code not in used:
            return code
    return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚗 Открыть приложение", url=APP_URL)],
        [InlineKeyboardButton("✅ Я оплатил — получить код", callback_data="get_code")],
    ]
    text = (
        "🚗 *Эвакуатор Трекер*\n\n"
        "Приложение для учёта перевозок и расходов владельца эвакуатора.\n\n"
        "📊 *Что умеет:*\n"
        "• Учёт перевозок по месяцам\n"
        "• Учёт расходов — топливо, обслуживание\n"
        "• Чистая прибыль = доходы минус расходы\n"
        "• Работает без интернета\n"
        "• Экспорт и импорт данных\n\n"
        f"🆓 *Бесплатно:* 10 записей\n"
        f"♾ *Полная версия:* {PRICE} ₽ — безлимит навсегда\n\n"
        "Для оплаты напишите нам — пришлём реквизиты и выдадим код активации."
    )
    await update.message.reply_text(
        text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "get_code":
        user_id = str(query.from_user.id)
        user_codes = load_json(USER_CODES_FILE, {})

        # Уже получал код — вернуть тот же
        if user_id in user_codes:
            code = user_codes[user_id]
            await query.edit_message_text(
                f"✅ *Твой код активации:*\n\n`{code}`\n\n"
                "Введи его в приложении в поле активации.\n"
                "Код одноразовый — работает на одном устройстве.",
                parse_mode="Markdown"
            )
            return

        # Генерируем новый уникальный код
        code = get_unique_code()
        if not code:
            await query.edit_message_text("😔 Ошибка генерации кода. Напиши нам — выдадим вручную.")
            return

        # Сохраняем код как использованный и привязываем к пользователю
        used = load_json(USED_CODES_FILE, [])
        used.append(code)
        save_json(USED_CODES_FILE, used)

        user_codes[user_id] = code
        save_json(USER_CODES_FILE, user_codes)

        await query.edit_message_text(
            f"✅ *Твой код активации:*\n\n`{code}`\n\n"
            "Скопируй и введи в приложении в поле активации.\n"
            "Код одноразовый — работает только на одном устройстве.",
            parse_mode="Markdown"
        )


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Нажми /start чтобы начать.")


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))
    logger.info("Бот запущен")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
