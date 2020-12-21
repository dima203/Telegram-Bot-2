from aiogram import executor
from config import dispatcher
import handlers


executor.start_polling(dispatcher, skip_updates=True)
