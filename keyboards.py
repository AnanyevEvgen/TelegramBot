from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

reply_keyboard_cancel = ReplyKeyboardMarkup([["Завершити ❌"]], resize_keyboard=True, is_persistent=True)

reply_keyboard_random = ReplyKeyboardMarkup([["Хочу ще факт 🧠", "Завершити ❌"]],
                                      resize_keyboard=True, is_persistent=True)

reply_keyboard_talk = ReplyKeyboardMarkup([["Інша особистість 👤", "Завершити ❌"]],
                                      resize_keyboard=True, is_persistent=True)

reply_keyboard_work = ReplyKeyboardMarkup([["Почати спочатку ⏪", "Завершити ❌"]],
                                      resize_keyboard=True, is_persistent=True)

inline_keyboard_talk = InlineKeyboardMarkup([
    [InlineKeyboardButton(callback_data='talk_cobain', text="Курт Кобейн")],
    [InlineKeyboardButton(callback_data='talk_queen', text="Єлизавета II")],
    [InlineKeyboardButton(callback_data='talk_tolkien', text="Джон Толкін")],
    [InlineKeyboardButton(callback_data='talk_nietzsche', text="Фрідріх Ніцше")],
    [InlineKeyboardButton(callback_data='talk_hawking', text="Стівен Гокінг")]
])

inline_keyboard_quiz = InlineKeyboardMarkup([
    [InlineKeyboardButton(callback_data='quiz_prog', text="Програмування мовою Python")],
    [InlineKeyboardButton(callback_data='quiz_math', text="Математика")],
    [InlineKeyboardButton(callback_data='quiz_biology', text="Біологія")],
    [InlineKeyboardButton(callback_data='quiz_more', text="На ту ж тему, що й попереднє")]
])

inline_keyboard_work_category = InlineKeyboardMarkup([
    [InlineKeyboardButton(callback_data='category_book', text="Книга 📕")],
    [InlineKeyboardButton(callback_data='category_music', text="Музика 🎵")],
    [InlineKeyboardButton(callback_data='category_movie', text="Фільм 🎦")]
])

inline_keyboard_work = InlineKeyboardMarkup([
    [InlineKeyboardButton(callback_data='work_next', text="Не подобається ⏭️")]
])