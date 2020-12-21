from data_base import DataBase
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from secret import TOKEN


bot = Bot(TOKEN)
storage = MemoryStorage()
dispatcher = Dispatcher(bot, storage=storage)
print('bot ready')

data_base = DataBase('users.db')


class Form(StatesGroup):
    message = State()


for i in data_base.get_ids():
    print(data_base.get_user_by_id(i))
