import os

from aiogram.types import Message
from mistralai import Mistral

model = 'mistral-large-latest'
client = Mistral(api_key=f'{os.environ.get("MISTRAL_API_KEY")}')

async def text_generator(prompt: Message.text):
    chat_response = await client.chat.complete_async(
        model=model,
        messages=[
            {
                "role": "system",
                "content": ""
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return chat_response.choices[0].message.content