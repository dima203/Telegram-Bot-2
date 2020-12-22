from data_base import DataBase
from question_base import QuestionBase
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from secret import TOKEN


bot = Bot(TOKEN)
storage = MemoryStorage()
dispatcher = Dispatcher(bot, storage=storage)
print('bot ready')

users_db = DataBase('users.db')
lessons_db = DataBase('lessons.db')
questions_base = QuestionBase('question_base.data')


class Lessons(StatesGroup):
    lesson = State()
    answer = State()
    message = State()


class Message(StatesGroup):
    admin = State()
    question = State()
    answer = State()
    message = State()


for i in users_db.get_ids('users'):
    print(users_db.get_record_by_id('users', i))
