from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from keyboards.inline import feedback
from database.postgre_feedback import add_feedback, get_update_history, update_feedback, delete_feedback


class Feedback(StatesGroup):
    f_type = State()
    text = State()


class ContinueFeedback(StatesGroup):
    text = State()


async def feedback_type(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer('Choose feedback type:',
                              reply_markup=feedback())
    await Feedback.f_type.set()


async def feedback_text(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['f_type'] = call.data
    await call.message.delete()
    await call.message.answer('Write text message for admin:')
    await Feedback.next()


async def feedback_finish(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = msg.text
    tg_id = msg.from_id
    try:
        await add_feedback(tg_id, data)
        await msg.answer('Your feedback has been sent! Wait for a response from the administrator.')
    except:
        await msg.answer('You have an open question, please wait for an answer')
    await state.finish()


async def feedback_continue(call: types.CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.answer('Write text message for admin:')
    await ContinueFeedback.text.set()


async def feedback_continue_step2(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = msg.text
    await msg.answer('Your feedback has been sent! Wait for a response from the administrator.')
    tg_id = msg.from_id
    history = await get_update_history(tg_id)
    await update_feedback(tg_id, history, data)

    await state.finish()


async def feedback_delete(call: types.CallbackQuery):
    tg_id = call.from_user.id
    await call.message.edit_reply_markup()
    await delete_feedback(tg_id)
    await call.message.answer('You finish chat with admin!')


def register(dp: Dispatcher):
    dp.register_callback_query_handler(feedback_type, text='feedback')
    dp.register_callback_query_handler(feedback_text, state=Feedback.f_type)
    dp.register_message_handler(feedback_finish, state=Feedback.text)
    dp.register_callback_query_handler(feedback_continue, text='continue_chat')
    dp.register_message_handler(feedback_continue_step2, state=ContinueFeedback.text)
    dp.register_callback_query_handler(feedback_delete, text='close_chat')
