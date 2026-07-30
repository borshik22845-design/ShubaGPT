from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender
from aiogram.filters import Command
from aiogram.enums import ChatType
from openai import AsyncOpenAI
from db import user_register, is_user_registered, add_dialogue
from chat_engine import process_ai, process_photo


async def cmd_start(message: Message):
    user_id = message.chat.id if message.chat.type in {ChatType.GROUP, ChatType.SUPERGROUP} else message.from_user.id
    await user_register(user_id)
    await message.answer("Привет! я Shuba_GPT, используй команду /help.")


async def cmd_help(message: Message):
    await message.answer(f"/restart - сбрасывает диалог.")


async def cmd_restart(message: Message):
    user_id = message.chat.id if message.chat.type in {ChatType.GROUP, ChatType.SUPERGROUP} else message.from_user.id
    answer = await is_user_registered(user_id)
    if answer:
        user_dialogue = [{"role": "system", "content": "Привет! Ты ИИ чат-бот ShubaGPT в Telegram. Ты умеешь отвечать на текст и анализировать картинки, которые тебе присылают. Не используй Markdown-разметку (звёздочки, решётки и т.д.) — она не отображается в Telegram."}]
        await add_dialogue(user_id, user_dialogue)
        await message.answer("История очищена.")
    else:
        await message.answer("Зарегистрируйтесь через /start.")



async def cmd_ai_text(message: Message, client: AsyncOpenAI, bot: Bot):
    if message.chat.type in {ChatType.GROUP, ChatType.SUPERGROUP}:
        user_message = message.text
        answer = await is_user_registered(message.chat.id)
        if '@ShubaGPTbot' in user_message:
            if answer:
                user_id = message.chat.id
                name = message.from_user.first_name or message.from_user.username or "Пользователь"
                async with ChatActionSender.typing(chat_id=message.chat.id, bot=bot):
                    try:
                        assistant_reply = await process_ai(client, user_id, user_message, name)
                        await message.reply(assistant_reply)
                    except Exception as e:
                        print(e)
                        await message.answer("Ошибка =(")
            else:
                await message.answer(f"Зарегистрируйтесь через /start.")
    elif message.chat.type == ChatType.PRIVATE:
        user_id = message.from_user.id
        answer = await is_user_registered(user_id)
        if answer:
            user_message = message.text
            name = message.from_user.first_name or message.from_user.username or "Пользователь"
            async with ChatActionSender.typing(chat_id = message.chat.id, bot = bot):
                try:
                    assistant_reply = await process_ai(client, user_id, user_message, name)
                    await message.answer(assistant_reply)
                except Exception as e:
                    print(e)
                    await message.answer("Ошибка =(")
        else:
            await message.answer(f"Зарегистрируйтесь через /start.")


async def cmd_ai_photo(message: Message, client: AsyncOpenAI, bot: Bot):
    if message.chat.type in {ChatType.GROUP, ChatType.SUPERGROUP}:
        text = message.caption or ''
        answer = await is_user_registered(message.chat.id)
        if '@ShubaGPTbot' in text:
            if answer:
                user_id = message.chat.id
                name = message.from_user.first_name or message.from_user.username or "Пользователь"
                photo = message.photo[-1]
                caption = message.caption or ''
                file = await bot.download(photo.file_id)
                user_message = await process_photo(file, caption)
                async with ChatActionSender.typing(chat_id=message.chat.id, bot=bot):
                    try:
                        assistant_reply = await process_ai(client, user_id, user_message, name)
                        await message.reply(assistant_reply)
                    except Exception as e:
                        print(e)
                        await message.answer("Ошибка =(")
            else:
                await message.answer(f"Зарегистрируйтесь через /start.")
    elif message.chat.type == ChatType.PRIVATE:
        user_id = message.from_user.id
        answer = await is_user_registered(user_id)
        if answer:
            name = message.from_user.first_name or message.from_user.username or "Пользователь"
            photo = message.photo[-1]
            caption = message.caption or ''
            user_message = await process_photo(file, caption)
            async with ChatActionSender.typing(chat_id=message.chat.id, bot=bot):
                try:
                    assistant_reply = await process_ai(client, user_id, user_message, name)
                    await message.reply(assistant_reply)
                except Exception as e:
                    print(e)
                    await message.answer("Ошибка =(")
        else:
            await message.answer(f"Зарегистрируйтесь через /start.")


