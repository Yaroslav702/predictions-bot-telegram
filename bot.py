import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

from sqlalchemy.orm import sessionmaker

from database import *
from keyboards import *

load_dotenv()

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot, storage=MemoryStorage())

engine = ENGINE
Session = sessionmaker(engine)
session = Session()

# loop = asyncio.get_event_loop()


async def set_default_commands(dp):
    await bot.set_my_commands(
        [
            types.BotCommand('start', "Запустити бота."),
            types.BotCommand('change_time', "Змінити час для сповіщень.")
        ]
        
    )


@dp.message_handler(state='*', commands='start')
async def process_start_command(message: types.Message, state: FSMContext):
    if_exists = session.query(User).filter_by(
        telegram_id=message.from_user.id).first()
    if not if_exists:
        new_user = User(
            telegram_id=message.from_user.id,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username,
            subscribed=True,
            notification_time=9
        )
        session.add(new_user)
        session.commit()

        await bot.send_message(message.from_user.id, 'Привіт!🥰\nЯ - бот з передбаченнями.\nОбери час, у який тобі зручно отримувати сповіщення.🎱', reply_markup=set_time_keyboard)
    else:
        await bot.send_message(message.from_user.id, 'Ви уже зареєстровані. 😊', reply_markup=commands_keyboard)

    await state.set_state('save_notifications_time')


@dp.callback_query_handler(lambda x: x.data, state='save_notifications_time')
async def set_notifications_time(callback_query: types.CallbackQuery, state: FSMContext):
    json_callback = json.loads(callback_query.data)
    if json_callback['time']:
        time = json_callback.get('time', 9)
        user = session.query(User).filter(
            User.telegram_id == int(callback_query.message.chat.id)).first()
        user.notification_time = time
        session.commit()

        await bot.send_message(callback_query.message.chat.id, text=f'Чудово!\nТепер ти отримуватимеш сповіщення о <b>{time}:00</b>.', parse_mode='html')
        await state.set_state('default')


async def on_startup(dispatcher):
    await set_default_commands(dispatcher)

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
