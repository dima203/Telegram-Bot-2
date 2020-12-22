from aiogram import types
from config import bot, dispatcher, users_db, lessons_db, questions_base, Lessons, Message
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from secret import ADMIN_IDS


@dispatcher.message_handler(commands="set_commands", state="*")
async def cmd_set_commands(message: types.Message):
    if message.from_user.id in ADMIN_IDS:
        commands = [types.BotCommand(command="/start",
                                     description="Стартовая команда. Записывает id пользователя в БД"),
                    types.BotCommand(command="/adm", description="Написать сообщение админу")]
        await bot.set_my_commands(commands)
        await message.answer("Команды настроены.")


@dispatcher.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.chat.id
    print(f'User_{user_id} write start')

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('Уроки', 'Помощь')
    keyboard.row('Комната админов')

    if user_id not in users_db.get_ids('users'):
        if user_id in ADMIN_IDS:
            users_db.add_record('users', user_id, message.from_user.username, 'admin')

        else:
            if message.from_user.username:
                users_db.add_record('users', user_id, message.from_user.username, 'user')

            else:
                users_db.add_record('users', user_id, f'User_{user_id}', 'user')

        await bot.send_message(user_id, 'Стартуем', reply_markup=keyboard)

    else:
        await bot.send_message(user_id, 'Вы уже есть в БД', reply_markup=keyboard)


@dispatcher.message_handler(lambda message: True if message.chat.id not in users_db.get_ids('users') else False)
async def start(message: types.Message):
    await bot.send_message(message.chat.id, 'Напишите команду /start')


@dispatcher.message_handler(lambda message: message.text.lower() == 'уроки')
async def mess(message: types.Message):
    await Lessons.lesson.set()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for lesson_id in lessons_db.get_ids('lessons'):
        res = lessons_db.get_record_by_id('lessons', lesson_id)
        keyboard.row(f'{res["id"]:3}: {res["theme"]}')
    keyboard.row('Отмена')
    await bot.send_message(message.chat.id, 'Выбери урок', reply_markup=keyboard)


@dispatcher.message_handler(state='*', commands='cancel')
@dispatcher.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    if current_state is None:
        return

    elif current_state == 'Lessons:lesson':
        keyboard.row('Уроки', 'Помощь')
        keyboard.row('Комната админов')
        await state.finish()

    elif current_state == 'Lessons:answer':
        for lesson_id in lessons_db.get_ids('lessons'):
            res = lessons_db.get_record_by_id('lessons', lesson_id)
            keyboard.row(f'{res["id"]:3}: {res["theme"]}')
        keyboard.row('Отмена')
        await Lessons.lesson.set()

    elif current_state == 'Lessons:message':
        keyboard.row('Тест')
        keyboard.row('Вопросы к преподавателю')
        keyboard.row('Отмена')
        await Lessons.answer.set()

    elif current_state == 'Message:admin':
        keyboard.row('Уроки', 'Помощь')
        keyboard.row('Комната админов')
        await state.finish()

    elif current_state == 'Message:question':
        keyboard.row('Сообщения')
        keyboard.row('Отмена')
        await Message.admin.set()

    elif current_state == 'Message:answer':
        for question_id in questions_base.get_ids():
            question = questions_base.get_message(question_id)
            button = f'{question_id}: {lessons_db.get_record_by_id("lessons", question["lesson_id"])["theme"]}' \
                     f' {users_db.get_record_by_id("users", question["author_id"])["user_name"]}'
            keyboard.row(button)
        keyboard.row('Отмена')
        await Message.question.set()

    elif current_state == 'Message:message':
        keyboard.row('Ответить', 'Удалить')
        keyboard.row('Отмена')
        await Message.answer.set()

    await message.reply('ОК', reply_markup=keyboard)


