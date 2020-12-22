from aiogram import executor
from config import dispatcher, users_db
import handlers
import requests
import secret


for user_id in users_db.get_ids('users'):
    keyboard = handlers.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('Уроки', 'Помощь')
    keyboard.row('Комната админов')

    response = requests.post(
        url='https://api.telegram.org/bot{0}/{1}'.format(secret.TOKEN, 'sendMessage'),
        data={'chat_id': user_id, 'text': 'Бот запущен', 'reply_markup': keyboard.as_json()}
    ).json()

executor.start_polling(dispatcher, skip_updates=True)
