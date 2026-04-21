import telebot
import os
from telebot import types
from openai import OpenAI
#Всякие разные вещи
TOKEN = os.getenv('BOT_API_TOKEN')
OPENAI_KEY = os.getenv('IPAIANEPO')
bot = telebot.TeleBot(TOKEN)
client = OpenAI(api_key=OPENAI_KEY, base_url='https://routerai.ru/api/v1')
#Всякие словари
chat_history = {}
if __name__ == "__main__":
    print("бот запущен!")
def set_commands():
    bot.set_my_commands([
        types.BotCommand("restart", "Очистить историю")
    ])
set_commands()

@bot.message_handler(commands=['restart'])
def restart(message):
    chat_history.pop(message.chat.id, None)
    bot.send_message(message.chat.id, '✅ История очищена')

@bot.message_handler(content_types=['text'])
def send_text(message):
    chat_id = message.chat.id
    if message.chat.type == 'private':
        user_text = message.text
        name = message.from_user.first_name
        if chat_id not in chat_history:
            chat_history[chat_id] = [
                {'role': 'system', 'content': 'Ты ShubaGPT, отвечай в меру, будь разговорчивым. Для твоего понимание ты бот в телеграмме не используй знаки выделения которые ты используешь а то это не красиво выглядит, и анализировать картинки ты умеешь программа тебя в этом не огрничивает а вот смотреть файлы не можешь.'}
            ]
        chat_history[chat_id].append({'role': 'user', 'content': f'user: {name}\n{user_text}'})
        bot.send_chat_action(chat_id, 'typing')
        try:
            response = client.chat.completions.create(
                model="openai/gpt-4.1-mini",
                messages=chat_history[chat_id]
            )
            bot_answer = response.choices[0].message.content
            # Сохраняем ответ бота в историю
            chat_history[chat_id].append({'role': 'assistant', 'content': bot_answer})
            # Отправляем ответ
            bot.send_message(
                chat_id,
                bot_answer,
                reply_to_message_id = message.message_id  # <-- вот это связывает ответ с сообщением
            )
        except Exception as e:
            bot.send_message(chat_id, f"⚠️ Что то пошло не так. Ошибка.")
            # Очищаем историю при ошибке, чтобы не ломалось дальше
            chat_history[chat_id] = chat_history[chat_id][:1]
    elif message.chat.type == 'group' or message.chat.type == 'supergroup':
        user_text = message.text
        name = message.from_user.first_name
        if '@ShubaGPTbot' in user_text:
            if chat_id not in chat_history:
                chat_history[chat_id] = [
                    {'role': 'system', 'content': 'Ты ShubaGPT, отвечай в меру, будь разговорчивым. Для твоего понимание ты бот в телеграмме не используй знаки выделения которые ты используешь а то это не красиво выглядит, и анализировать картинки ты умеешь программа тебя в этом не огрничивает а вот смотреть файлы не можешь.'}
                ]
            chat_history[chat_id].append({'role': 'user', 'content': f'user: {name}\n{user_text}'})
            bot.send_chat_action(chat_id, 'typing')
            try:
                response = client.chat.completions.create(
                    model="openai/gpt-4.1-mini",
                    messages=chat_history[chat_id]
                )

                bot_answer = response.choices[0].message.content

                # Сохраняем ответ бота в историю
                chat_history[chat_id].append({'role': 'assistant', 'content': bot_answer})

                # Отправляем ответ
                bot.send_message(
                    chat_id,
                    bot_answer,
                    reply_to_message_id = message.message_id  # <-- вот это связывает ответ с сообщением
                )
            except Exception as e:
                bot.send_message(chat_id, f"⚠️ Что то пошло не так. Ошибка.")
                # Очищаем историю при ошибке, чтобы не ломалось дальше
                chat_history[chat_id] = chat_history[chat_id][:1]

@bot.message_handler(content_types=['photo'])
def send_photo(message):
    chat_id = message.chat.id
    if message.chat.type == 'private':
        user_text = message.text
        name = message.from_user.first_name
        if chat_id not in chat_history:
            chat_history[chat_id] = [
                {'role': 'system', 'content': 'Ты ShubaGPT, отвечай в меру, будь разговорчивым. Для твоего понимание ты бот в телеграмме не используй знаки выделения которые ты используешь а то это не красиво выглядит, и анализировать картинки ты умеешь программа тебя в этом не огрничивает а вот смотреть файлы не можешь.'}
            ]
        #Получаем премую ссылку
        prompt = message.caption
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        photo_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
        vision_msg = {
            "role": "user",
            "name": f"{name}",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": photo_url}}
            ]
        }
        chat_history[chat_id].append(vision_msg)
        bot.send_chat_action(chat_id, 'typing')
        try:
            response = client.chat.completions.create(
                model="openai/gpt-4.1-mini",
                messages=chat_history[chat_id]
            )
            answer = response.choices[0].message.content

            chat_history[chat_id].append({"role": "assistant", "content": answer})
            bot.send_message(chat_id, answer, reply_to_message_id=message.message_id)

        except Exception as e:
            bot.send_message(chat_id, f"⚠️ Что то пошло не так. Ошибка.")
            chat_history[chat_id] = [chat_history[chat_id][0]]  # сброс до системного промпта
    elif message.chat.type == 'group' or message.chat.type == 'supergroup':
        user_text = message.text
        name = message.from_user.first_name
        if '@ShubaGPTbot' in message.caption:
            if chat_id not in chat_history:
                chat_history[chat_id] = [
                    {'role': 'system', 'content': 'Ты ShubaGPT, отвечай в меру, будь разговорчивым. Для твоего понимание ты бот в телеграмме не используй знаки выделения которые ты используешь а то это не красиво выглядит, и анализировать картинки ты умеешь программа тебя в этом не огрничивает а вот смотреть файлы не можешь.'}
                ]
            # Получаем премую ссылку
            prompt = message.caption
            file_id = message.photo[-1].file_id
            file_info = bot.get_file(file_id)
            photo_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
            #
            vision_msg = {
                "role": "user",
                "name": f"{name}",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": photo_url}}
                ]
            }
            chat_history[chat_id].append(vision_msg)
            bot.send_chat_action(chat_id, 'typing')
            try:
                response = client.chat.completions.create(
                    model="openai/gpt-4.1-mini",
                    messages=chat_history[chat_id]
                )
                answer = response.choices[0].message.content
                chat_history[chat_id].append({"role": "assistant", "content": answer})
                bot.send_message(chat_id, answer, reply_to_message_id=message.message_id)
            except Exception as e:
                bot.send_message(chat_id, f"⚠️ Что то пошло не так. Ошибка.")
                chat_history[chat_id] = [chat_history[chat_id][0]]  # сброс до системного промпта
bot.infinity_polling()
