from aiogram import types
from config import bot, dispatcher, data_base, Form
from aiogram.dispatcher import FSMContext
from secret import ADMIN_IDS


@dispatcher.message_handler(commands="set_commands", state="*")
async def cmd_set_commands(message: types.Message):
    if message.from_user.id == 772438359:
        commands = [types.BotCommand(command="/start",
                                             description="Стартовая команда. Записывает id пользователя в БД"),
                    types.BotCommand(command="/adm", description="Написать сообщение админу")]
        await bot.set_my_commands(commands)
        await message.answer("Команды настроены.")


@dispatcher.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.chat.id
    print(f'User_{user_id} write start')
    if user_id not in data_base.get_ids():
        if user_id in ADMIN_IDS:
            data_base.add_user(user_id, message.from_user.username, 'admin')
        else:
            if message.from_user.username:
                data_base.add_user(user_id, message.from_user.username, 'user')
            else:
                data_base.add_user(user_id, f'User_{user_id}', 'user')
    else:
        await bot.send_message(user_id, 'Вы уже есть в БД')


@dispatcher.message_handler(commands=['adm'])
async def admin_message(message: types.Message):
    await Form.message.set()
    await bot.send_message(message.chat.id, 'Введите своё сообщение')


@dispatcher.message_handler(state=Form.message)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    for user_id in data_base.get_ids():
        if data_base.get_user_by_id(user_id)['post'] == 'admin':
            await bot.send_message(user_id,
                                   'Пользователь ' + str(data_base.get_user_by_id(message.chat.id)['user_name']) +
                                   ':\n\n' + message.text + '\n\n' +
                                   'Дата и время: ' + str(message.date))
    await state.finish()


@dispatcher.message_handler(content_types=['text'])
async def mess(message: types.Message):
    text = list(message.text)
    text.reverse()
    text = ''.join(text)
    await bot.send_message(message.chat.id, text)
