import asyncio
import logging
import sys
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
import sqlite3
import message_router
import psycopg2
BOT_TOKEN = "8191016345:AAFyg6DpUeKp-csp8U8UhHfjI-73xoGT6Vs"

import psycopg2
bot = Bot(BOT_TOKEN)
user = "kostyan1ml"
password = "MatveiKostyaSasha17."
conn = psycopg2.connect(database="RZD_BD", user=user,
                        password=password, host="83.166.236.254")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS likes (user_id Text, reaction Int, query Text, answer Text, history Int)")
conn.commit()


async def on_startup():
    psycopg2.connect(database="RZD_BD", user=user,
                     password=password, host="83.166.236.254")
    print("Подключён к БД")


async def main() -> None:
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    await bot.delete_webhook(drop_pending_updates=True)
    dp = Dispatcher()
    dp.include_routers(message_router.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
