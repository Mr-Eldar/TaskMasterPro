from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from app.states import AiChat, WaitGenerator
from app.generators import text_generator

ai = Router()


@ai.message(Command('ai_chat'))
async def start_chat(message: Message, state: FSMContext):
    await message.answer('Привет напиши код.')
    await state.set_state(AiChat.start_chat)


@ai.message(Command('stop_ai'))
async def stop_chat(message: Message, state: FSMContext):
    await state.clear()


@ai.message(F.text, StateFilter(AiChat.start_chat))
async def chatting(message: Message, state: FSMContext):
    await state.set_state(WaitGenerator.wait_generator)
    response = await text_generator(prompt=message.text)
    await message.answer(response, parse_mode=ParseMode.MARKDOWN)


@ai.message(WaitGenerator.wait_generator)
async def chatting_wait(message: Message, state: FSMContext):
    await message.answer('Подождите ваш запрос обрабатывается.')