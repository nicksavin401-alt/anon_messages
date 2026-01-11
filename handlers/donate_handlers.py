from aiogram import Router, Bot
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import states as states
import keyboards as keyboards

donate_router = Router()

@donate_router.message(Command("donate"))
async def cmd_donate(
    message: Message, state: FSMContext
):
    await message.answer("Введите сумму звезд, которую хотите отправить разработчику: 🥺")
    await state.set_state(states.Donate.amount)

@donate_router.message(states.Donate.amount)
async def donate(
    message: Message, state: FSMContext
):
    if message.text.isdigit() and int(message.text)>0 and int(message.text)<100001:
        prices = [LabeledPrice(label="XTR", amount=int(message.text))]
        await message.answer_invoice(
            title="Помощь разработчику",
            description="Средства будут направлены на дальнейшую разработку! :3",
            prices=prices,
            provider_token="",
            payload=f"Помощь разработчику",
            currency="XTR"
            )
        await state.clear()
    else: 
        await message.answer("Пожалуйста, введите число не больше 100000")

@donate_router.pre_checkout_query()
async def on_pre_checkout_query(
    pre_checkout_query: PreCheckoutQuery, bot: Bot
):
    await pre_checkout_query.answer(
        ok=True,
        error_message=("Произошла ошибка, попробуйте ещё :C")
    )
    await bot.send_message(chat_id=pre_checkout_query.from_user.id,text="Благодарим за пожертвование!❤️")