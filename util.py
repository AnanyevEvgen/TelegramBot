import asyncio
import itertools
from contextlib import suppress

from telegram import BotCommand, BotCommandScopeChat, MenuButtonCommands, MenuButtonDefault, Message, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

# Надсилає в чат текстове повідомлення
async def send_text(update: Update, context: ContextTypes.DEFAULT_TYPE,
                    text: str) -> Message:
    if text.count('_') % 2 != 0:
        message = f"Рядок '{text}' є невалідним з точки зору markdown. Скористайтеся методом send_html()"
        print(message)
        return await update.message.reply_text(message)

    text = text.encode('utf16', errors='surrogatepass').decode('utf16')
    return await context.bot.send_message(chat_id=update.effective_chat.id,
                                          text=text,
                                          parse_mode=ParseMode.MARKDOWN)


# Надсилає в чат html повідомлення
async def send_html(update: Update, context: ContextTypes.DEFAULT_TYPE,
                    text: str) -> Message:
    text = text.encode('utf16', errors='surrogatepass').decode('utf16')
    return await context.bot.send_message(chat_id=update.effective_chat.id,
                                          text=text, parse_mode=ParseMode.HTML)


# Надсилає в чат текстове повідомлення, та додає або видаляє кнопки
async def send_text_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE,
                            text: str, keyboard) -> Message:
    text = text.encode('utf16', errors='surrogatepass').decode('utf16')
    return await context.bot.send_message(
        update.effective_message.chat_id,
        text=text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN,
        message_thread_id=update.effective_message.message_thread_id)


# Надсилає в чат фото
async def send_image(update: Update, context: ContextTypes.DEFAULT_TYPE,
                     name: str) -> Message:
    with open(f'resources/images/{name}.jpg', 'rb') as image:
        return await context.bot.send_photo(chat_id=update.effective_chat.id,
                                            photo=image)


# Надсилає в чат фото, та додає або видаляє кнопки
async def send_image_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE,
                     name: str, keyboard) -> Message:
    with open(f'resources/images/{name}.jpg', 'rb') as image:
        return await context.bot.send_photo(chat_id=update.effective_chat.id,
                                            photo=image, reply_markup=keyboard)


# Відображає команду та головне меню
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE,
                         commands: dict):
    command_list = [BotCommand(key, value) for key, value in commands.items()]
    await context.bot.set_my_commands(command_list, scope=BotCommandScopeChat(
        chat_id=update.effective_chat.id))
    await context.bot.set_chat_menu_button(menu_button=MenuButtonCommands(),
                                           chat_id=update.effective_chat.id)


# Видаляємо команди для конкретного чату
async def hide_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.delete_my_commands(
        scope=BotCommandScopeChat(chat_id=update.effective_chat.id))
    await context.bot.set_chat_menu_button(menu_button=MenuButtonDefault(),
                                           chat_id=update.effective_chat.id)


# Завантажує повідомлення з папки /resources/messages/
def load_message(name):
    with open("resources/messages/" + name + ".txt", "r",
              encoding="utf8") as file:
        return file.read()


# Завантажує промпт з папки /resources/prompts/
def load_prompt(name):
    with open("resources/prompts/" + name + ".txt", "r",
              encoding="utf8") as file:
        return file.read()


# Повертає текст обраної кнопки InlineKeyboardButton
def inline_button_in_text(data, keyboard):
    key = keyboard.inline_keyboard
    for i in range(len(key)):
        if key[i][0].callback_data == data:
            return key[i][0].text


# Іметує очікування під час виконання запиту до довготривалої функції
def screensaver(func):
    async def wrapper(self, message: Message, request, *args):
        frames = ["." * i for i in range(1, 5)]
        async def output_loop():
            try:
                for frame in itertools.cycle(frames):
                    await asyncio.sleep(0.5)
                    await message.edit_text(frame)
            except asyncio.CancelledError:
                pass
        task = asyncio.create_task(output_loop())
        try:
            result = await func(self, message, request, *args)
            return result
        finally:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
    return wrapper