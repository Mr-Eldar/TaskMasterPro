from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command, StateFilter

from app.database.requests import *
import app.keyboards as kb
import app.states as st
from app.generators import text_generation

user = Router()


@user.message(Command('start'))
async def cmd_start(message: Message):
    await message.answer('🚀 Добро пожаловать в <b>TaskMaster Pro</b> — твой умный помощник для управления задачами!\n\n'
                        '✨ <b>Что ты можешь сделать?</b>\n'
                        '✔️ Создавать и редактировать задачи\n'
                        '✔️ Отмечать выполнение одним кликом\n'
                        '✔️ Получать напоминания и аналитику\n\n'
                        '📌 Начни прямо сейчас — просто напиши нажми кнопку ниже!\n\n'
                        '🤖 <b>Скоро здесь появится ещё больше крутых функций...</b>', reply_markup=kb.start_kb, parse_mode=ParseMode.HTML)
    await set_user(message.from_user.id)


@user.message(Command('menu'))
async def cmd_menu(message: Message):
    await message.answer('📌 <b>Главное меню TaskMaster Pro</b>\n\n'
                        'Здесь всё, что нужно для управления задачами:\n\n'
                        '✅ <b>/tasks</b> — открыть список задач\n'
                        '📋 <b>/chat</b> — открыть чат с ИИ\n'
                        '🔄 <b>/task_managment</b> — управление задачами\n\n'
                        '💡 Быстрый доступ к функциям — выбирай действие!\n\n'
                        '<b>Используй кнопки ниже или вводи команды вручную</b>', reply_markup=kb.start_kb, parse_mode=ParseMode.HTML)


@user.message(Command('chat'))
@user.message(F.text == 'ИИ 💬')
async def cmd_ii_chat(message: Message, state: FSMContext):
    await state.set_state(st.Gen.startChat)
    await message.answer('🤖 <b>Диалог с ИИ</b>\n'
                        'Задавай любые вопросы: от погоды до программирования, от рецептов до советов'
                        'ИИ постарается помочь тебе максимально точно и понятно.\n\n'
                        '💬 <b>Просто начни писать — ИИ ответит!</b>', reply_markup=kb.stop_chat, parse_mode=ParseMode.HTML)


@user.message(F.text == 'Закончить диалог ❌')
async def stop_chat(message: Message, state: FSMContext):
    await message.answer('Диалог был закончен ✅')
    await state.clear()


@user.message(StateFilter(st.Gen.startChat))
async def generating(message: Message, state: FSMContext):
    await state.set_state(st.Gen.wait)
    response = await text_generation(message.text)
    await message.answer(response, parse_mode=ParseMode.MARKDOWN)
    await state.set_state(st.Gen.startChat)


@user.message(StateFilter(st.Gen.wait))
async def waiting_text_generation(message: Message):
    await message.answer('Подождите, ваш запрос обрабатывается ⌛️')


@user.message(Command('tasks'))
@user.message(F.text == 'Задачи 📝')
@user.callback_query(F.data == 'categories')
async def cmd_tasks(event: Message | CallbackQuery):
    if isinstance(event, Message):
        user_id = await get_user_id_by_tg_id(event.from_user.id)

        if user_id is None:
            await event.answer("❗️Ошибка: пользователь не найден в базе.")
            return
        await event.answer_sticker(sticker='CAACAgUAAxkBAAEPAZJogUkSBVK_3SoQIsgrQZS5V3ugswACHQ0AAsWB2VXEazw9gagmazYE')
        await event.answer('📋 Ваши текущие задачи\n\n'
                        'Здесь отображается полный список активных задач. Для управления используйте соответствующие команды.\n\n'
                        'ℹ️ <i>Чтобы добавить, изменить или удалить задачу — воспользуйтесь командой <b>Упарвление задачами</b> или <b>/task_management:</b></i>.',
                        reply_markup=await kb.tasks(user_id), parse_mode=ParseMode.HTML)
    else:
        user_id = await get_user_id_by_tg_id(event.from_user.id)

        if user_id is None:
            await event.answer("❗️Ошибка: пользователь не найден в базе.")
            return
        await event.answer()
        await event.message.edit_text('<b>📋 Ваши текущие задачи</b>\n\n'
                        'Здесь отображается полный список активных задач. Для управления используйте соответствующие команды.\n\n'
                        'ℹ️ <i>Чтобы добавить, изменить или удалить задачу — воспользуйтесь командой <b>Упарвление задачами</b> или <b>/task_management:</b></i>.',
                        reply_markup=await kb.tasks(user_id), parse_mode=ParseMode.HTML)


