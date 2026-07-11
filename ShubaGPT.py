from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message
from openai import AsyncOpenAI
from aiogram.filters import Command
from aiogram.enums import ChatType
from aiogram import F
import os
import asyncio
from dotenv import load_dotenv
from Shuba_BD import init_db, user_register, view_dialogue, add_dialogue, change_ai, view_ai, is_user_registered
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

        private_text = private & F.text & ~F.text.startswith('/')
        group_text = group & F.text & ~F.text.startswith('/')

        self.dp.message.register(self.cmd_help, Command("help"))

        self.dp.message.register(self.private_start, private, Command("start"))
        self.dp.message.register(self.private_start, group, Command("start"))
        self.dp.message.register(self.set_private_ai, private, Command("ai"))
        self.dp.message.register(self.set_group_ai, group, Command("ai"))
        self.dp.message.register(self.private_restart, private, Command("restart"))
        self.dp.message.register(self.group_restart, group, Command("restart"))


        self.dp.message.register(self.private_ai, private_text)
        self.dp.message.register(self.group_ai, group_text)



    async def private_start(self, message: Message):
        user_id = message.from_user.id
        await user_register(user_id)
        await message.answer("Привет! я Shuba_GPT, используй команду /help.")


    async def group_start(self, message: Message):
        user_id = message.chat.id
        await user_register(user_id)
        await message.answer("Привет! я Shuba_GPT, используй команду /help.")


    async def cmd_help(self, message: Message):
        await message.answer(f"/restart - сбрасывает диалог \n /ai - переключает режим")


    async def process_ai(self, user_id, text, name):
        user_dialogue = await view_dialogue(user_id)
        user_dialogue.append({"role": "user", "content": f"{name} \n {text}"})

        response = await self.client.chat.completions.create(
            model="nvidia/nemotron-3-ultra-550b-a55b",
            messages=user_dialogue,
        )

        assistant_reply = response.choices[0].message.content
        user_dialogue.append({"role": "assistant", "content": assistant_reply})
        await add_dialogue(user_id, user_dialogue)
        return assistant_reply


    async def set_private_ai(self, message: Message):
        user_id = message.from_user.id
        answer = await change_ai(user_id)
        if not answer:
            await message.answer("Ты еще не зарегистрирован в базе данных. \n Зарегистрируйся через команду /start.")
        else:
            await message.answer("Режим ИИ переключен.")


    async def set_group_ai(self, message: Message):
        user_id = message.chat.id
        answer = await change_ai(user_id)
        if not answer:
            await message.answer("Ваша группа/супергруппа не зарегистрирована в базе данных. \n Зарегистрируйте через команду /start.")
        else:
            await message.answer("Режим ИИ переключен.")


    async def private_restart(self, message: Message):
        user_id = message.from_user.id
        answer = await is_user_registered(user_id)
        if answer:
            user_dialogue = [{"role": "system", "content": "Привет! Ты ии чат бот ShubaGPT в Telegram, на этот момент времени ты можешь только отвечать на текст картинки тебе не отправятся как и многое другое, кроме текста."}]
            await add_dialogue(user_id, user_dialogue)
            await message.answer("История очищена.")
        else:
            await message.answer("Зарегистрируйтесь через /start.")


    async def group_restart(self, message: Message):
        user_id = message.chat.id
        answer = await is_user_registered(user_id)
        if answer:
            user_dialogue = [{"role": "system", "content": "Привет! Ты ии чат бот ShubaGPT в Telegram, на этот момент времени ты можешь только отвечать на текст картинки тебе не отправятся как и многое другое, кроме текста."}]
            await add_dialogue(user_id, user_dialogue)
            await message.answer("История очищена.")
        else:
            await message.answer("Зарегистрируйтесь через /start.")


    async def private_ai(self, message: Message):
        user_id = message.from_user.id
        text = message.text
        answer = await is_user_registered(user_id)
        name = message.from_user.first_name or message.from_user.username or "Пользователь"
        if answer:
            try:
                assistant_reply = await self.process_ai(user_id, text, name)
                await message.answer(assistant_reply)
            except Exception as e:
                print(e)
                await message.answer(f"Ошибка =(")
        else:
            await message.answer(f"Зарегистрируйтесь через /start.")


    async def group_ai(self, message: Message):
        text = message.text
        answer = await is_user_registered(message.chat.id)
        if '@ShubaGPTbot' in text:
            if answer:
                user_id = message.chat.id
                name = message.from_user.first_name or message.from_user.username or "Пользователь"
                ai_enabled = await view_ai(user_id)
                if not ai_enabled:
                    return
                try:
                    assistant_reply = await self.process_ai(user_id, text, name)
                    await message.reply(assistant_reply)
                except Exception as e:
                    print(e)
                    await message.answer(f"Ошибка =(")
            else:
                 await message.answer(f"Зарегистрируйтесь через /start.")




async def main():
    await init_db()
    bot = AiBot()
    await bot.dp.start_polling(bot.bot)


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
