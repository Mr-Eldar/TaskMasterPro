from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

ai = Router()

@ai.message(Command('ai_chat'))
async def start_chat(message: Message):
    await message.answer('Привет напиши код.')
