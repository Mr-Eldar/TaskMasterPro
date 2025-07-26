from app.database.models import async_session
from app.database.models import User, WorkTasks, WorkTaskItem
from sqlalchemy import select, update, delete, desc


def connection(func):
    async def wrapper(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)
    return wrapper


@connection
async def set_user(session, tg_id):
    user = await session.scalar(select(User).where(User.tg_id == tg_id))

    if not user:
        session.add(User(tg_id=tg_id))
        await session.commit()


@connection
async def set_status(session, task_id):
    result = await session.execute(select(WorkTaskItem).where(WorkTaskItem.id == task_id))
    task = result.scalar_one_or_none()

    if task is None:
        return print('НЕ НАЙДЕНО')

    task.status = not task.status

    await session.commit()


# Add Requests

@connection
async def add_work_task(session, name, user_id):
    work_task = await session.scalar(select(WorkTasks).where(WorkTasks.name == name))

    if not work_task:
        session.add(WorkTasks(user_id=user_id, name=name))
        await session.commit()


@connection
async def add_task_item(session, category, name, description, photo):
    work_task_item = await session.scalar(select(WorkTaskItem).where(WorkTaskItem.name == name))

    if not work_task_item:
        session.add(WorkTaskItem(category=category, name=name, description=description, photo=photo))
        await session.commit()


# Get Requests
@connection
async def get_work_tasks(session, user_id):
    work_tasks = await session.scalars(select(WorkTasks).where(WorkTasks.user_id == user_id))
    return work_tasks.all()


@connection
async def get_wt_items_by_id(session, category_id):
    return await session.scalars(select(WorkTaskItem).where(WorkTaskItem.category == category_id))


@connection
async def get_task_item_info(session, task_item_id):
    return await session.scalar(select(WorkTaskItem).where(WorkTaskItem.id == task_item_id))


# Delete Requests

@connection
async def delete_work_task(session, task_id):
    work_task = await session.scalar(select(WorkTasks).where(WorkTasks.id == task_id))

    if work_task:
        await session.delete(work_task)
        await session.commit()


@connection
async def delete_task_item(session, task_id):
    task_item = await session.scalar(select(WorkTaskItem).where(WorkTaskItem.id == task_id))

    if task_item:
        await session.delete(task_item)
        await session.commit()


# Edit Requests

@connection
async def rename_work_task(session, task_id, update_name):
    work_task = await session.scalar(select(WorkTasks).where(WorkTasks.id == task_id))

    if work_task:
        query = update(WorkTasks).where(WorkTasks.id == task_id).values(name=update_name)
        await session.execute(query)
        await session.commit()


@connection
async def update_work_task_item(session, task_id, new_name=None, new_description=None):
    task_item = await session.scalar(select(WorkTaskItem).where(WorkTaskItem.id == task_id))

    if task_item:
        if new_name is not None:
            task_item.name = new_name
        if new_description is not None:
            task_item.description = new_description

        await session.commit()
