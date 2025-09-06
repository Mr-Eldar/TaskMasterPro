import math

from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from app.database.requests import *

ITEM_PER_PAGE = 6

start_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, keyboard=[
    [KeyboardButton(text='Задачи 📝'), KeyboardButton(text='чат с ИИ 💬')],
    [KeyboardButton(text='Управление планами ⚙️')]
])

tasks_management_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить План ➕', callback_data='add_work_task'),
     InlineKeyboardButton(text='Добавить Задачу ➕', callback_data='add_work_task_item')],
    [InlineKeyboardButton(text='Изменить План ✏️', callback_data='edit_work_task'),
     InlineKeyboardButton(text='Изменить Задачу ✏️', callback_data='edit_work_task_item')],
    [InlineKeyboardButton(text='Удалить План ❌', callback_data='remove_work_task'),
     InlineKeyboardButton(text='Удалить Задачу ❌', callback_data='remove_work_task_item')]
])

pick_tools_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Имя ⭐️', callback_data='rename_name')],
    [InlineKeyboardButton(text='Описание 📝', callback_data='rename_desc')],
])

yes_or_no_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Точно ✅', callback_data='yes'),
     InlineKeyboardButton(text='Я передумал(-а) ❌', callback_data='no')]
])

stop_chat = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, keyboard=[
    [KeyboardButton(text='Закончить диалог ❌')]
])


async def task_item_buttons(task_id, category_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Не выполненно ❌', callback_data=f'set_status_{task_id}_{category_id}')],
        [InlineKeyboardButton(text='🔙 Назад', callback_data=f'work_task_{category_id}')],
    ])


async def task_item_buttons_complete(task_id, category_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Выполненно ✅', callback_data=f'set_status_{task_id}_{category_id}')],
        [InlineKeyboardButton(text='🔙 Назад', callback_data=f'work_task_{category_id}')],
    ])


async def tasks(user_id):
    keyboard = InlineKeyboardBuilder()
    work_tasks = await get_work_tasks(user_id)
    print(work_tasks)

    if not work_tasks:
        keyboard.add(
            InlineKeyboardButton(
                text="Нет планов 😔",
                callback_data="no_tasks"
            )
        )
    else:
        for work_task in work_tasks:
            items = list(await get_wt_items_by_id(work_task.id))
            total = len(items)
            completed = len([item for item in items if item.status])

            if total > 0:
                percent = int((completed / total) * 100)
                if percent == 100:
                    text = f"{work_task.name} — {percent}% ✅"
                elif percent > 0:
                    text = f"{work_task.name} — {percent}% 🔥"
                else:
                    text = f"{work_task.name} — {percent}% 😔"
            else:
                text = f"{work_task.name} — 0% 😔"

            keyboard.add(
                InlineKeyboardButton(
                    text=text,
                    callback_data=f'work_task_{work_task.id}'
                )
            )

    return keyboard.adjust(1).as_markup()


async def select_tasks(user_id):
    keyboard = InlineKeyboardBuilder()
    work_tasks = await get_work_tasks(user_id)

    for work_task in work_tasks:
        keyboard.add(InlineKeyboardButton(text=work_task.name, callback_data=f'select_tasks_{work_task.id}'))
    keyboard.row(InlineKeyboardButton(text='Отмена ❌', callback_data='back_now'))

    return keyboard.adjust(1).as_markup()


async def select_tasks_item(category_id):
    keyboard = InlineKeyboardBuilder()
    task_items = await get_wt_items_by_id(category_id)

    for task_item in task_items:
        keyboard.add(InlineKeyboardButton(text=task_item.name, callback_data=f'select_tasks_item_{task_item.id}'))
    keyboard.row(InlineKeyboardButton(text='Отмена ❌', callback_data='back_now'))

    return keyboard.adjust(1).as_markup()


async def tasks_item(category_id, page: int = 1):
    keyboard = InlineKeyboardBuilder()
    task_items = list(await get_wt_items_by_id(category_id))

    total_pages = math.ceil(len(task_items) / ITEM_PER_PAGE)
    page = max(1, min(page, total_pages))

    start = (page - 1) * ITEM_PER_PAGE
    end = start + ITEM_PER_PAGE
    page_items = task_items[start:end]

    buttons = [
        InlineKeyboardButton(text=(f'{item.name} ✅' if item.status else item.name), callback_data=f"task_item_{category_id}_{item.id}")
        for item in page_items
    ]

    if not task_items:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Нет задач 😔", callback_data="noop")],
            [InlineKeyboardButton(text="🔙 К задачам", callback_data="categories")]
        ])

    for i in range(0, len(buttons), 2):
        keyboard.row(*buttons[i:i+2])

    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Пред", callback_data=f"page:{category_id}:{page - 1}"))
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text="След ➡️", callback_data=f"page:{category_id}:{page + 1}"))

    if nav_buttons:
        keyboard.row(*nav_buttons)
    keyboard.row(InlineKeyboardButton(text="🔙 К Планам", callback_data="categories"))

    return keyboard.as_markup()