import warnings

from telegram import ReplyKeyboardRemove, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, \
    CommandHandler, ConversationHandler, filters, MessageHandler
from telegram.warnings import PTBUserWarning

from credentials import config
from gpt import ChatGptService
from keyboards import *
from util import inline_button_in_text, load_message, send_image, send_text, \
    send_image_buttons, send_text_buttons, show_main_menu

# Вимкнення попередження PTBUserWarning
warnings.filterwarnings('ignore', category=PTBUserWarning)

# Константи станів ConversationHandler
S_RANDOM, S_GPT, S_TALK, S_QUIZ, S_PHOTO, S_WOKR,  = range(1,7)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = load_message('main')
    await send_image(update, context, 'main')
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        'start': 'Головне меню',
        'random': 'Дізнатися випадковий цікавий факт 🧠',
        'gpt': 'Задати питання ChatGPT 🤖',
        'talk': 'Поговорити з відомою особистістю 👤',
        'quiz': 'Взяти участь у квізі ❓',
        'photo': 'ChatGPT проаналізує зображення 🖼️',
        'work': 'ChatGPT порекомендує твір 📕🎵🎦'
    })

async def random_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_image(update, context, 'random')
    text = load_message('random')
    await send_text_buttons(update, context, text, reply_keyboard_random)
    chat_gpt.set_prompt(update.effective_chat.id, 'random')
    await random_next(update, context)
    return S_RANDOM

async def random_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    last_message = await send_text(update, context, '...')
    request_ai = await chat_gpt.add_message(update.effective_chat.id, "user", "Цікавий факт")
    ai_response = await chat_gpt.request_text(last_message, request_ai)
    await chat_gpt.add_message(update.effective_chat.id, "assistant", ai_response)
    await last_message.edit_text(ai_response)
    return S_RANDOM

async def gpt_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_image(update, context, 'gpt')
    text = load_message('gpt')
    await send_text_buttons(update, context, text, reply_keyboard_cancel)
    chat_gpt.set_prompt(update.effective_chat.id, 'gpt')
    return S_GPT

async def gpt_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    request_ai = await chat_gpt.add_message(update.effective_chat.id, "user", message_text)
    last_message = await send_text(update, context, '...')
    ai_response = await chat_gpt.request_text(last_message, request_ai)
    await chat_gpt.add_message(update.effective_chat.id, "user", ai_response)
    await last_message.edit_text(ai_response)
    text = load_message('gpt')
    await send_text(update, context, text)
    return S_GPT

async def talk_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_image_buttons(update, context, 'talk', reply_keyboard_cancel)
    text = load_message('talk')
    await send_text_buttons(update, context, text, inline_keyboard_talk)
    return S_TALK

async def talk_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    callback_data = update.callback_query.data
    button_text = inline_button_in_text(callback_data, inline_keyboard_talk)
    text = f"Ви обрали: {button_text}, можете розпочинати розмову"
    await send_text_buttons(update, context, text, reply_keyboard_talk)
    chat_gpt.set_prompt(update.effective_chat.id, callback_data)
    return S_TALK

async def talk_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    request_ai = await chat_gpt.add_message(update.effective_chat.id, "user", message_text)
    last_message = await send_text(update, context, "...")
    ai_response = await chat_gpt.request_text(last_message, request_ai)
    await chat_gpt.add_message(update.effective_chat.id, "assistant", ai_response)
    await last_message.edit_text(ai_response)
    return S_TALK

async def quiz_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_image_buttons(update, context, 'quiz', reply_keyboard_cancel)
    text = load_message('quiz')
    await send_text_buttons(update, context, text, inline_keyboard_quiz)
    chat_gpt.set_prompt(update.effective_chat.id, 'quiz')
    user_data = context.user_data
    user_data.setdefault('quiz_score', 0)
    user_data.setdefault('quiz_total', 0)
    user_data['quiz_score'] = 0
    user_data['quiz_total'] = 0
    return S_QUIZ

async def quiz_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    callback_data = update.callback_query.data
    transition = await chat_gpt.check_history(update, context)
    if type(transition) == str:
        return S_QUIZ
    request_ai = await chat_gpt.add_message(update.effective_chat.id, "user", callback_data)
    last_message = await send_text(update, context, "...")
    ai_response = await chat_gpt.request_text(last_message, request_ai)
    await chat_gpt.add_message(update.effective_chat.id, "assistant", ai_response)
    await last_message.edit_text(ai_response)
    return S_QUIZ

