from db import view_dialogue, add_dialogue, is_user_registered
from openai import AsyncOpenAI
import base64
import os
import asyncio

async def process_ai(client: AsyncOpenAI, user_id, user_message, name):
    user_dialogue = await view_dialogue(user_id)
    if isinstance(user_message, str):
        user_dialogue.append({"role": "user", "content": f"{name} \n {user_message}"})
    else:
        user_message["content"][0]["text"] = f"{name}\n{user_message['content'][0]['text']}"
        user_dialogue.append(user_message)

    response = await client.chat.completions.create(
        model="openai/gpt-5.4-nano",
        messages=user_dialogue,
    )

    assistant_reply = response.choices[0].message.content
    user_dialogue.append({"role": "assistant", "content": assistant_reply})
    while len(user_dialogue) > 20:
        user_dialogue.pop(1)
        user_dialogue.pop(1)
    await add_dialogue(user_id, user_dialogue)
    return assistant_reply


async def process_photo(file, caption):
    image_bytes = file.read()
    base64_str = base64.b64encode(image_bytes).decode("utf-8")
    data_uri = f"data:image/jpeg;base64,{base64_str}"
    user_message = {
        "role": "user",
        "content": [
            {"type": "text", "text": caption},
            {"type": "image_url", "image_url": {"url": data_uri}}
        ]
    }
    return user_message


async def process_file(file, caption):
    file_bytes =file.read()
    filename = file.name
    base64_str = base64.b64encode(file_bytes).decode("utf-8")
    mime_types = {
            '.pdf': 'application/pdf',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.xls': 'application/vnd.ms-excel',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.txt': 'text/plain',
            '.csv': 'text/csv',
        }
    ext = os.path.splitext(filename)[1].lower()
    mime_type = mime_types.get(ext, 'application/octet-stream')
    data_url = f"data:{mime_type};base64,{base64_str}"
    user_message = {
        "role": "user",
        "content": [
            {"type": "text", "text": caption},
            {"type": "file", "file": {
                    "filename": filename,
                    "file_data": data_url
                }
            }
        ]
    }
    return user_message

_locks: dict[int, asyncio.Lock] = {}

def get_user_lock(user_id: int) -> asyncio.Lock:
    if user_id not in _locks:
        _locks[user_id] = asyncio.Lock()
    return _locks[user_id]
    
    