@dispatcher.message_handler(state=Lessons.lesson)
async def mess(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        lesson_id = ''
        for char in message.text:
            if char.isnumeric():
                lesson_id += char
            else:
                break
        lesson_id = int(lesson_id)

        data['lesson'] = lessons_db.get_record_by_id('lessons', lesson_id)

        lesson = data['lesson']

    await bot.send_message(message.chat.id, f'Урок №{lesson_id}:\n\nТема: {lesson["theme"]} \n\n{lesson["text"]}')
    await bot.send_message(message.chat.id, 'https://wombat.org.ua/AByteOfPython/AByteofPythonRussian-2.02.pdf')

    paths = lesson["materials"]
    paths = paths.split('\n')
    for path in paths:
        await bot.send_message(message.chat.id, path)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('Тест')
    keyboard.row('Вопросы к преподавателю')
    keyboard.row('Отмена')
    await bot.send_message(message.chat.id,
                           'Удачи в изучении. Снизу кнопки для сдачи теста,'
                           ' помощи от преподавателя или, если вы не хотите, то отмена',
                           reply_markup=keyboard)
    await Lessons.next()


@dispatcher.message_handler(state=Lessons.answer)
async def mess(message: types.Message, state: FSMContext):
    if message.text.lower() == 'вопросы к преподавателю':
        async with state.proxy() as data:
            await Lessons.message.set()
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add('Отмена')
            await bot.send_message(message.chat.id, 'Введи своё сообщение:', reply_markup=keyboard)
    elif message.text.lower() == 'тест':
        async with state.proxy() as data:
            await bot.send_message(message.chat.id, f'Это ссылка на тест.\nВаш id: {message.chat.id} '
                                                    f'(Обязательно этот id указать в тесте,'
                                                    f' без него преподаватель не сможет отправить ответ)'
                                                    f'\n{data["lesson"]["test"]}')


@dispatcher.message_handler(state=Lessons.message)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        questions_base.add_message(message.text, data['lesson']['id'], message.chat.id, message.date)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('Тест')
    keyboard.row('Вопросы к преподавателю')
    keyboard.row('Отмена')
    await bot.send_message(message.chat.id, 'Сообщение отправлено', reply_markup=keyboard)
    await Lessons.answer.set()


@dispatcher.message_handler(lambda message: True if (message.text.lower() == 'комната админов'
                                                     and message.chat.id in ADMIN_IDS) else False)
async def mess(message: types.Message):
    await Message.admin.set()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('Сообщения')
    keyboard.row('Отмена')
    await bot.send_message(message.chat.id, 'Добро пожаловать', reply_markup=keyboard)


@dispatcher.message_handler(state=Message.admin)
async def mess(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text.lower() == 'сообщения':
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for question_id in questions_base.get_ids():
                question = questions_base.get_message(question_id)
                button = f'{question_id}: {lessons_db.get_record_by_id("lessons", question["lesson_id"])["theme"]}' \
                         f' {users_db.get_record_by_id("users", question["author_id"])["user_name"]}'
                keyboard.row(button)
            keyboard.row('Отмена')
            await Message.question.set()
            await bot.send_message(message.chat.id, 'Выберите сообщение', reply_markup=keyboard)


@dispatcher.message_handler(state=Message.question)
async def mess(message: types.Message, state: FSMContext):
    message_id = ''
    for char in message.text:
        if char.isnumeric():
            message_id += char
        else:
            break
    message_id = int(message_id)

    async with state.proxy() as data:
        data['message_id'] = message_id
        question = questions_base.get_message(message_id)
        text = f'id сообщения: {message_id}\n' \
               f'Урок: {lessons_db.get_record_by_id("lessons", question["lesson_id"])["theme"]}\n' \
               f'Пользователь: {users_db.get_record_by_id("users", question["author_id"])["user_name"]}\n\n' \
               f'{question["text"]}\n\n' \
               f'{question["date"]}'
        await bot.send_message(message.chat.id, text)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.row('Ответить', 'Удалить')
        keyboard.row('Отмена')
        await Message.answer.set()
        await bot.send_message(message.chat.id, 'Что делать будем?', reply_markup=keyboard)


@dispatcher.message_handler(state=Message.answer)
async def mess(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text.lower() == 'ответить':
            await Message.message.set()
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add('Отмена')
            await bot.send_message(message.chat.id, 'Введи своё сообщение:', reply_markup=keyboard)

        elif message.text.lower() == 'удалить':
            questions_base.delete_message(data['message_id'])
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for question_id in questions_base.get_ids():
                question = questions_base.get_message(questions_base)
                button = f'{question_id}: {lessons_db.get_record_by_id("lessons", question["lessons_id"])["theme"]}' \
                         f' {users_db.get_record_by_id("users", question["author_id"])["user_name"]}'
                keyboard.row(button)
            keyboard.row('Отмена')
            await Message.question.set()
            await bot.send_message(message.chat.id, 'Сообщение удалено', reply_markup=keyboard)


@dispatcher.message_handler(state=Message.message)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        message_id = data['message_id']
        question = questions_base.get_message(message_id)
        if question['author_id'] in users_db.get_ids('users'):
            await bot.send_message(question['author_id'],
                                   f'Вам пришел ответ на ваш вопрос:\n'
                                   f'Урок №{question["lesson_id"]}: '
                                   f'{lessons_db.get_record_by_id("lessons", question["lesson_id"])["theme"]}' +
                                   f'\n\n {question["text"]}\n\n'
                                   f'Ответ:\n{message.text}')

    questions_base.delete_message(message_id)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for question_id in questions_base.get_ids():
        question = questions_base.get_message(question_id)
        button = f'{question_id}: {lessons_db.get_record_by_id("lessons", question["lesson_id"])["theme"]}' \
                 f' {users_db.get_record_by_id("users", question["author_id"])["user_name"]}'
        keyboard.row(button)
    keyboard.row('Отмена')
    await bot.send_message(message.chat.id, 'Сообщение отправлено', reply_markup=keyboard)
    await Message.question.set()


@dispatcher.message_handler(content_types=['text'])
async def mess(message: types.Message):
    text = list(message.text)
    text.reverse()
    text = ''.join(text)
    await bot.send_message(message.chat.id, text)