async def quiz_verification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    request_ai = await chat_gpt.add_message(update.effective_chat.id, "user",
                                         "Перевір відповідь: " + message_text)
    last_message = await send_text(update, context, "...")
    ai_response = await chat_gpt.request_text(last_message, request_ai)
    await chat_gpt.add_message(update.effective_chat.id, "assistant", ai_response)
    user_data = context.user_data
    user_data['quiz_total'] = user_data.get('quiz_total', 0) + 1
    if ai_response == "Правильно!":
        user_data['quiz_score'] = user_data.get('quiz_score', 0) + 1
    score = user_data['quiz_score']
    total = user_data['quiz_total']
    ai_response += f"\nВсього вірно: {score} з: {total}"
    await last_message.edit_text(ai_response, reply_markup=inline_keyboard_quiz)
    return S_QUIZ

async def photo_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_image(update, context, 'photo')
    text = load_message('photo')
    await send_text_buttons(update, context, text, reply_keyboard_cancel)
    return S_PHOTO

async def photo_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = update.message.photo[-1]
    file = await context.bot.get_file(photo_file.file_id)
    image_bytes = await file.download_as_bytearray()
    last_message =await send_text(update, context, '...')
    ai_response = await chat_gpt.request_photo(last_message, image_bytes)
    await last_message.edit_text(ai_response)
    text = load_message('photo')
    await send_text_buttons(update, context, text, reply_keyboard_cancel)
    return S_PHOTO

async def work_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_image_buttons(update, context, 'work', reply_keyboard_cancel)
    text = load_message('work')
    await send_text_buttons(update, context, text, inline_keyboard_work_category)
    chat_gpt.set_prompt(update.effective_chat.id, 'work')
    return S_WOKR

async def work_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    callback_data = update.callback_query.data
    category = inline_button_in_text(callback_data, inline_keyboard_work_category)
    text = f"Ви обрали категорію: {category}, введіть жанр\n"
    await context.bot.edit_message_text(text, chat_id=update.effective_chat.id,
                                        message_id=update.effective_message.message_id)
    text = load_message(callback_data)
    await send_text_buttons(update, context, text, reply_keyboard_work)
    category = category.split()[0]
    user_data = context.user_data
    user_data.setdefault('category')
    user_data['category'] = category
    return S_WOKR

async def work_recommendation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    genre = update.message.text
    user_data = context.user_data
    category = user_data['category']
    request = f"Поверни твір. Категорія: {category}, жанр: {genre}"
    request_ai = await chat_gpt.add_message(update.effective_chat.id, "user", request)
    last_message = await send_text(update, context, "...")
    ai_response = await chat_gpt.request_text(last_message, request_ai)
    await chat_gpt.add_message(update.effective_chat.id, "assistant", ai_response)
    await last_message.edit_text(ai_response, reply_markup=inline_keyboard_work)
    return S_WOKR

async def work_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    request_ai = await chat_gpt.add_message(update.effective_chat.id, "user",
                                            "Не подобається")
    last_message = await send_text(update, context, "...")
    ai_response = await chat_gpt.request_text(last_message, request_ai)
    await chat_gpt.add_message(update.effective_chat.id, "assistant", ai_response)
    await last_message.edit_text(ai_response, reply_markup=inline_keyboard_work)
    return S_WOKR

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_text_buttons(update, context, 'Завдання завершено.', ReplyKeyboardRemove())
    await start(update, context)
    return ConversationHandler.END

app = (ApplicationBuilder()
       .token(config.BOT_TOKEN)
       .concurrent_updates(True)
       .build())

chat_gpt = ChatGptService()

# Відстеження стану
conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler('start', start),
        CommandHandler('random', random_start),
        CommandHandler('gpt', gpt_start),
        CommandHandler('talk', talk_start),
        CommandHandler('quiz', quiz_start),
        CommandHandler('photo', photo_start),
        CommandHandler('work', work_start)
    ],
    states={
        S_RANDOM: [MessageHandler((filters.Text(["Хочу ще факт 🧠"]) & ~filters.COMMAND), random_next)],
        S_GPT: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Text(["Завершити ❌"]), gpt_next)],
        S_TALK: [CallbackQueryHandler(talk_next, pattern="^talk_.*"),
        MessageHandler(filters.Text(["Інша особистість 👤"]), talk_start),
        MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Text(["Завершити ❌"]), talk_dialog)],
        S_QUIZ: [CallbackQueryHandler(quiz_next, pattern="^quiz_.*"),
        MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Text(["Завершити ❌"]), quiz_verification)],
        S_PHOTO: [MessageHandler(filters.PHOTO & ~filters.COMMAND, photo_next)],
        S_WOKR: [CallbackQueryHandler(work_category, pattern="^category_.*"),
        MessageHandler(filters.Text(["Почати спочатку ⏪"]), work_start),
        MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Text(["Завершити ❌"]), work_recommendation),
        CallbackQueryHandler(work_next, pattern="^work_next")],
    },
    fallbacks=[MessageHandler(filters.Text(["Завершити ❌"]), cancel)],
    allow_reentry=True,
)
app.add_handler(conv_handler)

print("Bot started...")
app.run_polling()