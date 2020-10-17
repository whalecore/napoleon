# from aiogram import Bot, Dispatcher, executor, types
# from aiogram.dispatcher import FSMContext
# from aiogram.dispatcher import storage
# from aiogram.dispatcher.filters.state import State, StatesGroup
# from aiogram.contrib.fsm_storage.memory import MemoryStorage
# import logging

# from aiogram.types.message import ContentTypes

# BOT_TOKEN = '1102746633:AAH2i3PRyzXa4AzKNzzoQgM8P20gLmXK4e8'

# storage = MemoryStorage()

# bot = Bot(token=BOT_TOKEN)
# dp = Dispatcher(bot, storage=storage)

# logging.basicConfig(level=logging.DEBUG)

# available_fn = ['суши', "спагетти", "хачапури"]
# available_sizes = ['маленькая', "средняя", "большая"]


# class OrderFood(StatesGroup):
#     wait_for_food = State()
#     wait_for_size = State()


# @dp.message_handler(commands=['start'])
# async def start(message: types.Message):
#     await bot.send_message(message.chat.id, 'Любое сообщение')


# @dp.message_handler(commands=['food'], state='*')
# async def food_step1(message: types.Message):
#     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     for name in available_fn:
#         keyboard.add(name)
#     await message.answer('Выберите блюдо', reply_markup=keyboard)
#     await OrderFood.wait_for_food.set()


# @dp.message_handler(state=OrderFood.wait_for_food, content_types=ContentTypes.TEXT)
# async def food_step2(message: types.Message, state: FSMContext):
#     if message.text.lower() not in available_fn:
#         await message.reply('Пожалуйста, выберите блюдо на клавиатуре')
#         return
#     await state.update_data(chosen_food=message.text.lower())

#     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     for size in available_sizes:
#         keyboard.add(size)
#     await OrderFood.next()
#     await message.answer('Теперь выберите размер порции', reply_markup=keyboard)


# @dp.message_handler(state=OrderFood.wait_for_size, content_types=types.ContentTypes.TEXT)
# async def food_step3(message: types.Message, state: FSMContext):
#     if message.text.lower() not in available_sizes:
#         await message.answer('Выбери размер порции на клавиатуре')
#         return
#     user_data = await state.get_data()
#     await bot.send_message(message.chat.id, f'Вы заказали {message.text.lower()}, размер порции - {user_data["chosen_food"]}\n')
#     await state.finish()

# executor.start_polling(dp, skip_updates=True)

import logging

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor

logging.basicConfig(level=logging.INFO)

API_TOKEN = '1102746633:AAH2i3PRyzXa4AzKNzzoQgM8P20gLmXK4e8'


bot = Bot(token=API_TOKEN)

# For example use simple MemoryStorage for Dispatcher.
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# States
class Form(StatesGroup):
    name = State()  # Will be represented in storage as 'Form:name'
    age = State()  # Will be represented in storage as 'Form:age'
    gender = State()  # Will be represented in storage as 'Form:gender'


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    """
    Conversation's entry point
    """
    # Set state
    await Form.name.set()

    await message.reply("Hi there! What's your name?")


# You can use state '*' if you need to handle all states
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    """
    Process user name
    """
    async with state.proxy() as data:
        data['name'] = message.text

    await Form.next()
    await message.reply("How old are you?")


# Check age. Age gotta be digit
@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.age)
async def process_age_invalid(message: types.Message):
    """
    If age is invalid
    """
    return await message.reply("Age gotta be a number.\nHow old are you? (digits only)")


@dp.message_handler(lambda message: message.text.isdigit(), state=Form.age)
async def process_age(message: types.Message, state: FSMContext):
    # Update state and data
    await Form.next()
    await state.update_data(age=int(message.text))

    # Configure ReplyKeyboardMarkup
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("Male", "Female")
    markup.add("Other")

    await message.reply("What is your gender?", reply_markup=markup)


@dp.message_handler(lambda message: message.text not in ["Male", "Female", "Other"], state=Form.gender)
async def process_gender_invalid(message: types.Message):
    """
    In this example gender has to be one of: Male, Female, Other.
    """
    return await message.reply("Bad gender name. Choose your gender from the keyboard.")


@dp.message_handler(state=Form.gender)
async def process_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['gender'] = message.text

        # Remove keyboard
        markup = types.ReplyKeyboardRemove()

        # And send message
        await bot.send_message(
            message.chat.id,
            md.text(
                md.text('Hi! Nice to meet you,', md.bold(data['name'])),
                md.text('Age:', md.code(data['age'])),
                md.text('Gender:', data['gender']),
                sep='\n',
            ),
            reply_markup=markup,
            parse_mode=ParseMode.MARKDOWN,
        )

    # Finish conversation
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
