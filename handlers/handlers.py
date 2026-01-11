from aiogram import F, Router, Bot
from aiogram.types import Message
from aiogram.utils.deep_linking import create_start_link, decode_payload
from aiogram.filters import CommandStart, Command, CommandObject, StateFilter
from aiogram.fsm.context import FSMContext
import states as states
import keyboards as keyboards
import database.requests as requests
from aiogram.enums import ParseMode

router = Router()

@router.message(CommandStart(deep_link=True), StateFilter("*"))
async def start_handler_with_link(
    message: Message, command: CommandObject, state: FSMContext
):
    await state.clear()
    args = command.args
    payload = int(decode_payload(args))
    current_user_id = message.from_user.id
    

    if current_user_id == payload:
        await message.answer("Нельзя отправить сообщение самому себе xD")
        return
    
    if not requests.check_user_exists(payload):
        await message.answer(
            "Данного пользователя не существует или ссылка недействительна :C"
        )
        return
    
    if await requests.check_if_user_blocked(owner_user_id = payload, blocked_user_id=current_user_id):
        await message.answer("К сожалению пользователь вас заблокировал :C")
    else:
        await message.answer("Введи сообщение, которое хочешь отправить анонимно: ")
        await state.set_state(states.Send_message.receive_message)
        await state.update_data(receive_message=payload)

@router.message(CommandStart(deep_link=False))
async def start_handler(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id

    if await requests.check_user_exists(user_id):
        link = await create_start_link(bot, f'{message.from_user.id}', encode=True)
        await message.answer(
            f"Твоя ссылка:\n <code>{link}</code>",
            parse_mode=ParseMode.HTML
        )
    else:
        link = await create_start_link(bot, f'{message.from_user.id}', encode=True)
        await requests.create_user_profile(user_id)
        await message.answer(
            "Привет, рад видеть! Вот твоя новая ссылка:\n"
            f"<code>{link}</code>\n"
            "Cкопируй её в профиль и жди сообщений ;)",
            parse_mode=ParseMode.HTML
        )

@router.message(StateFilter(None), ~Command("donate"), ~Command("clean_blacklist"))
async def handle_plain_text(message: Message, bot: Bot):
    tg_id = message.from_user.id

    if await requests.check_user_exists(tg_id):
        link = await create_start_link(bot, f'{message.from_user.id}', encode=True)
        await message.answer(
            f"Твоя ссылка:\n <code>{link}</code>",
            parse_mode=ParseMode.HTML
        )
    else:
        link = await create_start_link(bot, f'{message.from_user.id}', encode=True)
        await message.answer(
            f"Привет! Твоя ссылка:\n <code>{link}</code>",
            parse_mode=ParseMode.HTML
        )


@router.message(states.Send_message.receive_message)
async def cmd_messaging(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    receiver_tg_id = data["receive_message"]
    message_id = message.message_id
    answer_button = await keyboards.create_answer_button(message.from_user.id, message_id)  # tg_id_1
    if message.photo:
        message_caption = ""
        if message.caption:
            message_caption = message.caption
        photo = message.photo[-1]
        await bot.send_photo(
            caption=f"Кто-то отправил тебе изображение!\n\n{message_caption}",
            chat_id=receiver_tg_id,
            photo=photo.file_id,
            reply_markup=answer_button,
            has_spoiler=True
        )
    elif message.text:
        await bot.send_message(text=f"Кто-то отправил тебе сообщение!: \n\n{message.text}", 
                               chat_id=receiver_tg_id, 
                               reply_markup=answer_button)
        await message.answer("Сообщение отправлено успешно!")
        await state.clear()
    else:
        message_caption = ""
        if message.caption:
            message_caption = message.caption
        await message.copy_to(caption="Кто-то отправил тебе сообщение!:\n\n{message_caption}", 
                              chat_id=receiver_tg_id, 
                              reply_markup=answer_button)
        await message.answer("Сообщение отправлено успешно!")
        await state.clear()

@router.message(states.Answer_message.receive_answer_message)
async def cmd_messaging(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    receiver_tg_id = data["receive_answer_message"]
    message_id = data["message_id"]
    answer_button = await keyboards.create_answer_button(message.from_user.id, message.message_id)
    if message.text:
        await bot.send_message(
            text=f"Кто-то ответил тебе на сообщение!:\n\n{message.text}",
            chat_id=receiver_tg_id,
            reply_to_message_id=int(message_id),
            reply_markup=answer_button
        )
    elif message.photo:
        message_caption = ""
        if message.caption:
            message_caption = message.caption
        photo = message.photo[-1]
        await bot.send_photo(
            caption=f"Кто-то ответил тебе изображением!\n\n{message_caption}",
            chat_id=receiver_tg_id,
            photo=photo.file_id,
            reply_markup=answer_button,
            has_spoiler=True
        )
    else:
        message_caption = ""
        if message.caption:
            message_caption = message.caption
        await message.copy_to(caption=f"Кто-то ответил тебе на сообщение!\n\n{message_caption}", 
                              chat_id=receiver_tg_id, 
                              reply_markup=answer_button)
        await message.answer("Сообщение отправлено успешно!")
        await state.clear()

    await message.answer("Ответ отправлен успешно!")
    await state.clear()


@router.message(Command("clean_blacklist"))
async def clean_blacklist(message: Message, state: FSMContext):
    if await requests.clean_blacklist(message.from_user.id):
        await message.answer("Черный список очищен!")
    else:
        await message.answer("Черный список пуст")