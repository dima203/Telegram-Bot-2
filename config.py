from data_base import DataBase
from question_base import QuestionBase
from help_question_base import HelpQuestionBase
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
help_questions_base = HelpQuestionBase('help_questions_base.data')


class Lessons(StatesGroup):
    group = State()
    lesson = State()
    answer = State()
    message = State()


class Message(StatesGroup):
    admin = State()
    question = State()
    user = State()
    answer = State()
    answer_user = State()
    message = State()
    message_user = State()


class Help(StatesGroup):
    main = State()
    questions = State()
    new_question = State()
    create_answer = State()
    create_question = State()
    create_question_text = State()


class Profile(StatesGroup):
    change_name = State()


for i in users_db.get_ids('users'):
    print(users_db.get_record_by_id('users', i))
