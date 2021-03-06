from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from config import users_db, lessons_db, questions_base, help_questions_base
from callback_datas import answers_callback, question_callback, change_name_callback

main_user = ReplyKeyboardMarkup(resize_keyboard=True)
main_user.row('Уроки', 'Помощь')
main_user.row('Профиль')

main_admin = ReplyKeyboardMarkup(resize_keyboard=True)
main_admin.row('Уроки', 'Помощь')
main_admin.row('Профиль')
main_admin.row('Комната админов')

lessons_groups = ReplyKeyboardMarkup(resize_keyboard=True)
lessons_groups.row('Основы')
lessons_groups.row('ООП')
lessons_groups.row('Отмена')


def lessons_main(group: str) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for lesson_id in lessons_db.get_ids(group):
        res = lessons_db.get_record_by_id(group, lesson_id)
        keyboard.row(f'{res["id"]:3}: {res["theme"]}')
    keyboard.row('Отмена')
    return keyboard


lessons_lesson = ReplyKeyboardMarkup(resize_keyboard=True)
lessons_lesson.row('Тест')
lessons_lesson.row('Вопросы к преподавателю')
lessons_lesson.row('Отмена')

adminsroom_main = ReplyKeyboardMarkup(resize_keyboard=True)
adminsroom_main.row('Сообщения', 'Пользователь')
adminsroom_main.row('Все пользователи')
adminsroom_main.row('Отмена')


def adminsroom_message_chose() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for question_id in questions_base.get_ids():
        question = questions_base.get_message(question_id)
        button = f'{question_id}: {lessons_db.get_record_by_id(question["lesson_group"], question["lesson_id"])["theme"]}' \
                 f' {users_db.get_record_by_id("users", question["author_id"])["user_name"]}'
        keyboard.row(button)
    keyboard.row('Отмена')
    return keyboard


adminsroom_message_main = ReplyKeyboardMarkup(resize_keyboard=True)
adminsroom_message_main.row('Ответить', 'Удалить')
adminsroom_message_main.row('Отмена')


def adminsroom_user_chose() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for user_id in users_db.get_ids('users'):
        user = users_db.get_record_by_id('users', user_id)
        button = f'{user_id}: {user["user_name"]}'
        keyboard.row(button)
    keyboard.row('Отмена')
    return keyboard


adminsroom_user_main = ReplyKeyboardMarkup(resize_keyboard=True)
adminsroom_user_main.row('Повысить', 'Понизить')
adminsroom_user_main.row('Написать сообщение')
adminsroom_user_main.row('Отмена')

help_main = ReplyKeyboardMarkup(resize_keyboard=True)
help_main.row('Помощь по боту')
help_main.row('Вопросы')
help_main.row('Отмена')


def help_questions() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('Задать вопрос')
    for question_id in help_questions_base.get_questions_ids():
        question = help_questions_base.get_question(question_id)
        button = f'{question_id}: {question["theme"]}'
        keyboard.row(button)
    keyboard.row('Отмена')
    return keyboard


def help_question_main_user(question_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    button_answers = InlineKeyboardButton(f'Ответы ({len(help_questions_base.get_answers_ids())})',
                                          callback_data=question_callback.new(
                                              action='answers', question_id=question_id
                                          ))
    button_answer_to_question = InlineKeyboardButton('Ответить', callback_data=question_callback.new(
        action='answer_to_question', question_id=question_id
    ))
    keyboard.row(button_answers)
    keyboard.row(button_answer_to_question)
    return keyboard


def help_question_main_admin(question_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    button_answers = InlineKeyboardButton(f'Ответы ({len(help_questions_base.get_answers_ids(question_id))})',
                                          callback_data=question_callback.new(
                                              action='answers', question_id=question_id
                                          ))
    button_delete = InlineKeyboardButton('Удалить', callback_data=question_callback.new(
        action='delete', question_id=question_id
    ))
    button_answer_to_question = InlineKeyboardButton('Ответить', callback_data=question_callback.new(
        action='answer_to_question', question_id=question_id
    ))
    keyboard.row(button_answers, button_delete)
    keyboard.row(button_answer_to_question)
    return keyboard


def help_answer_main_admin(question_id: int, answer_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    button_delete = InlineKeyboardButton('Удалить', callback_data=answers_callback.new(
        action='delete', question_id=question_id, answer_id=answer_id
    ))
    keyboard.row(button_delete)
    return keyboard


def profile_main() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    change_button = InlineKeyboardButton('Сменить имя', callback_data=change_name_callback.new(
        action='change_name'
    ))
    keyboard.row(change_button)
    return keyboard


cancel = ReplyKeyboardMarkup(resize_keyboard=True)
cancel.add('Отмена')
