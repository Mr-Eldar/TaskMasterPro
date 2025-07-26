import asyncio
import os

from aiogram import Bot, Dispatcher

from app.user import user
from app.tasks import tasks


from dotenv import load_dotenv


async def main():
    load_dotenv()
    bot = Bot(token=os.getenv('TOKEN'))
    
    dp = Dispatcher()
    dp.include_routers(user, tasks)
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)
    
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