@user.message(Command('task_management'))
@user.message(F.text == 'Управление задачами ⚙️')
async def cmd_tasks_management(message: Message):
    await message.answer_sticker(sticker='CAACAgUAAxkBAAEPAZBogUHWO-e8KEIvyze7UBcvq9xVmAAChg0AAizm0VTVsAdI2XV_6DYE')
    await message.answer('🎯 <b>Управление задачами и планами</b>\n\n'
                        'Здесь вы можете полностью контролировать свои задачи и ежедневные планы.\n\n'
                        '🔹 <b>Добавление</b>\n'
                        'Задача — долгосрочная цель (например, "Изучить TypeScript")\n'
                        'План — конкретное действие на день (например, "Практика типов с 10:00 до 12:00")\n\n'
                        '🔹 <b>Изменение</b>\n'
                        'Редактируйте название, сроки, приоритет\n'
                        'Переносите, разбивайте на этапы\n\n'
                        '🔹 <b>Удаление</b>\n'
                        'Уберите ненужные или выполненные пункты\n\n'
                        '<b>Выберите действие ниже:</b>',
                        reply_markup=kb.tasks_management_kb, parse_mode=ParseMode.HTML)


@user.callback_query(F.data.startswith('work_task_'))
async def cmd_get_work_tasks(callback: CallbackQuery):
    task_id = int(callback.data.split('_')[2])
    await callback.answer('')
    await callback.message.delete()
    await callback.message.answer('📅 <b>Планы на сегодня</b>\n\n'
                                        'Здесь отображаются все ваши запланированные дела на текущий день.\n'
                                        'Чтобы добавить или изменить планы, используйте команду <b>/task_management</b>.',
                                reply_markup=await kb.tasks_item(task_id, page=1), parse_mode=ParseMode.HTML)


@user.callback_query(F.data.startswith('task_item_'))
async def cmd_get_task_item_info(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.delete()

    parts = callback.data.split('_')
    category_id = int(parts[2])
    item_id = int(parts[3])

    task_item = await get_task_item_info(item_id)

    if task_item.status == True:
        await callback.message.answer_photo(photo=task_item.photo,
                                            caption=f'Название: {task_item.name}\n\n'
                                                    f'{task_item.description}',
                                            reply_markup=await kb.task_item_buttons_complete(item_id, category_id))
    else:
        await callback.message.answer_photo(photo=task_item.photo,
                                            caption=f'Название: {task_item.name}\n\n'
                                                    f'{task_item.description}',
                                            reply_markup=await kb.task_item_buttons(item_id, category_id))


@user.callback_query(F.data.startswith('set_status_'))
async def cmd_set_status(callback: CallbackQuery):
    await callback.answer('')
    task_id = int(callback.data.split('_')[2])
    category_id = int(callback.data.split('_')[-1])
    await set_status(task_id)
    info = await get_task_item_info(task_id)

    if info.status == True:
        await callback.message.edit_reply_markup(reply_markup=await kb.task_item_buttons_complete(task_id, category_id))
    else:
        await callback.message.edit_reply_markup(reply_markup=await kb.task_item_buttons(task_id, category_id))


@user.callback_query(F.data.startswith("page:"))
async def cmd_paginate_tasks(callback: CallbackQuery):
    _, category_id, page = callback.data.split(":")
    markup = await kb.tasks_item(int(category_id), int(page))
    await callback.message.edit_reply_markup(reply_markup=markup)
    await callback.answer()