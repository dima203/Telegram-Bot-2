from aiogram.utils.callback_data import CallbackData

question_callback = CallbackData('help', 'action', 'question_id')
answers_callback = CallbackData('help', 'action', 'question_id', 'answer_id')
