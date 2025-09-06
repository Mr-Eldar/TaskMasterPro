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
    try:
        bot = Bot(token=os.getenv('TOKEN'))

        dp = Dispatcher()
        dp.include_routers(user, tasks, ai)
        dp.startup.register(startup)
        dp.shutdown.register(shutdown)
        # Инициализируем базу данных
        try:
            await async_main()
        except Exception as e:
            from app.database.models import init_database
            init_database()
            await async_main()

        # Запускаем бота
        await dp.start_polling(bot)
    except Exception as e:
        print(e)


async def startup():
    print('Starting up...')


async def shutdown():
    print('Shutting down...')


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
