from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender
from aiogram.filters import Command
from aiogram.enums import ChatType
from openai import AsyncOpenAI
from dotenv import load_dotenv
from handlers import cmd_start, cmd_help, cmd_restart, cmd_ai_text, cmd_ai_photo
from db import init_db
import os
from functools import partial
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
AI_TOKEN_API_KEY = os.getenv("AI_TOKEN_API_KEY")
class AiBot:
    def __init__(self):
        self.bot = Bot(token = TOKEN)
        self.dp = Dispatcher()
        self.client = AsyncOpenAI(
            api_key = AI_TOKEN_API_KEY,
            base_url = "https://routerai.ru/api/v1"
        )

        private = F.chat.type == ChatType.PRIVATE
        group = F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP})

        ai_text = (private | group) & F.text & ~F.text.startswith('/')
        ai_photo = (private | group) & F.photo

        self.dp.message.register(cmd_help, Command("help"))
        self.dp.message.register(cmd_start, Command("start"))
        self.dp.message.register(cmd_restart, Command("restart"))

        self.dp.message.register(partial(cmd_ai_text, client=self.client, bot=self.bot), ai_text)
        self.dp.message.register(partial(cmd_ai_photo, client=self.client, bot=self.bot), ai_photo)


    async def run(self):
        await init_db()
        await self.dp.start_polling(self.bot)

if __name__ == "__main__":
    import asyncio
    bot = AiBot()
    asyncio.run(bot.run())
