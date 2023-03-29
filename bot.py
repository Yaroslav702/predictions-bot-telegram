import asyncio
import os
import random
import schedule
from threading import Thread
from dotenv import load_dotenv
from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.utils.executor import start_webhook

from sqlalchemy.orm import sessionmaker

from database import *
from keyboards import *

load_dotenv()
TOKEN = os.getenv('TOKEN')

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

engine = ENGINE
Session = sessionmaker(engine)
session = Session()

loop = asyncio.get_event_loop()

async def set_default_commands(dp):
    await bot.set_my_commands(
        [
            types.BotCommand('start', "Запустити бота."),
            types.BotCommand('change_time', "Змінити час для сповіщень.")
        ]
        
    )


@dp.message_handler(state='*', commands='start')
async def process_start_command(message: types.Message, state: FSMContext):
    user = session.query(User).filter_by(
        telegram_id=message.from_user.id).first()
    if not user:
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
        user_notifications_time = user.notification_time
        await bot.send_message(message.from_user.id, f'Ви уже зареєстровані. 😊\nЧас отримання передбачень - <b>{user_notifications_time}:00</b>', parse_mode='html')

    await state.set_state('save_notifications_time')

@dp.message_handler(state='*', commands='change_time')
async def change_notifications_time(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, 'Обери час, у який тобі зручно отримувати сповіщення.🎱', reply_markup=set_time_keyboard)
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


def get_predictions():
    predictions = session.query(Prediction).all()
    predictions_texts = [i.text for i in predictions]
    return predictions_texts


def get_user_ids(time: int) -> list:
    users = session.query(User).filter_by(notification_time=time).all()
    users_ids = [i.telegram_id for i in users]
    return users_ids


async def send_prediction(users_ids: list, predictions_list: list) -> None:
    for user in users_ids:
        prediction = random.choice(predictions_list)
        await bot.send_message(user, f'Привіт!\n\nТвоє передбачення на сьогодні:\n{prediction}')


async def send_prediction_15():
    users_ids = get_user_ids(15)
    predictions_texts = get_predictions()

    await send_prediction(users_ids, predictions_texts)


async def send_prediction_9():
    users_ids = get_user_ids(9)
    predictions_texts = get_predictions()

    await send_prediction(users_ids, predictions_texts)

async def send_prediction_20():
    users_ids = get_user_ids(20)
    predictions_texts = get_predictions()

    await send_prediction(users_ids, predictions_texts)



def predictions_15():
    send_fut = asyncio.run_coroutine_threadsafe(send_prediction_15(), loop)
    send_fut.result()

def predictions_20():
    send_fut = asyncio.run_coroutine_threadsafe(send_prediction_20(), loop)
    send_fut.result()

def predictions_9():
    send_fut = asyncio.run_coroutine_threadsafe(send_prediction_9(), loop)
    send_fut.result()


def run_schedule():
    schedule.every().day.at("15:00").do(predictions_15)
    schedule.every().day.at("20:00").do(predictions_20)
    schedule.every().day.at("09:00").do(predictions_9)
    while True:
        schedule.run_pending()

if __name__ == '__main__':
    executor_predictions = Thread(target=run_schedule, args=())
    executor_predictions.start()

    executor.start_polling(dp, on_startup=on_startup)