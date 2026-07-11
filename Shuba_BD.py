from sqlalchemy import Column, Integer, String, Boolean, JSON, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
import os
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
print("🔍 ТЕКУЩИЙ URL БАЗЫ:", DATABASE_URL)  # <-- ДОБАВЬ ЭТУ СТРОКУ

engine = create_async_engine(
    DATABASE_URL,
    echo=False
)

async_session = async_sessionmaker(engine, class_=AsyncSession)


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    dialogue = Column(JSON, nullable=True, default=lambda: [{"role": "system", "content": "Привет! Ты ии чат бот ShubaGPT в Telegram, на этот момент времени ты можешь только отвечать на текст картинки тебе не отправятся как и многое другое, кроме текста."}])
    privilege = Column(String(50), nullable=True, default=None)
    ai = Column(Boolean, default=False)

async def user_register(user_id: int):
    """Добавление юзера в бд"""
    async with async_session() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            new_user = User(user_id=user_id)
            session.add(new_user)
            await session.commit()
        else:
            return


async def add_dialogue(user_id, user_dialogue):
    """Функция добавления диалога в бд"""
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user:
            user.dialogue = user_dialogue
            await session.commit()
            return True
        return False


async def view_dialogue(user_id):
    """Достает диалог из бд"""
    async with async_session() as session:
        user = await session.get(User, user_id)
        return user.dialogue if user else None


async def view_ai(user_id):
    """Смотрит значение ai"""
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user:
            user_ai = user.ai
            return user_ai
        return False


async def change_ai(user_id):
    """Меняет значение ai в таблице"""
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user:
            user.ai = not user.ai
            await session.commit()
            return True
        return False


async def is_user_registered(user_id):
    """Функция проверки юзера в базе"""
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user:
            return True
        return False


async def init_db():
    """Асинхронная инициализация базы"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)



