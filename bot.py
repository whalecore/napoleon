import time
import logging
from aiogram.dispatcher import storage
from aiogram.types import message
from aiogram.types.message import ContentTypes
from aiogram.types.reply_keyboard import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode, InputMediaAudio
from aiogram.utils import executor
from aiogram.utils.markdown import text

from parser import search_wiki
from aiohttp.helpers import current_task

import requests
from functions import hi_pitch, low_pitch
from io import BufferedWriter

import random
import string
import os

logging.basicConfig(level=logging.DEBUG)

BOT_TOKEN = os.environ['TOKEN']

bot = Bot(token=BOT_TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# states


class Form(StatesGroup):
    wiki = State()
    voice = State()
    voice_hi = State()
    voice_low = State()
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
    buttons = ['Высокий', 'Низкий', 'Отмена']
    for button in buttons:
        keyboard.add(button)
    await bot.send_message(
        message.chat.id,
        'Выберите тембр, в который мне нужно преобразовать ваш голос.',
        reply_markup=keyboard
    )


@dp.message_handler(state='*', text=['Отмена'])
async def cancel(message: types.Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    btns = ["Вики", "Тембр голоса", "Фото"]
    for btn in btns:
        keyboard.add(btn)
    await state.finish()
    await bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEBdwZfioz_Q2I_fVq77fJlMezQWO7IYAAC2gcAAmMr4gmP2IPUry3pGhsE')
    await bot.send_message(message.chat.id, 'Ваше действие отменено, mon ami.', reply_markup=keyboard)


@dp.message_handler(state=Form.voice, text=['Высокий'])
async def get_voice(message: types.Message, state: FSMContext):
    await Form.voice_hi.set()
    await bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEBdzZfiq_jEecS7wNcCWhIMbmplm1kSQAC4QcAAmMr4gnzHOpFutpxDxsE')
    await bot.send_message(
        message.chat.id,
        "Прошу вас записать мне голосовое сообщение, mon ami!"
    )


@dp.message_handler(state=Form.voice_hi, content_types=ContentTypes.VOICE)
async def high(message: types.Message, state: FSMContext):
    await bot.send_message(
        message.chat.id,
        'Получите, распишитесь!'
    )
    await Form.voice.set()

    file_info = await bot.get_file(message.voice.file_id)
    random_name = ''.join(random.choice(string.ascii_lowercase)
                          for i in range(8)) + '.ogg'
    await bot.download_file(file_info.file_path, random_name)
    hp_file = hi_pitch(random_name)
    await bot.send_audio(message.chat.id, audio=open(hp_file, 'rb'))
    os.remove(random_name)
    os.remove(hp_file)


@dp.message_handler(state=Form.voice, text=['Низкий'])
async def get_voice(message: types.Message, state: FSMContext):
    await Form.voice_low.set()
    await bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEBdzZfiq_jEecS7wNcCWhIMbmplm1kSQAC4QcAAmMr4gnzHOpFutpxDxsE')
    await bot.send_message(
        message.chat.id,
        "Прошу вас записать мне голосовое сообщение, mon ami!"
    )


@dp.message_handler(state=Form.voice_low, content_types=ContentTypes.VOICE)
async def high(message: types.Message, state: FSMContext):
    await bot.send_message(
        message.chat.id,
        'Получите, распишитесь!'
    )
    await Form.voice.set()

    file_info = await bot.get_file(message.voice.file_id)
    random_name = ''.join(random.choice(string.ascii_lowercase)
                          for i in range(8)) + '.ogg'
    await bot.download_file(file_info.file_path, random_name)
    hp_file = low_pitch(random_name)
    await bot.send_audio(message.chat.id, audio=open(hp_file, 'rb'))
    os.remove(random_name)
    os.remove(hp_file)


@dp.message_handler(state="*", text=['Фото'])
async def photo(message: types.Message):
    await bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEBdrxfigFLzdXbHhCGk00WOF_AdKQlqwAC3QcAAmMr4glNJX_q7yBeaxsE')
    await bot.send_message(
        message.chat.id,
        "Увы, monsiuer/madam, данная функция все еще в разработке."
    )


executor.start_polling(dp, skip_updates=True)
