# import random
# from string import ascii_lowercase
# from aiogram import Bot, Dispatcher, executor, types
# # from aiogram.dispatcher import FSMContext
# # from aiogram.dispatcher.filters.state import State, StatesGroup
# import logging
# import time
# import requests
# import aiogram.utils.markdown as md
# from aiogram.dispatcher import FSMContext


# from aiogram.types.message import ContentTypes

# from functions import hi_pitch, low_pitch, remove_all_oggs
# from parser import search_wiki

# BOT_TOKEN = '1252484349:AAGC4t5-PzwZq-0Q56mOxfduGfcZamDSWDo'

# bot = Bot(token=BOT_TOKEN)
# dp = Dispatcher(bot)

# logging.basicConfig(level=logging.DEBUG)

# keyboard = types.ReplyKeyboardMarkup(
#     resize_keyboard=True, one_time_keyboard=False)
# person_btn = types.KeyboardButton('Получить инфо из Википедии')
# voice = types.KeyboardButton('Преобразовать голос')
# face = types.KeyboardButton('Распознавание лиц (в разработке)')
# keyboard.add(person_btn, voice, face)


# # class MakeWikiRequest(StatesGroup):
# #     waiting_for_request = State()
# #     waiting_for_audio = State()
# #     inactive = State()


# @dp.message_handler(commands=['start'])
# async def start(message: types.Message):
#     await message.answer('Привет! Я чат-бот Наполеон. Клавиатура для использования доступна ниже: \
#     Мои функции: \n\n \
#     1. Поиск по Википедии \n \
#     2. Изменение тембра голоса \n \
#     3. Распознавание лица по фото', reply_markup=keyboard)


# @dp.message_handler(text=['Получить инфо из Википедии'], state="*")
# async def wiki(message: types.Message):
#     await bot.send_message(message.chat.id, "Напишите, что мне поискать")
#     # await MakeWikiRequest.waiting_for_request.set()

#     @dp.message_handler(content_types=ContentTypes.TEXT)
#     async def send_wiki(message: types.Message):
#         # await state.update_data(message=message.text)
#         links = search_wiki(message.text)
#         counter = 0
#         for k, v in links.items():
#             if counter == 3:
#                 # await state.finish()
#                 break
#             else:
#                 formatted_string = '<strong>' + k + '</strong>' + '\n\n' + v
#                 await bot.send_message(message.chat.id, formatted_string, parse_mode='HTML')
#                 counter += 1
#                 time.sleep(1)


# @dp.message_handler(text=['Преобразовать голос'])
# async def voice_file(message: types.Audio):
#     # voice_file = message.file_id
#     keyboard = types.ReplyKeyboardMarkup(
#         resize_keyboard=True, one_time_keyboard=False)
#     hi = types.KeyboardButton('Высокий тембр')
#     low = types.KeyboardButton('Низкий тембр')
#     keyboard.add(hi, low)
#     await bot.send_message(message.chat.id, 'Выберите тембр и запишите аудио', reply_markup=keyboard)

#     @dp.message_handler(text=['Высокий тембр'])
#     async def high(message: types.Message.voice):
#         voice_file = message.file_id
#         url = 'https://api.telegram.org/file/bot{}/{}'.format(
#             BOT_TOKEN, voice_file)
#         r = requests.get(url)
#         random_filename = ''.join(random.choice(
#             ascii_lowercase) for i in range(8))
#         with open(random_filename, 'wb') as audiofile:
#             audiofile.write(r.content)
#         hi = hi_pitch(random_filename)
#         await bot.send_file(message.chat.id, voice=hi)

# executor.start_polling(dp, skip_updates=True)

import logging
from aiogram.dispatcher import storage
from aiogram.types import message
from aiogram.types.message import ContentTypes
from aiogram.types.reply_keyboard import ReplyKeyboardMarkup

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram.utils.markdown import text

from parser import search_wiki

import requests
from functions import hi_pitch, low_pitch

logging.basicConfig(level=logging.DEBUG)

BOT_TOKEN = '1102746633:AAH2i3PRyzXa4AzKNzzoQgM8P20gLmXK4e8'

bot = Bot(token=BOT_TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# states


class Form(StatesGroup):
    wiki = State()
    voice = State()
    image = State()


@dp.message_handler(commands='start')
async def start_cmd(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=False)
    buttons = ['Вики', 'Тембр голоса', 'Фото']
    for button in buttons:
        keyboard.add(button)
    await bot.send_sticker(message.chat.id, sticker='CAACAgIAAxkBAAEBdq5fifgIYgtIeZqJcebZKqJZDXmndwAC0gcAAmMr4gnJXh1bpcCgaxsE')
    await bot.send_message(
        message.chat.id,
        md.text(
            md.text("Bonjour! Я - бот ", md.bold("Наполеон!")),
            md.text('Я умею искать нужные тебе статьи в Википедии,'),
            md.text('менять тембр твоего голоса и искать информацию по фото!'),
            md.text('Просто воспользуйся клавиатурой и следуй подсказкам!'),
            sep='\n'
        ),
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN,
    )


@dp.message_handler(state='*', text=['Вики'])
async def wiki_request(message: types.Message):
    await Form.wiki.set()
    await bot.send_message(
        message.chat.id,
        'Введите название статьи для поиска'
    )


@dp.message_handler(state=Form.wiki)
async def send_wiki_article(message: types.Message, state: FSMContext):
    await bot.send_message(
        message.chat.id,
        'Нашел для вас следующую, наиболее релевантную статью:'
    )
    await state.finish()

    links = search_wiki(message.text)
    await bot.send_sticker(message.chat.id, sticker='CAACAgIAAxkBAAEBdr5figFZdToMHNEvHCgS-oQk010d3gAC0AcAAmMr4glCITo69YshNhsE')
    await bot.send_message(
        message.chat.id,
        md.link(title=links[0]['search_title'],
                url=links[0]['search_link']),
        parse_mode=ParseMode.MARKDOWN,
    )


@dp.message_handler(state='*', text='Тембр голоса')
async def voice_pitch(message: types.Message, state: FSMContext):
    await Form.voice.set()
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=False)
    buttons = ['Высокий', 'Низкий']
    for button in buttons:
        keyboard.add(button)
    await bot.send_message(
        message.chat.id,
        'Выберите тембр, в который мне нужно преобразовать ваш голос.',
        reply_markup=keyboard
    )


@dp.message_handler(state=Form.voice, text=['Высокий'])
async def get_voice(message: types.Message, state: FSMContext):
    await bot.send_message(
        message.chat.id,
        "А теперь отправьте мне голосовое сообщение."
    )


@dp.message_handler(state=Form.voice, content_types=ContentTypes.VOICE)
async def high(message: types.Message, state: FSMContext):
    await bot.send_message(
        message.chat.id,
        'Получите, распишитесь!'
    )
    await state.finish()

    file_info = await bot.get_file(message.voice.file_id)
    downloaded_file = await bot.download_file(file_info.file_path, 'test.ogg')
    hp_file = await hi_pitch(downloaded_file)
    await bot.send_audio(message.chat.id, hp_file)

executor.start_polling(dp, skip_updates=True)
