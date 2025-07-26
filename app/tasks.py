import asyncio

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from app.user import cmd_tasks_management
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest

from app.database.requests import *
import app.keyboards as kb
import app.states as st

tasks = Router()


async def delete_last_messages(bot: Message.bot, chat_id: int, from_message_id: int, count: int):
    for i in range(count):
        msg_id = from_message_id - i
        try:
            await bot.delete_message(chat_id=chat_id, message_id=msg_id)
        except TelegramBadRequest as e:
            pass
        except Exception as e:
            # Ловим другие ошибки
            print(f"❌ Ошибка при удалении message_id={msg_id}: {e}")


@tasks.callback_query(F.data == 'add_work_task')
async def cmd_add_new_category_process(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('➕ Добавь новую задачу в список дел!\n'
                                     'Укажи цель, которую хочешь достичь — и <b>начни путь к результату</b> 📝🚀', parse_mode=ParseMode.HTML)
    await state.set_state(st.AddNewCategory.name)


@tasks.callback_query(F.data == 'add_work_task_item')
async def cmd_add_plan_process(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Выберите задачу в которую хотите добавить план 🚀',
                                     reply_markup=await kb.select_tasks(callback.from_user.id))
    await state.set_state(st.AddNewCategoryPlan.category)


@tasks.callback_query(F.data == 'edit_work_task')
async def cmd_edit_work_task(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text('♻️ <b>Передумал? Меняем!</b>\n'
                                     'Эта команда поможет тебе ✍️ переименовать задачу или ✏️ подправить описание, если что-то изменилось.\n\n'
                                     'Просто укажи 🆔 ID задачи — и вперёд!', reply_markup=await kb.select_tasks(callback.from_user.id), parse_mode=ParseMode.HTML)
    await state.set_state(st.EditWorkTask.category)


@tasks.callback_query(F.data == 'edit_work_task_item')
async def cmd_edit_task_item(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text('♻️ <b>Передумал? Меняем!</b>\n'
                                     'Эта команда поможет тебе ✍️ переименовать план или ✏️ подправить имя, описание или картинку если что-то изменилось.\n\n'
                                     'Просто укажи 🆔 ID задачи — и вперёд!', reply_markup=await kb.select_tasks(callback.from_user.id), parse_mode=ParseMode.HTML)
    await state.set_state(st.EditTaskItem.category)


@tasks.callback_query(F.data == 'remove_work_task')
async def cmd_delete_work_task_item(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text('🗂 Завершил задачу? Смело удаляй и двигайся дальше 🚀✅\n\n', reply_markup=await kb.select_tasks(callback.from_user.id))
    await state.set_state(st.DeleteWorkTasks.category)


@tasks.callback_query(F.data == 'remove_work_task_item')
async def cmd_delete_work_task_item(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text('🗂 Завершил план? Смело удаляй и двигайся дальше 🚀✅\n\n'
                                     'Для начала выбери категорию из которой хочешь удалить план 👇',
                                     reply_markup=await kb.select_tasks(callback.from_user.id))
    await state.set_state(st.DeleteTaskItem.category)


@tasks.callback_query(F.data.startswith('select_tasks_'), st.DeleteWorkTasks.category)
async def cmd_delete_process(callback: CallbackQuery, state: FSMContext):
    callbackData = callback.data.split('_')[-1]
    await state.update_data(category=callbackData)
    await callback.message.edit_text(f'Вы точно уверены в том что хотите удалить категорию безвозратно ⁉️',
                                     reply_markup=kb.yes_or_no_kb)
    await state.set_state(st.DeleteWorkTasks.hisUnderstand)


@tasks.callback_query(F.data.startswith('select_tasks_'), st.DeleteTaskItem.category)
async def cmd_delete_process(callback: CallbackQuery, state: FSMContext):
    callbackData = callback.data.split('_')[-1]
    await state.update_data(category=callbackData)
    await callback.message.edit_text(f'Теперь выберите план из этой категории который хотите удалить 👇',
                                     reply_markup=await kb.select_tasks_item(callbackData))
    await state.set_state(st.DeleteTaskItem.plan)


@tasks.callback_query(F.data.startswith('select_tasks_item_'), st.DeleteTaskItem.plan)
async def cmd_delete_plan_process(callback: CallbackQuery, state: FSMContext):
    callbackData = callback.data.split('_')[-1]
    await state.update_data(plan=callbackData)
    await callback.message.edit_text(f'Вы точно уверены в том что хотите удалить план безвозратно ⁉️',
                                     reply_markup=kb.yes_or_no_kb)
    await state.set_state(st.DeleteTaskItem.hisUnderstand)


@tasks.callback_query(F.data.startswith('select_tasks_'), st.AddNewCategoryPlan.category)
async def cmd_select_tasks_process(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    category = int(callback.data.split('_')[-1])
    await state.update_data(category=category)
    await callback.message.edit_text('⏰ Запланируй, что и когда ты сделаешь\n'
                                     'Маленький шаг сегодня — <b>большой результат завтра</b> 🚀\n\n'
                                     'Добавьте название для вашего плана 📝', parse_mode=ParseMode.HTML)
    await state.set_state(st.AddNewCategoryPlan.name)


@tasks.callback_query(F.data.startswith('select_tasks_'), st.EditWorkTask.category)
async def cmd_edit_task_process(callback: CallbackQuery, state: FSMContext):
    callbackData = callback.data.split('_')[-1]
    await state.update_data(category=callbackData)
    await callback.message.edit_text(f'🆕 Как назовём задачу теперь?\n'
                                     f'Напиши новое имя для выбранной задачи 📝\n'
                                     f'Можно использовать эмодзи и до 50 символов.')
    await state.set_state(st.EditWorkTask.new_name)


@tasks.callback_query(F.data.startswith('select_tasks_'), st.EditTaskItem.category)
async def cmd_edit_task_item_process(callback: CallbackQuery, state: FSMContext):
    callbackData = callback.data.split('_')[-1]
    await state.update_data(category=callbackData)
    await callback.message.edit_text('Теперь выберите план из этой категории который хотите изменить 👇',
                                     reply_markup=await kb.select_tasks_item(callbackData))
    await state.set_state(st.EditTaskItem.plan)


@tasks.callback_query(F.data.startswith('select_tasks_item_'), st.EditTaskItem.plan)
async def cmd_edit_plan_process(callback: CallbackQuery, state: FSMContext):
    callbackData = callback.data.split('_')[-1]
    await state.update_data(plan=callbackData)
    await callback.message.edit_text(f'Теперь выберите пункт который хотите изменить 👇',
                                     reply_markup=kb.pick_tools_kb)
    await state.set_state(st.EditTaskItem.new_info)


@tasks.message(st.AddNewCategory.name)
async def cmd_add_precess(message: Message, state: FSMContext):
    await set_user(message.from_user.id)
    await state.update_data(name=message.text)
    data = await state.get_data()
    await add_work_task(data['name'], message.from_user.id)
    await message.answer('🎯 Отлично! Ты только что задал себе новую цель\n'
                         'Сделай её достижимой — шаг за шагом 🔥')
    await asyncio.sleep(1)
    await cmd_tasks_management(message)


@tasks.message(st.AddNewCategoryPlan.name)
async def cmd_add_plan_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('🧠 Опишите свой шаг или действие на день\n'
                         'Это поможет понять, зачем нужен этот план и что он даёт 🎯')
    await state.set_state(st.AddNewCategoryPlan.description)


@tasks.message(st.AddNewCategoryPlan.description)
async def cmd_add_plan_desc(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer('📸 Отправь изображение, которое относится к твоему плану или задаче\n'
                         'Это может быть фото, скриншот или вдохновляющая картинка ✨')
    await state.set_state(st.AddNewCategoryPlan.photo)


@tasks.message(st.AddNewCategoryPlan.photo)
async def cmd_add_plan(message: Message, state: FSMContext):
    await set_user(message.from_user.id)
    if not message.photo:
        await message.answer('Извините но мне нужно чтобы вы отправили фото 🖼')
        return
    await state.update_data(photo=message.photo[-1].file_id)
    data = await state.get_data()
    await add_task_item(data['category'], data['name'], data['description'], data['photo'])
    await message.answer('✅ План добавлен!\n'
                         'Шаг к цели записан — осталось только выполнить 💪')
    await state.clear()
    await asyncio.sleep(1)
    await cmd_tasks_management(message)


@tasks.message(st.EditWorkTask.new_name)
async def cmd_edit_task_name(message: Message, state: FSMContext):
    if len(message.text) > 50:
        await message.answer('Количество символов не дожно превышать 50 ❌\n\n'
                             'Попробуйте еще раз 🔄')
        return
    await state.update_data(new_name=message.text)
    await message.answer('Вы точно уверены в том что хотите переименовать задачу ⁉️', reply_markup=kb.yes_or_no_kb)
    await state.set_state(st.EditWorkTask.hisUnderstand)


@tasks.callback_query(F.data.startswith('rename_'), st.EditTaskItem.new_info)
async def cmd_edit_task_info(callback: CallbackQuery, state: FSMContext):
    callbackData = callback.data.split('_')[-1]
    await state.update_data(pick_tools=callbackData)
    if callbackData == 'name':
        await callback.message.edit_text('Теперь введите новое имя для вашего пункта ✏️')
    if callbackData == 'desc':
        await callback.message.edit_text('Теперь введите новое описание для вашего пункта ✏️')
    await state.set_state(st.EditTaskItem.hisUnderstand)


@tasks.callback_query(st.DeleteWorkTasks.hisUnderstand)
async def cmd_delete_process(callback: CallbackQuery, state: FSMContext):
    await set_user(message.from_user.id)
    data = await state.get_data()

    if callback.data == 'yes':
        await callback.answer('Задача была успешно удалена 🎉')
        await delete_work_task(data['category'])
    elif callback.data == 'no':
        await callback.answer('Действие было отменено ❌')
    await delete_last_messages(
        bot=callback.message.bot,
        chat_id=callback.message.chat.id,
        from_message_id=callback.message.message_id,
        count=2
    )

    await state.clear()
    await cmd_tasks_management(callback.message)


@tasks.callback_query(st.DeleteTaskItem.hisUnderstand)
async def cmd_delete_process(callback: CallbackQuery, state: FSMContext):
    await set_user(message.from_user.id)
    data = await state.get_data()

    if callback.data == 'yes':
        await callback.answer('План был успешно удалена 🎉')
        await delete_task_item(data['category'])
    elif callback.data == 'no':
        await callback.answer('Действие было отменено ❌')
    await delete_last_messages(
        bot=callback.message.bot,
        chat_id=callback.message.chat.id,
        from_message_id=callback.message.message_id,
        count=2
    )

    await state.clear()
    await cmd_tasks_management(callback.message)


@tasks.callback_query(st.EditWorkTask.hisUnderstand)
async def cmd_edit_process(callback: CallbackQuery, state: FSMContext):
    await set_user(message.from_user.id)
    data = await state.get_data()

    if callback.data == 'yes':
        await callback.answer('Задача была успешно переименована 🎉')
        await rename_work_task(data['category'], data['new_name'])
    elif callback.data == 'no':
        await callback.answer('Действие было отменено ❌')
    await delete_last_messages(
        bot=callback.message.bot,
        chat_id=callback.message.chat.id,
        from_message_id=callback.message.message_id,
        count=4
    )

    await state.clear()
    await cmd_tasks_management(callback.message)


@tasks.message(st.EditTaskItem.hisUnderstand)
async def cmd_edit_task_process(message: Message, state: FSMContext):
    await state.update_data(new_info=message.text)
    await message.answer(f'Вы точно уверены в том что хотите изменить план ⁉️',
                                     reply_markup=kb.yes_or_no_kb)
    await state.set_state(st.EditTaskItem.final)


@tasks.callback_query(st.EditTaskItem.final)
async def cmd_edit_task_process(callback: CallbackQuery, state: FSMContext):
    await set_user(callback.from_user.id)
    data = await state.get_data()
    await callback.answer()

    if callback.data == 'yes':
        if data['pick_tools'] == 'name':
            await update_work_task_item(data['plan'], new_name=data['new_info'])
        elif data['pick_tools'] == 'desc':
            await update_work_task_item(data['plan'], new_description=data['new_info'])
        await callback.answer('План был успешно успешно изменен🎉')
    elif callback.data == 'no':
        await callback.answer('Действие было отменено ❌')
    await asyncio.sleep(0.5)

    await delete_last_messages(
        bot=callback.message.bot,
        chat_id=callback.message.chat.id,
        from_message_id=callback.message.message_id,
        count=4
    )

    await state.clear()
    await cmd_tasks_management(callback.message)


@tasks.callback_query(F.data == 'back_now')
async def back_now(callback: CallbackQuery):
    await callback.answer('Действие было отменено ❌')
    await delete_last_messages(
        bot=callback.message.bot,
        chat_id=callback.message.chat.id,
        from_message_id=callback.message.message_id,
        count=2
    )
    await cmd_tasks_management(callback.message)