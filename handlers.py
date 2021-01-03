from aiogram import types
from config import (bot, is_test, dispatcher, users_db, lessons_db,
                    questions_base, help_questions_base,
                    Lessons, Message, Help, Profile)
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from secret import ADMIN_IDS
import keyboards
from callback_datas import answers_callback, question_callback, change_name_callback


@dispatcher.message_handler(lambda message: True if message.chat.id not in ADMIN_IDS and is_test else False, state='*')
async def test(message: types.Message):
    await bot.send_message(message.chat.id, 'Сейчас проводится тест. Бот временно не доступен =(')


@dispatcher.message_handler(commands='set_commands', state='*')
async def cmd_set_commands(message: types.Message):
    if message.from_user.id in ADMIN_IDS:
        commands = [types.BotCommand(command="/start",
                                     description="Стартовая команда. Записывает id пользователя в БД")]
        await bot.set_my_commands(commands)
        await message.answer("Команды настроены.")


@dispatcher.message_handler(commands=['start'], state='*')
async def start(message: types.Message, state: FSMContext):
    user_id = message.chat.id

    if user_id in ADMIN_IDS:
        keyboard = keyboards.main_admin
    else:
        keyboard = keyboards.main_user

    await state.finish()

    if user_id not in users_db.get_ids('users'):
        if user_id in ADMIN_IDS:
            users_db.add_record('users', user_id, message.from_user.username, 'admin', 100)

        else:
            if message.from_user.username:
                users_db.add_record('users', user_id, message.from_user.username, 'user', 1)

            else:
                users_db.add_record('users', user_id, f'User_{user_id}', 'user', 1)

        print(users_db.get_record_by_id('users', user_id))

        await bot.send_message(user_id, 'Стартуем', reply_markup=keyboard)

    else:
        await bot.send_message(user_id, 'Вы уже есть в БД', reply_markup=keyboard)


@dispatcher.message_handler(lambda message: True if message.chat.id not in users_db.get_ids('users') else False)
async def start_write(message: types.Message):
    await bot.send_message(message.chat.id, 'Напишите команду /start')


@dispatcher.message_handler(state='*', commands='cancel')
@dispatcher.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        current_state = await state.get_state()
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

        if current_state is None:
            return

        elif current_state == 'Lessons:group':
            if message.chat.id in ADMIN_IDS:
                keyboard = keyboards.main_admin
            else:
                keyboard = keyboards.main_user
            await state.finish()

        elif current_state == 'Lessons:lesson':
            keyboard = keyboards.lessons_groups
            await Lessons.group.set()

        elif current_state == 'Lessons:answer':
            keyboard = keyboards.lessons_main(data['group'])
            await Lessons.lesson.set()

        elif current_state == 'Lessons:message':
            keyboard = keyboards.lessons_lesson
            await Lessons.answer.set()

        elif current_state == 'Message:admin':
            if message.chat.id in ADMIN_IDS:
                keyboard = keyboards.main_admin
            else:
                keyboard = keyboards.main_user
            await state.finish()

        elif current_state == 'Message:question':
            keyboard = keyboards.adminsroom_main
            await Message.admin.set()

        elif current_state == 'Message:answer':
            keyboard = keyboards.adminsroom_message_chose()
            await Message.question.set()

        elif current_state == 'Message:message':
            keyboard = keyboards.adminsroom_message_main
            await Message.answer.set()

        elif current_state == 'Message:user':
            keyboard = keyboards.adminsroom_main
            await Message.admin.set()

        elif current_state == 'Message:answer_user':
            keyboard = keyboards.adminsroom_main
            await Message.admin.set()

        elif current_state == 'Message:message_user':
            keyboard = keyboards.adminsroom_user_main
            await Message.answer_user.set()

        elif current_state == 'Help:main':
            if message.chat.id in ADMIN_IDS:
                keyboard = keyboards.main_admin
            else:
                keyboard = keyboards.main_user
            await state.finish()

        elif current_state == 'Help:questions':
            keyboard = keyboards.help_main
            await Help.main.set()

        elif current_state == 'Help:create_answer':
            keyboard = keyboards.help_questions()
            await Help.questions.set()

        elif current_state == 'Help:create_question':
            keyboard = keyboards.help_questions()
            await Help.main.set()

        elif current_state == 'Help:create_question_text':
            keyboard = keyboards.help_questions()
            await Help.main.set()

        elif current_state == 'Profile:change_name':
            if message.chat.id in ADMIN_IDS:
                keyboard = keyboards.main_admin
            else:
                keyboard = keyboards.main_user
            await state.finish()

        await message.reply('ОК', reply_markup=keyboard)


