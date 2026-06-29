import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN", "8800988574:AAGEsAuKAvWyyKm7r9C28vxKubOFwxIRndc")
print(f"TOKEN = {TOKEN}")  # временно для отладки

bot = Bot(token=TOKEN)
dp = Dispatcher()

# username -> user_id
registered_users = {}
# user_id -> target_id (ожидает отправки сообщения)
waiting = {}
# user_id -> user_id (активный чат: кто с кем переписывается)
active_chats = {}

@dp.message(Command("start"))
async def start(message: types.Message):
    args = message.text.split()
    username = message.from_user.username
    if username:
        registered_users[username.lower()] = message.from_user.id

    if len(args) > 1:
        target_id = int(args[1])
        waiting[message.from_user.id] = target_id
        await message.answer("Напиши своё анонимное сообщение:")
    else:
        link = f"https://t.me/anon_iuk_bot?start={message.from_user.id}"
        await message.answer(
            f"Привет! Ты зарегистрирован в боте.\n\n"
            f"Твоя ссылка: {link}\n\n"
            f"Или напиши /send @username чтобы написать анонимно!\n"
            f"Когда получишь анонимное сообщение — можешь ответить командой /reply"
        )

@dp.message(Command("send"))
async def send_command(message: types.Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Напиши так: /send @username")
        return

    username = args[1].replace("@", "").lower()
    target_id = registered_users.get(username)

    if not target_id:
        await message.answer("Этот пользователь не зарегистрирован в боте.")
        return

    if target_id == message.from_user.id:
        await message.answer("Нельзя писать самому себе 😄")
        return

    waiting[message.from_user.id] = target_id
    await message.answer(f"Напиши своё анонимное сообщение:")

@dp.message(Command("reply"))
async def reply_command(message: types.Message):
    sender_id = active_chats.get(message.from_user.id)
    if not sender_id:
        await message.answer("Нет активного чата. Тебе нужно сначала получить анонимное сообщение.")
        return

    waiting[message.from_user.id] = sender_id
    await message.answer("Напиши ответное анонимное сообщение:")

@dp.message(Command("stop"))
async def stop_command(message: types.Message):
    active_chats.pop(message.from_user.id, None)
    waiting.pop(message.from_user.id, None)
    await message.answer("Чат завершён.")

@dp.message()
async def handle_message(message: types.Message):
    username = message.from_user.username
    if username:
        registered_users[username.lower()] = message.from_user.id

    target_id = waiting.get(message.from_user.id)
    if target_id:
        await bot.send_message(
            target_id,
            f"🔒 Анонимное сообщение:\n\n{message.text}\n\n"
            f"Чтобы ответить напиши /reply"
        )
        await message.answer("Сообщение отправлено! Если получишь ответ — увидишь его здесь.")
        active_chats[target_id] = message.from_user.id
        waiting.pop(message.from_user.id)
    else:
        await message.answer(
            "Используй:\n"
            "/send @username — написать анонимно\n"
            "/reply — ответить на последнее сообщение\n"
            "/stop — завершить чат"
        )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())