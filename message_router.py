from aiogram import Router, types, F
from aiogram.types import Message, FSInputFile
import json
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot import conn, cursor, bot
import hashlib
from aiogram.fsm.state import State, StatesGroup
import os
from pydub import AudioSegment

from whisper import translate_audio
import requests

router = Router()
users = {}
def hsh(id):
    return str(hash(id))

@router.message(Command('start'))
async def start_handler(message: Message):
    if hsh(message.from_user.id) in users:
        users[hsh(message.from_user.id)]['query'] = "."
        users[hsh(message.from_user.id)]['content'] = "."
        users[hsh(message.from_user.id)]['f'] = True
    else:
        users[hsh(message.from_user.id)] = {'query': ".", 'content': ".", 'f': True}
    await message.answer(f"Здравствуйте, {message.chat.username}, я ИИ ассистент РЖД. Чем могу быть полезен?")


@router.message(Command('clear_history'))
async def start_handler(message: Message):
    cursor.execute(f"""UPDATE likes SET history = 0 WHERE user_id = '{hsh(message.from_user.id)}'""")
    conn.commit()
    await message.reply("История общения отчищена")

def get_llm_answer(question, history):
    print('START GENERATING ANSWER')
    print(question, history)
    response = requests.post("https://my-subdomen.ru.tuna.am/predict", json={"query": question, "history": history})
    response_json = response.json()
    an = response_json.get('output')
    print('FINISHED GENERATING ANSWER')
    print(an)
    return an

if not os.path.exists("voices"):
    os.makedirs("voices")


async def save_voice_message(voice: types.Voice, file_name: str):
    file = await bot.get_file(voice.file_id)
    await bot.download_file(file.file_path, file_name)

    # Конвертация OGG в MP3
    audio = AudioSegment.from_file(file_name, format="ogg")
    audio.export(file_name, format="mp3")


# Функция обработки голосового сообщения (для примера всегда возвращает "Привет")
def process_voice_message_to_text(file_name: str) -> str:
    # Заглушка для обработки голосового сообщения
    result = translate_audio(file_name)
    print(result)
    return result
def get_last_3(user_id):
    cursor.execute(f"SELECT  query FROM likes where user_id = '{user_id}' and reaction*history=1")
    rows = cursor.fetchall()
    f = rows[:min(3, len(rows))]
    his = []
    if not rows:
        return ""
    for i in f:
        his.append(i[0])
    return " ".join(his)

async def edit_msg(message: types.Message, text):
    await message.edit_text(text)


@router.message()
async def any_message(message: Message):
    global users
    if hsh(message.from_user.id) not in users  or (hsh(message.from_user.id) in users and users[hsh(message.from_user.id)]['f']):
        wait_msg = await message.answer('Пожалуйста, подождите. Генерирую ответ!')
        if message.voice != None:
            await bot.send_chat_action(message.chat.id, 'typing')
            voice = message.voice
            file_name = f"voices/voice_{hsh(message.from_user.id)}_{message.message_id}.mp3"
            await save_voice_message(voice, file_name)
            text = str(process_voice_message_to_text(file_name))
            await bot.send_chat_action(message.chat.id, 'typing')
        else:
            if str(message.text)[0] == '/':
                await message.answer('Неизвестная команда!')
                text = -1
            else:
                await bot.send_chat_action(message.chat.id, 'typing')
                text = message.text
        if text != -1:
            print(text)
            await bot.send_chat_action(message.chat.id, 'typing')

            await bot.send_chat_action(message.chat.id, 'typing')
            await bot.delete_message(message.chat.id, wait_msg.message_id)
            builder = InlineKeyboardBuilder()
            if text:
                history = get_last_3(hsh(message.from_user.id))
                content = get_llm_answer(text, history)
                if content != 'К сожалению я не могу ответить на ваш вопрос. Попробуйте переформулировать его и задать снова':
                    if hsh(message.from_user.id) in users:
                        users[hsh(message.from_user.id)]['query'] = text
                        # users[hsh(message.from_user.id)]['content'] = text
                        users[hsh(message.from_user.id)]['content'] = content
                        users[hsh(message.from_user.id)]['f'] = False
                    else:
                        users[hsh(message.from_user.id)] = {'query': text, 'content': content, 'f': False}
                        # users[hsh(message.from_user.id)] = {'query': text, 'content': text, 'f': False}
                    builder.add(types.InlineKeyboardButton(
                        text="👍",
                        callback_data="like")
                    )
                    builder.add(types.InlineKeyboardButton(
                        text="👎",
                        callback_data="dislike")
                    )
                    await message.answer(users[hsh(message.from_user.id)]['content'], reply_markup=builder.as_markup())
                else:
                    await message.answer(text='К сожалению я не могу ответить на ваш вопрос. Попробуйте переформулировать его и задать снова')
            else:
                await message.answer("К сожалению вы ничего не сказали, повторите ваш вопрос.")
    else:
        await message.answer("Поставьте реакцию на ответ помощника перед тем, как задавать новый вопрос.")

        # await message.answer('Решился ли Ваш вопрос?', )


@router.callback_query(F.data == 'like')
async def like(callback: types.CallbackQuery):
    global users
    users[hsh(callback.from_user.id)]['f'] = True
    # await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await bot.edit_message_reply_markup(callback.message.business_connection_id, callback.message.chat.id,
                                        callback.message.message_id, reply_markup=None)
    await callback.message.answer(
        'Мы рады, что ваш вопрос решился! Если вас интересуют другие вопросы, то вы можете меня спросить об этом!')
    cursor.execute(f"""INSERT INTO likes(user_id, reaction, query, answer, history)
                VALUES  ('{callback.message.chat.id}', {1}, '{users[hsh(callback.from_user.id)]['query']}', '{users[hsh(callback.from_user.id)]['content']}', 1)""")
    conn.commit()


@router.callback_query(F.data == 'dislike')
async def like(callback: types.CallbackQuery):
    global users
    users[hsh(callback.from_user.id)]['f'] = True
    await bot.edit_message_reply_markup(callback.message.business_connection_id, callback.message.chat.id,
                                        callback.message.message_id, reply_markup=None)
    await callback.message.answer(
        'Очень жаль, что мой ответ Вас не устроил. Если вас интересуют другие вопросы, то вы можете меня спросить об этом!')
    cursor.execute(f"""INSERT INTO likes(user_id, reaction, query, answer, history)
            VALUES  ('{callback.message.chat.id}', {0}, '{users[hsh(callback.from_user.id)]['query']}', '{users[hsh(callback.from_user.id)]['content']}', 0)""")
    conn.commit()



