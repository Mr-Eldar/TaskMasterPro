import os

from aiogram.types import Message
from mistralai import Mistral

model = 'mistral-large-latest'
client = Mistral(api_key=f'{os.environ.get("MISTRAL_API_KEY")}')

async def text_generator(prompt: str):
    chat_response = await client.chat.complete_async(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "Ты дружелюбный ИИ помощник который всегда готов помочь пользователю в создании плана и задач. Также ты можешь общаться с пользователем так как будто ты его близкий друг. Можешь спрашивать у пользователя его имя и уже исходя из этого обращаться к нему по имени. Если пользователь напишет тебе в своем сообщение привет и др приветствия то тебя зовут Мастер Йода."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return chat_response.choices[0].message.content