@dispatcher.message_handler(lambda message: message.text.lower() == 'уроки', content_types=['text'])
async def lessons(message: types.Message):
    await Lessons.group.set()
    await bot.send_message(message.chat.id, 'Выбери группу', reply_markup=keyboards.lessons_groups)


@dispatcher.message_handler(content_types=['text'], state=Lessons.group)
async def lessons(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text.lower() == 'основы':
            group = 'begin'
        elif message.text.lower() == 'ооп':
            group = 'OOP'
        else:
            await bot.send_message(message.chat.id, 'Такой группы нет, выберите верное название группы')
            return

        data['group'] = group
        await Lessons.lesson.set()
        await bot.send_message(message.chat.id, 'Веберите урок', reply_markup=keyboards.lessons_main(group))


@dispatcher.message_handler(content_types=['text'], state=Lessons.lesson)
async def lessons_chose(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        lesson_id = ''
        for char in message.text:
            if char.isnumeric():
                lesson_id += char
            else:
                break
        if lesson_id:
            lesson_id = int(lesson_id)
        else:
            await bot.send_message(message.chat.id, 'Неправильный номер урока.'
                                                    ' Введите корректный номер или выберите из клавиатуры')
            return

        if int(lesson_id) not in lessons_db.get_ids(data['group']):
            await bot.send_message(message.chat.id, 'Неправильный номер урока.'
                                                    ' Введите корректный номер или выберите из клавиатуры')
            return

        data['lesson'] = lessons_db.get_record_by_id(data['group'], lesson_id)

        lesson = data['lesson']

    if lesson['level'] > users_db.get_record_by_id('users', message.chat.id)['level']:
        await bot.send_message(message.chat.id, 'У вас слишком низкий уровень. Чтобы получить уровень выше, '
                                                'Вы должны пройти тест в предыдущем уроке, если вы его прошли, но еще '
                                                'не получили уровень, обратитесь к преподавателю.\n'
                                                f'Ваш уровень: '
                                                f'{users_db.get_record_by_id("users", message.chat.id)["level"]}\n'
                                                f'Требуется уровень: {lesson["level"]}')
        return

    if 'Практическая' in lesson['theme']:
        text = lesson['text']
        text = text.split('\n')
        user_id = message.chat.id
        user_var = user_id % len(text)
        await bot.send_message(message.chat.id, f'Урок №{lesson_id}:\n\nТема: {lesson["theme"]} \n\n{text[user_var]}')
    else:
        await bot.send_message(message.chat.id, f'Урок №{lesson_id}:\n\nТема: {lesson["theme"]} \n\n{lesson["text"]}')
    await bot.send_message(message.chat.id, 'https://wombat.org.ua/AByteOfPython/AByteofPythonRussian-2.02.pdf')

    paths = lesson["materials"]
    paths = paths.split('\n')
    for path in paths:
        await bot.send_message(message.chat.id, path)
    await bot.send_message(message.chat.id,
                           'Удачи в изучении. Снизу кнопки для сдачи теста,'
                           ' помощи от преподавателя или, если вы не хотите, то отмена',
                           reply_markup=keyboards.lessons_lesson)
    await Lessons.next()


@dispatcher.message_handler(content_types=['text'], state=Lessons.answer)
async def lesson_handler(message: types.Message, state: FSMContext):
    if message.text.lower() == 'вопросы к преподавателю':
        async with state.proxy() as data:
            await Lessons.message.set()
            await bot.send_message(message.chat.id, 'Введи своё сообщение:', reply_markup=keyboards.cancel)
    elif message.text.lower() == 'тест':
        async with state.proxy() as data:
            await bot.send_message(message.chat.id, f'Это ссылка на тест.\nВаш id: {message.chat.id} '
                                                    f'(Обязательно этот id указать в тесте,'
                                                    f' без него преподаватель не сможет отправить ответ)'
                                                    f'\n{data["lesson"]["test"]}')


@dispatcher.message_handler(content_types=['text'], state=Lessons.message)
async def lesson_question(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        questions_base.add_message(message.text, data['group'], data['lesson']['id'], message.chat.id, message.date)
    await bot.send_message(message.chat.id, 'Сообщение отправлено', reply_markup=keyboards.lessons_lesson)
    await Lessons.answer.set()


@dispatcher.message_handler(lambda message: True if (message.text.lower() == 'комната админов'
                                                     and message.chat.id in ADMIN_IDS) else False,
                            content_types=['text'])
async def admin(message: types.Message):
    await Message.admin.set()
    await bot.send_message(message.chat.id, 'Добро пожаловать', reply_markup=keyboards.adminsroom_main)


@dispatcher.message_handler(content_types=['text'], state=Message.admin)
async def admin_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text.lower() == 'сообщения':
            await Message.question.set()
            await bot.send_message(message.chat.id, 'Выберите сообщение',
                                   reply_markup=keyboards.adminsroom_message_chose())

        elif message.text.lower() == 'пользователь':
            await Message.user.set()
            await bot.send_message(message.chat.id, 'Введите id пользователя',
                                   reply_markup=keyboards.adminsroom_user_chose())

        elif message.text.lower() == 'все пользователи':
            with open('users.txt', 'w') as users_file:
                users_file.write(f'{"id":^11}|{"username":^20}|{"post":^6}|{"level":^6}\n')
                users_file.write('-' * (12 + 21 + 7 + 6) + '\n')
                for user_id in users_db.get_ids('users'):
                    user = users_db.get_record_by_id('users', user_id)
                    users_file.write(f'{user["id"]:<11}|{user["user_name"]:^20}|{user["post"]:6}|{user["level"]:<6}\n')
            with open('users.txt', 'r') as users_file:
                await bot.send_document(message.chat.id, users_file)


@dispatcher.message_handler(content_types=['text'], state=Message.question)
async def admin_chose_message(message: types.Message, state: FSMContext):
    message_id = ''
    for char in message.text:
        if char.isnumeric():
            message_id += char
        else:
            break
    if message_id:
        message_id = int(message_id)
    else:
        await bot.send_message(message.chat.id, 'Неправильный номер сообщения.'
                                                ' Введите корректный номер или выберите из клавиатуры')
        return

    if int(message_id) not in questions_base.get_ids():
        await bot.send_message(message.chat.id, 'Неправильный номер сообщения.'
                                                ' Введите корректный номер или выберите из клавиатуры')
        return

    async with state.proxy() as data:
        data['message_id'] = message_id
        question = questions_base.get_message(message_id)
        text = f'id сообщения: {message_id}\n' \
               f'Урок: {lessons_db.get_record_by_id("begin", question["lesson_id"])["theme"]}\n' \
               f'Пользователь: {users_db.get_record_by_id("users", question["author_id"])["user_name"]} ' \
               f'({users_db.get_record_by_id("users", question["author_id"])["level"]}) ' \
               f'({question["author_id"]})\n\n' \
               f'{question["text"]}\n\n' \
               f'{question["date"]}'
        await bot.send_message(message.chat.id, text)
        await Message.answer.set()
        await bot.send_message(message.chat.id, 'Что делать будем?', reply_markup=keyboards.adminsroom_message_main)


@dispatcher.message_handler(content_types=['text'], state=Message.user)
async def admin_chose_user(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        user_id = ''
        for char in message.text:
            if char.isnumeric():
                user_id += char
            else:
                break
        if user_id:
            user_id = int(user_id)
        else:
            await bot.send_message(message.chat.id, 'Неправильный id пользователя')
            return

        if int(user_id) not in users_db.get_ids('users'):
            await bot.send_message(message.chat.id, 'Неправильный id пользователя')
            return

        data['user_id'] = int(user_id)
        user = users_db.get_record_by_id('users', data['user_id'])
        text = f'id: {user["id"]}\n' \
               f'username: {user["user_name"]}\n' \
               f'level: {user["level"]}\n' \
               f'post: {user["post"]}'
        await Message.answer_user.set()
        await bot.send_message(message.chat.id, text, reply_markup=keyboards.adminsroom_user_main)


@dispatcher.message_handler(content_types=['text'], state=Message.answer)
async def admin_message_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text.lower() == 'ответить':
            await Message.message.set()
            await bot.send_message(message.chat.id, 'Введи своё сообщение:', reply_markup=keyboards.cancel)

        elif message.text.lower() == 'удалить':
            questions_base.delete_message(data['message_id'])
            await Message.question.set()
            await bot.send_message(message.chat.id, 'Сообщение удалено',
                                   reply_markup=keyboards.adminsroom_message_chose())


@dispatcher.message_handler(content_types=['text'], state=Message.answer_user)
async def admin_user_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text.lower() == 'повысить':
            user_id = data['user_id']
            users_db.update_column('users', user_id, 'level', users_db.get_record_by_id('users', user_id)['level'] + 1)
            await bot.send_message(message.chat.id, f'Уровень повышен '
                                                    f'({users_db.get_record_by_id("users", user_id)["level"]})')
            await bot.send_message(data['user_id'], f'Ваш уровень повышен '
                                                    f'({users_db.get_record_by_id("users", user_id)["level"]})')

        elif message.text.lower() == 'понизить':
            user_id = data['user_id']
            users_db.update_column('users', user_id, 'level', users_db.get_record_by_id("users", user_id)['level'] - 1)
            await bot.send_message(message.chat.id, f'Уровень понижен '
                                                    f'({users_db.get_record_by_id("users", user_id)["level"]})')
            await bot.send_message(data['user_id'], f'Ваш уровень понижен '
                                                    f'({users_db.get_record_by_id("users", user_id)["level"]})')

        elif message.text.lower() == 'написать сообщение':
            await Message.message_user.set()
            await bot.send_message(message.chat.id, 'Введи своё сообщение:', reply_markup=keyboards.cancel)


@dispatcher.message_handler(content_types=['text'], state=Message.message)
async def admin_question_answer(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        message_id = data['message_id']
        question = questions_base.get_message(message_id)
        if question['author_id'] in users_db.get_ids('users'):
            await bot.send_message(question['author_id'],
                                   f'Вам пришел ответ на ваш вопрос:\n'
                                   f'Урок №{question["lesson_id"]}: '
                                   f'{lessons_db.get_record_by_id(question["group"], question["lesson_id"])["theme"]}' +
                                   f'\n\n {question["text"]}\n\n'
                                   f'Ответ:\n{message.text}')

    questions_base.delete_message(message_id)
    await bot.send_message(message.chat.id, 'Сообщение отправлено', reply_markup=keyboards.adminsroom_message_chose())
    await Message.question.set()


@dispatcher.message_handler(content_types=['text'], state=Message.message_user)
async def admin_user_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        user_id = data['user_id']
        await bot.send_message(user_id, f'Вам написал админ:\n'
                               f'{message.text}')
    await bot.send_message(message.chat.id, 'Сообщение отправлено', reply_markup=keyboards.adminsroom_user_main)
    await Message.answer_user.set()


@dispatcher.message_handler(lambda message: True if message.text.lower() == 'помощь' else False, content_types=['text'])
async def bot_help(message: types.Message):
    await Help.main.set()
    await bot.send_message(message.chat.id, 'Выберите вопрос или напишите свой', reply_markup=keyboards.help_main)


@dispatcher.message_handler(content_types=['text'], state=Help.main)
async def help_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text.lower() == 'вопросы':
            await Help.questions.set()
            await bot.send_message(message.chat.id, 'Выберите вопрос или задайте свой',
                                   reply_markup=keyboards.help_questions())

        elif message.text.lower() == 'помощь по боту':
            text = 'Приветствую тебя.\n' \
                   'Данный бот нужен тем, кто хочет изучить язык программирования python.\n' \
                   'Для того, чтобы начать перейдите в раздел "Уроки". Там находятся уроки. ' \
                   'Проходя их, Вы будете зарабатывать уровень и открывать новые уроки.' \
                   'В дальнейшем планируется добавить много новых функций и фишек.\n' \
                   'Если у вас возникли проблемы, то пишите свои вопросы здесь или под конкретным уроком.\n' \
                   'Успехов!!!'
            await bot.send_message(message.chat.id, text)


@dispatcher.message_handler(content_types=['text'], state=Help.questions)
async def help_questions_chose(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text.lower() == 'задать вопрос':
            await Help.create_question.set()
            await bot.send_message(message.chat.id, 'Введите тему вопроса', reply_markup=keyboards.cancel)

        else:
            question_id = ''
            for char in message.text:
                if char.isnumeric():
                    question_id += char
                else:
                    break
            if question_id:
                question_id = int(question_id)
            else:
                await bot.send_message(message.chat.id, 'Неправильный номер вопроса.'
                                                        ' Введите корректный номер или выберите из клавиатуры')
                return

            if int(question_id) not in help_questions_base.get_questions_ids():
                await bot.send_message(message.chat.id, 'Неправильный номер вопроса.'
                                                        ' Введите корректный номер или выберите из клавиатуры')
                return

            data['question'] = help_questions_base.get_question(question_id)
            question = data['question']
            text = f'Тема: {question["theme"]}\n' \
                   f'Пользователь: {users_db.get_record_by_id("users", question["author_id"])["user_name"]} ' \
                   f'({users_db.get_record_by_id("users", question["author_id"])["level"]})\n\n' \
                   f'{question["text"]}\n\n' \
                   f'{question["date"]}'

            if message.chat.id in ADMIN_IDS:
                keyboard = keyboards.help_question_main_admin(question_id)
            else:
                keyboard = keyboards.help_question_main_user(question_id)
            await bot.send_message(message.chat.id, text, reply_markup=keyboard)


@dispatcher.message_handler(content_types=['text'], state=Help.create_question)
async def help_questions_chose(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['theme'] = message.text
        await Help.create_question_text.set()
        await bot.send_message(message.chat.id, 'Введите текст вопроса', reply_markup=keyboards.cancel)


@dispatcher.message_handler(content_types=['text'], state=Help.create_question_text)
async def help_questions_chose(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
        await Help.questions.set()
        help_questions_base.add_question(data['theme'], data['text'], message.chat.id, message.date)
        await bot.send_message(message.chat.id, 'Вопрос создан', reply_markup=keyboards.help_questions())


@dispatcher.message_handler(content_types=['text'], state=Help.create_answer)
async def create_answer(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = message.text
        question_id = data['question_id']
        author_id = help_questions_base.get_question(question_id)['author_id']
        help_questions_base.add_answer(question_id, text, message.chat.id, message.date)
        await bot.send_message(message.chat.id, 'Ответ отправлен', reply_markup=keyboards.help_questions())
        await bot.send_message(author_id,
                               f'Пользователь {users_db.get_record_by_id("users", message.chat.id)["user_name"]} '
                               f'({users_db.get_record_by_id("users", message.chat.id)["level"]})'
                               f' ответил на Ваш вопрос: '
                               f'{help_questions_base.get_question(question_id)["theme"]}')
        await Help.questions.set()


@dispatcher.message_handler(lambda message: True if message.text.lower() == 'профиль' else False,
                            content_types=['text'])
async def profile(message: types.Message):
    user = users_db.get_record_by_id('users', message.chat.id)
    text = f'Имя: {user["user_name"]}\n' \
           f'id: {user["id"]}\n' \
           f'Уровень: {user["level"]}\n'
    await bot.send_message(message.chat.id, text, reply_markup=keyboards.profile_main())


@dispatcher.message_handler(content_types=['text'], state=Profile.change_name)
async def create_answer(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        users_db.update_column('users', message.chat.id, 'user_name', message.text)
        await state.finish()
        if message.chat.id in ADMIN_IDS:
            await bot.send_message(message.chat.id, 'Имя изменено', reply_markup=keyboards.main_admin)
        else:
            await bot.send_message(message.chat.id, 'Имя изменено', reply_markup=keyboards.main_user)


@dispatcher.message_handler(content_types=['text'])
async def all_message(message: types.Message):
    text = list(message.text)
    text.reverse()
    text = ''.join(text)
    await bot.send_message(message.chat.id, text)


@dispatcher.callback_query_handler(lambda call: True if is_test and call.from_user.id not in ADMIN_IDS else False,
                                   state='*')
async def test(call: types.CallbackQuery):
    await bot.send_message(call.from_user.id, 'Сейчас проводится тест. Бот временно не доступен =(')


@dispatcher.callback_query_handler(question_callback.filter(action='answers'), state='*')
async def help_answers(call: types.CallbackQuery, callback_data: dict):
    await call.answer(cache_time=60)
    question_id = int(callback_data.get('question_id'))
    for answer_id in help_questions_base.get_answers_ids(question_id):
        answer = help_questions_base.get_question_answer(question_id, answer_id)
        text = f'Пользователь: {users_db.get_record_by_id("users", answer["author_id"])["user_name"]}' \
               f' ({users_db.get_record_by_id("users", answer["author_id"])["level"]})\n\n' \
               f'{answer["text"]}\n\n' \
               f'{answer["date"]}'
        if call.from_user.id in ADMIN_IDS:
            await bot.send_message(call.from_user.id, text,
                                   reply_markup=keyboards.help_answer_main_admin(question_id, answer_id))
        else:
            await bot.send_message(call.from_user.id, text)


@dispatcher.callback_query_handler(question_callback.filter(action='answer_to_question'), state=Help.questions)
async def help_answers(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=60)
    async with state.proxy() as data:
        question_id = int(callback_data.get('question_id'))
        data['question_id'] = question_id
        await Help.create_answer.set()
        await bot.send_message(call.from_user.id, 'Введите ответ', reply_markup=keyboards.cancel)


@dispatcher.callback_query_handler(answers_callback.filter(action='delete'), state='*')
async def help_answers(call: types.CallbackQuery, callback_data: dict):
    await call.answer(cache_time=60)
    if callback_data.get('answer_id'):
        question_id = int(callback_data.get('question_id'))
        answer_id = int(callback_data.get('answer_id'))
        await bot.delete_message(call.from_user.id, call.message.message_id)
        help_questions_base.delete_answer(question_id, answer_id)


@dispatcher.callback_query_handler(question_callback.filter(action='delete'), state='*')
async def help_answers(call: types.CallbackQuery, callback_data: dict):
    await call.answer(cache_time=60)
    if callback_data.get('question_id'):
        question_id = int(callback_data.get('question_id'))
        await bot.delete_message(call.from_user.id, call.message.message_id)
        help_questions_base.delete_question(question_id)
        await bot.send_message(call.from_user.id, 'Удалено', reply_markup=keyboards.help_questions())


@dispatcher.callback_query_handler(change_name_callback.filter(action='change_name'), state='*')
async def change_name(call: types.CallbackQuery, callback_data: dict):
    await call.answer(cache_time=60)
    await Profile.change_name.set()
    await bot.send_message(call.from_user.id, 'Введите новое имя', reply_markup=keyboards.cancel)


@dispatcher.callback_query_handler(state='*')
async def all_callback(call):
    await call.answer(cache_time=60)
    await bot.send_message(call.from_user.id, 'gg')
