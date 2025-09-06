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
    await message.answer('Привет! Напиши код. Для выхода используй /stop_ai')
    await state.set_state(AiChat.start_chat)


@ai.message(Command('stop_ai'))
async def stop_chat(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Чат с ИИ завершен.')


@ai.message(AiChat.start_chat)
async def chatting(message: Message, state: FSMContext):
    # Получаем текущую историю или создаем новую
    data = await state.get_data()
    history = data.get('chat_history', [])
    
    # Добавляем сообщение пользователя в историю
    history.append(f"User: {message.text}")
    
    await state.set_state(WaitGenerator.wait_generator)
    processing_msg = await message.answer('Ваш запрос обрабатывается...')
    
    try:
        # Передаем всю историю для контекста
        full_prompt = "\n".join(history)
        response = await text_generator(prompt=full_prompt)
        
        # Добавляем ответ ИИ в историю
        history.append(f"AI: {response}")
        
        # Сохраняем обновленную историю
        await state.update_data(chat_history=history[-10:])  # храним последние 10 сообщений
        
        await message.answer(response, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        await message.answer(f'Произошла ошибка: {str(e)}')
    
    finally:
        await processing_msg.delete()
        await state.set_state(AiChat.start_chat)


@ai.message(WaitGenerator.wait_generator)
async def chatting_wait(message: Message, state: FSMContext):
    await message.answer('Подождите, ваш предыдущий запрос еще обрабатывается.')