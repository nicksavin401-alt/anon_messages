from aiogram.filters.callback_data import CallbackData

class AnswerCallbackFactory(CallbackData, prefix="respond"):
    action: str
    user_id: str
    message_id: str 
    