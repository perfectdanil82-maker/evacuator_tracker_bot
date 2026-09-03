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

# Реальные скриншоты инструкций (публичные изображения)
IOS_STEP1_URL = "https://help.apple.com/assets/65D9B4B52D93F26A8B0A76DC/65D9B4B72D93F26A8B0A76E7/ru_RU/add-to-home-screen.png"
ANDROID_STEP1_URL = "https://www.androidauthority.com/wp-content/uploads/2021/05/Chrome-add-to-home-screen-menu.jpg"

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

def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚗 Открыть приложение", url=APP_URL)],
        [InlineKeyboardButton("📲 Установить на телефон", callback_data="install")],
        [InlineKeyboardButton("🔑 Получить код активации", callback_data="get_code")],
        [InlineKeyboardButton("❓ Как активировать", callback_data="howto")],
    ])

def back_to_install():
    return InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="install")]])

def back_to_main():
    return InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="back")]])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Сохраняем id сообщений с картинками чтобы удалять при навигации
    context.user_data['photo_msg_ids'] = []

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
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_keyboard())


async def delete_photo_messages(context, chat_id):
    """Удаляет сохранённые сообщения с картинками"""
    for msg_id in context.user_data.get('photo_msg_ids', []):
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
        except:
            pass
    context.user_data['photo_msg_ids'] = []


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id

    if query.data == "back":
        await delete_photo_messages(context, chat_id)
        await query.edit_message_text(
            "Выбери действие 👇",
            reply_markup=main_keyboard()
        )

    elif query.data == "install":
        await delete_photo_messages(context, chat_id)
        await query.edit_message_text(
            "📲 *Установка приложения*\n\nВыбери свою систему:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🍎 iPhone (Safari)", callback_data="install_ios")],
                [InlineKeyboardButton("🤖 Android (Chrome)", callback_data="install_android")],
                [InlineKeyboardButton("◀️ Назад", callback_data="back")],
            ])
        )

    elif query.data == "install_ios":
        await delete_photo_messages(context, chat_id)
        await query.edit_message_text(
            "🍎 *Установка на iPhone*\n\n"
            f"*1.* Открой в Safari: {APP_URL}\n\n"
            "*2.* Нажми кнопку «Поделиться» внизу\n"
            "_(квадрат со стрелкой ↑)_\n\n"
            "*3.* Выбери «Добавить на экран «Домой»»\n\n"
            "*4.* Нажми «Добавить» справа вверху\n\n"
            "✅ Иконка появится на рабочем столе",
            parse_mode="Markdown",
            reply_markup=back_to_install()
        )
        # Отправляем гифку-инструкцию
        try:
            msg = await context.bot.send_animation(
                chat_id=chat_id,
                animation="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcDd4aHp6NHZtNm9rNm85NW50NnJtbzNheTNkcWo2NW96OHAzeHZlMSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7aCXqfnpHhS0xG5i/giphy.gif",
                caption="👆 Вот так выглядит кнопка «Поделиться» в Safari"
            )
            context.user_data.setdefault('photo_msg_ids', []).append(msg.message_id)
        except:
            # Если гифка не загрузилась — отправляем текстовое пояснение
            msg = await context.bot.send_message(
                chat_id=chat_id,
                text="👇 Кнопка «Поделиться» находится внизу экрана Safari — квадрат со стрелкой ↑"
            )
            context.user_data.setdefault('photo_msg_ids', []).append(msg.message_id)

    elif query.data == "install_android":
        await delete_photo_messages(context, chat_id)
        await query.edit_message_text(
            "🤖 *Установка на Android*\n\n"
            f"*1.* Открой в Chrome: {APP_URL}\n\n"
            "*2.* Нажми три точки ⋮ справа вверху\n\n"
            "*3.* Выбери «Добавить на главный экран»\n\n"
            "*4.* Нажми «Добавить» в окне\n\n"
            "✅ Иконка появится на рабочем столе\n"
            "Работает офлайн после первого открытия",
            parse_mode="Markdown",
            reply_markup=back_to_install()
        )
        try:
            msg = await context.bot.send_photo(
                chat_id=chat_id,
                photo="https://www.androidauthority.com/wp-content/uploads/2021/05/Chrome-add-to-home-screen-menu.jpg",
                caption="👆 Три точки ⋮ в правом верхнем углу Chrome → «Добавить на главный экран»"
            )
            context.user_data.setdefault('photo_msg_ids', []).append(msg.message_id)
        except:
            msg = await context.bot.send_message(
                chat_id=chat_id,
                text="👆 Три точки ⋮ в правом верхнем углу Chrome → «Добавить на главный экран»"
            )
            context.user_data.setdefault('photo_msg_ids', []).append(msg.message_id)

    elif query.data == "howto":
        await delete_photo_messages(context, chat_id)
        await query.edit_message_text(
            "❓ *Как активировать полную версию*\n\n"
            "*1.* Оплати 129 ₽ — напиши нам для реквизитов\n\n"
            "*2.* Нажми «Получить код» в этом боте\n\n"
            "*3.* Открой приложение → при выходе экрана лимита введи код\n\n"
            "*4.* Готово — безлимит навсегда\n\n"
            "⚠️ Один код = одно устройство",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔑 Получить код", callback_data="get_code")],
                [InlineKeyboardButton("◀️ Назад", callback_data="back")],
            ])
        )

    elif query.data == "get_code":
        await delete_photo_messages(context, chat_id)
        user_id = str(query.from_user.id)
        user_codes = load_json(USER_CODES_FILE, {})

        if user_id in user_codes:
            code = user_codes[user_id]
            await query.edit_message_text(
                f"✅ *Твой код активации:*\n\n`{code}`\n\n"
                "Введи в приложении в поле активации.\n"
                "Код одноразовый — одно устройство.",
                parse_mode="Markdown",
                reply_markup=back_to_main()
            )
            return

        code = get_unique_code()
        if not code:
            await query.edit_message_text("😔 Ошибка. Напиши нам — выдадим вручную.")
            return

        used = load_json(USED_CODES_FILE, [])
        used.append(code)
        save_json(USED_CODES_FILE, used)
        user_codes[user_id] = code
        save_json(USER_CODES_FILE, user_codes)

        await query.edit_message_text(
            f"✅ *Твой код активации:*\n\n`{code}`\n\n"
            "Скопируй и введи в приложении в поле активации.\n"
            "Код одноразовый — одно устройство.",
            parse_mode="Markdown",
            reply_markup=back_to_main()
        )


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Нажми /start или выбери действие 👇",
        reply_markup=main_keyboard()
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
