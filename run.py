import asyncio
import os

from aiogram import Bot, Dispatcher

from app.user import user
from app.tasks import tasks
from app.ai_chat import ai
from app.database.models import async_main

from dotenv import load_dotenv


async def main():
    load_dotenv()
    bot = Bot(token=os.getenv('TOKEN'))
    
    dp = Dispatcher()
    dp.include_routers(user, tasks, ai)
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)

    try:
        await async_main()
    except Exception as e:
        print(f"Database initialization warning: {e}")
        # Продолжаем работу даже если БД не подключилась
    
    await dp.start_polling(bot)


async def startup():
    print('Starting up...')


async def shutdown():
    print('Shutting down...')


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
