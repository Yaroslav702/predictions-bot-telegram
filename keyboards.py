import json
from aiogram.types import (
    ReplyKeyboardRemove,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

set_time_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='9:00', callback_data=json.dumps({'time': 9}))],
        [InlineKeyboardButton(text='15:00', callback_data=json.dumps({'time': 15}))],
        [InlineKeyboardButton(text='20:00', callback_data=json.dumps({'time': 20}))]
    ],
)

commands_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Змінити час отримання сповіщень⏰')]
    ],
    resize_keyboard=True
)
