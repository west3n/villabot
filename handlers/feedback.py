from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from keyboards.inline import feedback
from database.postgre_feedback import add_feedback, get_update_history, update_feedback, delete_feedback
from database.postgre_user import lang
from texts.text import get_text


class Feedback(StatesGroup):
    f_type = State()
    text = State()


class ContinueFeedback(StatesGroup):
    text = State()


async def cmd_cancel(call: types.CallbackQuery, state: FSMContext):
    tg_id = call.from_user.id
    await call.message.delete()
    await state.finish()
    action = 4
    language = await lang(tg_id)
    text = await get_text(action, language)
    await call.message.answer(text)


async def feedback_type(call: types.CallbackQuery):
    tg_id = call.from_user.id
    await call.message.delete()
    action = 5
    language = await lang(tg_id)
    text = await get_text(action, language)
    await call.message.answer(text=text,
                              reply_markup=feedback(language))
    await Feedback.f_type.set()


async def feedback_type_2(message: types.Message):
    tg_id = message.from_user.id
    await message.delete()
    action = 5
    language = await lang(tg_id)
    text = await get_text(action, language)
    await message.answer(text=text,
                         reply_markup=feedback(language))
    await Feedback.f_type.set()


async def feedback_text(call: types.CallbackQuery, state: FSMContext):
    tg_id = call.from_user.id
    async with state.proxy() as data:
        data['f_type'] = call.data
    action = 6
    language = await lang(tg_id)
    text = await get_text(action, language)
    await call.message.delete()
    await call.message.answer(text=text)
    await Feedback.next()


async def feedback_finish(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = msg.text
    tg_id = msg.from_id
    try:
        action = 7
        language = await lang(tg_id)
        text = await get_text(action, language)
        await add_feedback(tg_id, data)
        await msg.answer(text=text)
    except:
        action = 8
        language = await lang(tg_id)
        text = await get_text(action, language)
        await msg.answer(text=text)
    await state.finish()


async def feedback_continue(call: types.CallbackQuery):
    await call.message.edit_reply_markup()
    tg_id = call.from_user.id
    action = 6
    language = await lang(tg_id)
    text = await get_text(action, language)
    await call.message.answer(text=text)
    await ContinueFeedback.text.set()


async def feedback_continue_step2(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = msg.text
    tg_id = msg.from_id
    action = 7
    language = await lang(tg_id)
    text = await get_text(action, language)
    await msg.answer(text=text)
    history = await get_update_history(tg_id)
    await update_feedback(tg_id, history, data)

    await state.finish()


async def feedback_delete(call: types.CallbackQuery):
    tg_id = call.from_user.id
    action = 9
    language = await lang(tg_id)
    text = await get_text(action, language)
    await call.message.edit_reply_markup()
    await delete_feedback(tg_id)
    await call.message.answer(text=text)


def register(dp: Dispatcher):
    dp.register_callback_query_handler(cmd_cancel, text='cancel', state='*')
    dp.register_callback_query_handler(feedback_type, text='feedback')
    dp.register_message_handler(feedback_type_2, commands='feedback', state="*")
    dp.register_callback_query_handler(feedback_text, state=Feedback.f_type)
    dp.register_message_handler(feedback_finish, state=Feedback.text)
    dp.register_callback_query_handler(feedback_continue, text='continue_chat')
    dp.register_message_handler(feedback_continue_step2, state=ContinueFeedback.text)
    dp.register_callback_query_handler(feedback_delete, text='close_chat')
