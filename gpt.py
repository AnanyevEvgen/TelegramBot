import base64

from openai import APIError
from telegram import Message, Update
from telegram.ext import ContextTypes

import keyboards
from credentials import config
from util import load_prompt, screensaver, send_text_buttons

class ChatGptService:
    MAX_HISTORY = 10

    def __init__(self):
        self.client = config.OPENAI_CLIENT
        self.conversations = {}

    def set_prompt(self,chat_id: int, name: str) -> None:
        if chat_id not in self.conversations:
            self.conversations[chat_id] = []
        prompt = load_prompt(name)
        self.conversations[chat_id] = [{"role": "system", "content": prompt}]

    async def check_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        history = self.conversations[update.effective_chat.id]
        if update.callback_query.data == 'quiz_more' and len(history) < 2:
            text = "Неможливо обрати останній пункт, тому що історія питань ще порожня, оберіть інший."
            await send_text_buttons(update, context, text, keyboards.inline_keyboard_quiz)
            return 'AWAIT_QUIZ'
        if update.callback_query.data != 'quiz_more':
            history = [history[0]]
        elif update.callback_query.data == 'quiz_more' and len(history) > 2:
            history = history[:5]
        self.conversations[update.effective_chat.id] = history

    async def add_message(self, chat_id: int, user_name: str, message_text: str, max_history = MAX_HISTORY):
        history = self.conversations[chat_id]
        if len(history) > 1 + max_history:
            history = [history[0]] + history[-max_history:]
        history.append({"role": user_name, "content": message_text})
        self.conversations[chat_id]=history
        return history

    @screensaver
    async def request_text(self, message: Message, data_text):
        try:
            result = await self.client.chat.completions.create(model="gpt-5-nano", messages=data_text)
            return result.choices[0].message.content.strip()
        except APIError:
            return "Помилка звернення до *ChatGPT*"

    @screensaver
    async def request_photo(self, message: Message, data_image: bytearray) -> str:
        prompt = load_prompt('photo')
        b64_image = base64.b64encode(data_image).decode()
        try:
            result = await self.client.responses.create(
                model="gpt-5-nano",
                input=[
                    {"role": "user",
                     "content": [
                         {"type": "input_text", "text": prompt},
                         {"type": "input_image",
                          "image_url": f"data:image/jpeg;base64,{b64_image}", },
                     ],
                     }
                ],
            )
            return result.output_text
        except APIError:
            return "Помилка звернення до *ChatGPT*"