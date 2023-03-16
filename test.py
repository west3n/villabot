from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
bot = Bot(token='ХУЙ НАХУЙ')


class MyStatesGroup(StatesGroup):
    my_state = State()


async def save_options(selected_options: list[str], state: FSMContext):
    await state.update_data(selected_options=selected_options)
    await state.update_data({'selected_options': []})  # <-- добавить ключ 'selected_options'
    await state.reset_state(with_data=False)


async def my_handler(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    selected_option = call.data.replace("select_option:", "")
    # Получаем идентификаторы сообщений
    message_id = call.message.message_id
    inline_message_id = call.inline_message_id
    # Получаем текущую разметку клавиатуры
    keyboard = call.message.reply_markup
    # Обновляем текст кнопки, если она еще не была выбрана
    for row in keyboard.inline_keyboard:
        for button in row:
            if button.callback_data == call.data:
                if "Выбрано" not in button.text:
                    button.text = f"{selected_option} (Выбрано)"
                    async with state.proxy() as data:
                        selected_options = data.get('selected_options', [])
                        selected_options.append(selected_option)
                        await state.update_data(selected_options=selected_options)
                elif "Выбрано" in button.text:
                    button.text = selected_option
                    async with state.proxy() as data:
                        selected_options = data.get('selected_options', [])
                        selected_options.remove(selected_option)
                        await state.update_data(selected_options=selected_options)

    # Проверяем, что "Done" кнопка уже добавлена в разметку клавиатуры
    done_button_added = False
    for row in keyboard.inline_keyboard:
        for button in row:
            if button.callback_data == "done":
                done_button_added = True
    # Если "Done" кнопка еще не добавлена, то добавляем ее
    if not done_button_added:
        done_button = InlineKeyboardButton("Done", callback_data="done")
        keyboard.add(done_button)
    # Обновляем разметку клавиатуры, если кнопка не была помечена как "выбранная"
    if selected_option not in call.message.text:
        await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=message_id,
                                            inline_message_id=inline_message_id, reply_markup=keyboard)
    else:
        await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=message_id,
                                            inline_message_id=inline_message_id, reply_markup=keyboard)


async def done_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    async with state.proxy() as data:
        selected_options = data.get('selected_options', [])
    if selected_options:
        await callback_query.message.answer("Selected options: {}".format(", ".join(selected_options)))
        # сохраняем выбранные опции в состоянии
        await save_options(selected_options, state)
    else:
        await callback_query.message.answer("No options selected")


async def select_options(message: types.Message, state: FSMContext):
    keyboard = await show_options()
    await message.answer("Select options:", reply_markup=keyboard)
    await MyStatesGroup.my_state.set()


async def show_options():
    options = ["Option 1", "Option 2", "Option 3"]
    keyboard = InlineKeyboardMarkup()
    for option in options:
        button = InlineKeyboardButton(option, callback_data=f"select_option:{option}")
        keyboard.add(button)
    keyboard.add(InlineKeyboardButton("Done", callback_data="done"))
    for row in keyboard.inline_keyboard:
        for button in row:
            if button.callback_data == "done":
                row.remove(button)
    return keyboard


def register(dp: Dispatcher):
    dp.register_message_handler(select_options, commands="start")
    dp.register_callback_query_handler(my_handler, lambda c: c.data.startswith("select_option"),
                                       state=MyStatesGroup.my_state)
    dp.register_callback_query_handler(done_handler, lambda c: c.data == "done",
                                       state=MyStatesGroup.my_state)
