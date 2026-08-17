import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender
from aiogram.filters import Command
from aiogram.enums import ChatType
from openai import AsyncOpenAI
from db import user_register, is_user_registered, add_dialogue
from chat_engine import process_ai, process_photo, process_file
MAX_FILE_SIZE = 50 * 1024 * 1024
HELP_TEXT = """
👋 Привет! Мои команды:
!start — старт
!help — помощь
!restart — перезапуск

Можно писать и с /.

👥 В группах и супергруппах: чтобы я ответил, начни сообщение с моего @username, иначе я не увижу его."""


async def cmd_start(message: Message):
    user_id = message.chat.id if message.chat.type in {ChatType.GROUP, ChatType.SUPERGROUP} else message.from_user.id
    await user_register(user_id)
    await message.reply("Привет! я Shuba_GPT, используй команду /help или !help.")


async def cmd_help(message: Message):
     await message.reply(HELP_TEXT)



async def cmd_restart(message: Message):
    user_id = message.chat.id if message.chat.type in {ChatType.GROUP, ChatType.SUPERGROUP} else message.from_user.id
    answer = await is_user_registered(user_id)
    if answer:
        user_dialogue = [{"role": "system", "content": "Привет! Ты ИИ чат-бот ShubaGPT в Telegram. Ты умеешь отвечать на текст и анализировать картинки, которые тебе присылают. Не используй Markdown-разметку (звёздочки, решётки и т.д.) — она не отображается в Telegram."}]
        await add_dialogue(user_id, user_dialogue)
        await message.reply("История очищена.")
    else:
        await message.reply("Зарегистрируйтесь через /start.")



async def cmd_ai_text(message: Message, client: AsyncOpenAI, bot: Bot):
    user_message = message.text
    user_id = (
        message.chat.id
        if message.chat.type in {ChatType.GROUP, ChatType.SUPERGROUP}
        and '@ShubaGPTbot' in user_message
        else message.from_user.id if message.chat.type == ChatType.PRIVATE
        else None
    )
    if user_id is None:
        return
    answer = await is_user_registered(user_id)
    if answer:
        name = message.from_user.first_name or message.from_user.username or "Пользователь"
        async with ChatActionSender.typing(chat_id=message.chat.id, bot=bot):
            try:
                assistant_reply = await process_ai(client, user_id, user_message, name)
                await message.reply(assistant_reply)
            except Exception:
                logging.exception("Ошибка при ответе AI")
                await message.reply("Ошибка =(")
    else:
        await message.reply(f"Зарегистрируйтесь через /start.")


async def cmd_ai_photo(message: Message, client: AsyncOpenAI, bot: Bot):
    caption = message.caption or ''
    user_id = (
        message.chat.id
        if message.chat.type in {ChatType.GROUP, ChatType.SUPERGROUP}
        and '@ShubaGPTbot' in caption
        else message.from_user.id if message.chat.type == ChatType.PRIVATE
        else None
    )
    if user_id is None:
        return
    answer = await is_user_registered(user_id)
    if answer:
        name = message.from_user.first_name or message.from_user.username or "Пользователь"
        photo = message.photo[-1]
        file = await bot.download(photo.file_id)
        user_message = await process_photo(file, caption)
        async with ChatActionSender.typing(chat_id=message.chat.id, bot=bot):
            try:
                assistant_reply = await process_ai(client, user_id, user_message, name)
                await message.reply(assistant_reply)
            except Exception:
                logging.exception("Ошибка при ответе AI")
                await message.reply("Ошибка =(")
    else:
        await message.reply(f"Зарегистрируйтесь через /start.")
        

async def cmd_ai_document(message: Message, client: AsyncOpenAI, bot: Bot):
    if message.document.file_size > MAX_FILE_SIZE:
        await 
        return message.answer("❌ Файл слишком большой! Отправляйте файл меньше 50мб")
    caption = message.caption or ''
    user_id = (
        message.chat.id
        if message.chat.type in {ChatType.GROUP, ChatType.SUPERGROUP}
        and '@ShubaGPTbot' in caption
        else message.from_user.id if message.chat.type == ChatType.PRIVATE
        else None
    )
    if user_id is None:
        return
    answer = await is_user_registered(user_id)
    if answer:
        file = await bot.download(message.document.file_id)
        file.name = message.document.file_name
        try:
            user_message = await process_file(file, caption)
        except Exception:
            logging.exception("Ошибка при обработке файла")
            await message.reply("Ошибка =(")
            return
        name = message.from_user.first_name or message.from_user.username or "Пользователь"
        async with ChatActionSender.typing(chat_id=message.chat.id, bot=bot):
            try:
                assistant_reply = await process_ai(client, user_id, user_message, name)
                await message.reply(assistant_reply)
            except Exception:
                logging.exception("Ошибка при ответе AI")
                await message.reply("Ошибка =(")
    else:
        await message.reply(f"Зарегистрируйтесь через /start.")
