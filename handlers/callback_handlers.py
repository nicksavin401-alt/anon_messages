from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
import states as states
import keyboards as keyboards
import database.requests as requests
from callback_factory import AnswerCallbackFactory

callback_router = Router()

@callback_router.callback_query(AnswerCallbackFactory.filter(F.action == "respond"))
async def handle_reply_message(callback: CallbackQuery, callback_data: AnswerCallbackFactory, state: FSMContext):
    receiver_tg_id = int(callback_data.user_id)
    message_id = int(callback_data.message_id)
    if await requests.check_if_user_blocked(owner_user_id = receiver_tg_id, blocked_user_id=callback.from_user.id):
        await callback.message.answer("К сожалению пользователь вас заблокировал :C")
    else: 
        await callback.message.answer("Введи сообщение которое хочешь отправить: ")
        await state.set_state(states.Answer_message.receive_answer_message)
        await state.update_data({"receive_answer_message" : receiver_tg_id,
                                 "message_id" : message_id})

@callback_router.callback_query(AnswerCallbackFactory.filter(F.action == "block"))
async def handle_reply_message(callback: CallbackQuery, callback_data: AnswerCallbackFactory, state: FSMContext):
    receiver_tg_id = int(callback_data.user_id)
    await requests.block_user(callback.from_user.id, receiver_tg_id)
    await callback.message.answer("Пользователь заблокирован!\n " \
                                  "Разблокировать: /clean_blacklist:")