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
    chars = string.ascii_uppercase + string.digits
    part1 = ''.join(random.choices(chars, k=4))
    part2 = ''.join(random.choices(chars, k=4))
    return f"EVA-{part1}-{part2}"

def get_unique_code():
    used = load_json(USED_CODES_FILE, [])
    for _ in range(100):
        code = generate_code()
        if code not in used:
            return code
    return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚗 Открыть приложение", url=APP_URL)],
        [InlineKeyboardButton("📲 Установить на телефон", callback_data="install")],
        [InlineKeyboardButton("🔑 Получить код активации", callback_data="get_code")],
        [InlineKeyboardButton("❓ Как активировать", callback_data="howto")],
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
        f"🆓 *Бесплатно:* 10 записей\n"
        f"♾ *Полная версия:* {PRICE} ₽ — безлимит навсегда\n\n"
        "Выбери действие 👇"
    )
    await update.message.reply_text(
        text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "install":
        await install_menu(query)

    elif query.data == "install_ios":
        await install_ios(query)

    elif query.data == "install_android":
        await install_android(query)

    elif query.data == "howto":
        await howto(query)

    elif query.data == "get_code":
        await give_code(query)

    elif query.data == "back":
        keyboard = [
            [InlineKeyboardButton("🚗 Открыть приложение", url=APP_URL)],
            [InlineKeyboardButton("📲 Установить на телефон", callback_data="install")],
            [InlineKeyboardButton("🔑 Получить код активации", callback_data="get_code")],
            [InlineKeyboardButton("❓ Как активировать", callback_data="howto")],
        ]
        await query.edit_message_text(
            "Выбери действие 👇",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def install_menu(query):
    keyboard = [
        [InlineKeyboardButton("🍎 iPhone (Safari)", callback_data="install_ios")],
        [InlineKeyboardButton("🤖 Android (Chrome)", callback_data="install_android")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back")],
    ]
    await query.edit_message_text(
        "📲 *Установка приложения*\n\n"
        "Выбери свою систему:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def install_ios(query):
    keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="install")]]

    # Отправляем инструкцию текстом с эмодзи-шагами
    text = (
        "🍎 *Установка на iPhone*\n\n"
        f"*Шаг 1.* Открой ссылку в Safari:\n{APP_URL}\n\n"
        "*Шаг 2.* Нажми кнопку «Поделиться» внизу экрана\n"
        "_(квадрат со стрелкой ↑)_\n\n"
        "*Шаг 3.* Прокрути список вниз и выбери\n"
        "«*Добавить на экран «Домой»*»\n\n"
        "*Шаг 4.* Нажми «*Добавить*» в правом верхнем углу\n\n"
        "✅ Готово! Иконка появится на рабочем столе.\n"
        "Приложение работает как обычное — без браузерной строки и офлайн."
    )
    await query.edit_message_text(
        text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    # Отправляем схему-инструкцию отдельным сообщением
    chat_id = query.message.chat_id
    await query.message.get_bot().send_message(
        chat_id=chat_id,
        text=(
            "📋 *Где найти кнопку на iPhone:*\n\n"
            "```\n"
            "┌─────────────────────────┐\n"
            "│  Safari                 │\n"
            "│  inspiring-jalebi...    │\n"
            "├─────────────────────────┤\n"
            "│                         │\n"
            "│   [страница открыта]    │\n"
            "│                         │\n"
            "├─────────────────────────┤\n"
            "│  ◁  □  [⬆️]  □  □      │\n"
            "│        ^^^              │\n"
            "│   эта кнопка           │\n"
            "└─────────────────────────┘\n"
            "```\n"
            "Затем: *Добавить на экран «Домой»* → *Добавить*"
        ),
        parse_mode="Markdown"
    )


async def install_android(query):
    keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="install")]]

    text = (
        "🤖 *Установка на Android*\n\n"
        f"*Шаг 1.* Открой ссылку в Chrome:\n{APP_URL}\n\n"
        "*Шаг 2.* Нажми три точки ⋮ в правом верхнем углу\n\n"
        "*Шаг 3.* Выбери «*Добавить на главный экран*»\n"
        "_(или «Установить приложение»)_\n\n"
        "*Шаг 4.* Нажми «*Добавить*» в появившемся окне\n\n"
        "✅ Готово! Иконка появится на рабочем столе.\n"
        "Приложение работает офлайн после первого открытия."
    )
    await query.edit_message_text(
        text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    chat_id = query.message.chat_id
    await query.message.get_bot().send_message(
        chat_id=chat_id,
        text=(
            "📋 *Где найти кнопку на Android:*\n\n"
            "```\n"
            "┌─────────────────────────┐\n"
            "│  [←] inspiring-jale [⋮] │\n"
            "│                    ^^^  │\n"
            "│               эта кнопка│\n"
            "├─────────────────────────┤\n"
            "│                         │\n"
            "│   [страница открыта]    │\n"
            "│                         │\n"
            "└─────────────────────────┘\n"
            "```\n"
            "Затем: *Добавить на главный экран* → *Добавить*"
        ),
        parse_mode="Markdown"
    )


async def howto(query):
    keyboard = [
        [InlineKeyboardButton("🔑 Получить код", callback_data="get_code")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back")],
    ]
    await query.edit_message_text(
        "❓ *Как активировать полную версию*\n\n"
        "*1.* Оплати 129 ₽ — напиши нам для получения реквизитов\n\n"
        "*2.* Получи код активации здесь в боте\n\n"
        "*3.* Открой приложение → когда выйдет экран лимита,\n"
        "введи код в поле и нажми «Активировать»\n\n"
        "*4.* Готово — безлимит навсегда на этом устройстве\n\n"
        "⚠️ Один код = одно устройство\n"
        "Код сохраняется даже если очистить кэш браузера",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def give_code(query):
    user_id = str(query.from_user.id)
    user_codes = load_json(USER_CODES_FILE, {})

    if user_id in user_codes:
        code = user_codes[user_id]
        keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="back")]]
        await query.edit_message_text(
            f"✅ *Твой код активации:*\n\n`{code}`\n\n"
            "Введи его в приложении в поле активации.\n"
            "Код одноразовый — работает на одном устройстве.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    code = get_unique_code()
    if not code:
        await query.edit_message_text("😔 Ошибка. Напиши нам — выдадим код вручную.")
        return

    used = load_json(USED_CODES_FILE, [])
    used.append(code)
    save_json(USED_CODES_FILE, used)
    user_codes[user_id] = code
    save_json(USER_CODES_FILE, user_codes)

    keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="back")]]
    await query.edit_message_text(
        f"✅ *Твой код активации:*\n\n`{code}`\n\n"
        "Скопируй и введи в приложении в поле активации.\n"
        "Код одноразовый — работает только на одном устройстве.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚗 Открыть приложение", url=APP_URL)],
        [InlineKeyboardButton("📲 Установить на телефон", callback_data="install")],
        [InlineKeyboardButton("🔑 Получить код активации", callback_data="get_code")],
    ]
    await update.message.reply_text(
        "Нажми /start или выбери действие 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))
    logger.info("Бот запущен")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
