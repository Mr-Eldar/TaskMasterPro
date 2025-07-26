import os
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DB_URL")

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = async_sessionmaker(engine)
