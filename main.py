from aiogram import executor
from config import bot, is_test, dispatcher, users_db
import keyboards
from secret import ADMIN_IDS
import handlers


async def start(bot_dispatcher):
    if is_test:
        for user_id in users_db.get_ids('users'):
            if user_id in ADMIN_IDS:
                await bot.send_message(user_id, 'Бот запущен в тестовом режиме', reply_markup=keyboards.main_admin)
    else:
        for user_id in users_db.get_ids('users'):
            if user_id in ADMIN_IDS:
                await bot.send_message(user_id, 'Бот запущен', reply_markup=keyboards.main_admin)
            else:
                await bot.send_message(user_id, 'Бот запущен', reply_markup=keyboards.main_user)

executor.start_polling(dispatcher, skip_updates=True, on_startup=start)
