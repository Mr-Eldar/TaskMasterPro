from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from app.states import AiChat, WaitGenerator
from app.generators import text_generator

ai = Router()

# def escape_markdown(text: str) -> str:
#     """Экранирует специальные символы MarkdownV2"""
#     escape_chars = r'_*[]()~`>#+-=|{}.!'
#     return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

async def send_long_message(message: Message, text: str, parse_mode: ParseMode = None):
    """Отправляет длинное сообщение частями с обработкой ошибок разметки"""
    try:
        if len(text) <= 4000:
            await message.answer(text, parse_mode=parse_mode)
            return
        
        chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
        
        for i, chunk in enumerate(chunks):
            if i == 0:
                await message.answer(chunk, parse_mode=parse_mode)
            else:
                prefix = "*(продолжение)*\n" if parse_mode == ParseMode.MARKDOWN else "<i>(продолжение)</i>\n"
                await message.answer(f"{prefix}{chunk}", parse_mode=parse_mode)
                
    except Exception as e:
        # Если ошибка разметки, отправляем без нее с экранированием
        if "can't parse entities" in str(e):
            safe_text = parse_mode == ParseMode.MARKDOWN else text
            
            if len(safe_text) <= 4000:
                await message.answer(safe_text)
            else:
                chunks = [safe_text[i:i+4000] for i in range(0, len(safe_text), 4000)]
                for i, chunk in enumerate(chunks):
                    if i == 0:
                        await message.answer(chunk)
                    else:
                        await message.answer(f"Продолжение:\n{chunk}")
        else:
            raise e


@ai.message(Command('ai_chat'))
@ai.message(F.text == 'чат с ИИ 💬')
async def start_chat(message: Message, state: FSMContext):
    await message.answer('🌟 ДОБРО ПОЖАЛОВАТЬ, ЮНЫЙ ПАДАВАН ЗНАНИЙ! 🌟\n\n'
    '<b>Я — Мастер Йода, твой личный наставник в мире учёбы, планов и побед над ленью! 🧙‍♂️✨'
    'Мудрый, как 900-летний джедай, дружелюбный, как Чубакка после чашки какао, и строгий, как экзаменатор на ОГЭ (но только когда надо!).</b>\n\n', parse_mode=ParseMode.HTML)
    await message.answer('🔮 ЧТО Я УМЕЮ (и чем помогу тебе):\n'
    '✅ Составлять планы подготовки — хоть к ОГЭ, хоть к битве со Звездой Смерти (ну или с контрольной по алгебре).\n'
    '✅ Объяснять темы "с нуля" — как будто ты только что проснулся после гиперсна и ничего не помнишь ("Дискриминант? Это что, новый вид дроидов?").\n'
    '✅ Мотивировать — когда лень атакует, как армия клонов, я напомню: "Делай или не делай — но не бросай на половине!"\n'
    '✅ Составлять расписания — чтобы ты успевал всё: и учиться, и отдыхать ("Да, спать тоже надо! Даже джедаям!").\n'
    '✅ Отвечать на вопросы — хоть по математике, хоть по жизни ("Как пережить экзамены? Как не спалить ужин, пока учишь формулы?").', parse_mode=ParseMode.HTML)
    await message.answer('🌿 НАЧНЁМ?\n'
    '<b>Как зовут того, кто готов покорить учёбу со мной?</b> 😊'
    '<b>(Или просто напиши, с чего хочешь начать! "План по математике", "Объясни физику", "Как не заснуть на уроке истории" — я на всё отвечу!)</b>\n\n'
    
    '✨ ПОМНИ:\n'
    '<b>Трудно — не значит невозможно. Невозможно — не значит не попробовать. А попробовать — уже половина победы!</b>\n\n'
    
    '<b>— Мастер Йода (и твой новый лучший друг в учёбе). 🚀</b>\n\n'
    
    '---'
    '<b>P.S. Если вдруг забудешь, как со мной общаться — просто напиши "Йода, помоги!" И я приду на помощь, как Han Solo в последний момент. 😉</b>', parse_mode=ParseMode.HTML)

    await message.answer('<b>Но знай я храню память только в в одном чате если ты закончишь диалог то я забуду о чем мы говорили. Уж прости мне уже 900 лет как ни как.</b>', parse_mode=ParseMode.HTML)
    await state.set_state(AiChat.start_chat)


@ai.message(Command('stop_ai'))
async def stop_chat(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Чат с ИИ завершен.')


@ai.message(AiChat.start_chat)
async def chatting(message: Message, state: FSMContext):
    data = await state.get_data()
    history = data.get('chat_history', [])
    
    history.append(f"User: {message.text}")
    
    await state.set_state(WaitGenerator.wait_generator)
    processing_msg = await message.answer('Ваш запрос обрабатывается... ⌛️')
    
    try:
        full_prompt = "\n".join(history)
        response = await text_generator(prompt=full_prompt)
        
        # Экранируем специальные символы Markdown чтобы избежать ошибок
        safe_response = response.replace('*', '\\*').replace('_', '\\_').replace('`', '\\`')
        
        await send_long_message(message, ParseMode.MARKDOWN)
        
        history.append(f"AI: {response}")
        
        await state.update_data(chat_history=history[-100:])
    except Exception as e:
        await message.answer(f'Произошла ошибка: {str(e)}')
    
    finally:
        await processing_msg.delete()
        await state.set_state(AiChat.start_chat)


@ai.message(WaitGenerator.wait_generator)
async def chatting_wait(message: Message, state: FSMContext):
    await message.answer('Подождите, ваш предыдущий запрос еще обрабатывается.')