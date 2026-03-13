import asyncio
import json
import os
import psutil
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from mcrcon import MCRcon

# --- Загрузка конфигурации ---
CONFIG_PATH = "config.json"

if not os.path.exists(CONFIG_PATH):
    print(f"Ошибка: Файл {CONFIG_PATH} не найден. Пожалуйста, запустите установщик (installer_gui.exe).")
    input("Нажмите Enter для выхода...")
    exit(1)

try:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
except Exception as e:
    print(f"Ошибка при чтении config.json: {e}")
    input("Нажмите Enter для выхода...")
    exit(1)

# Читаем данные
API_TOKEN = config.get("bot_token", "")
ADMIN_ID = str(config.get("admin_id", ""))
SERVER_DIR = config.get("server_dir", "")
RCON_PASSWORD = config.get("rcon_password", "")
RCON_PORT = config.get("rcon_port", 25575)
RCON_HOST = "127.0.0.1"

if not API_TOKEN:
    print("Внимание: Токен бота не указан в config.json!")
    input("Нажмите Enter для выхода...")
    exit(1)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


# Проверка, является ли пользователь админом
def is_admin(user_id):
    return str(user_id) == ADMIN_ID


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    welcome_text = (
        "🎮 Привет! Я MineControlBot.\n\n"
        "Я умею управлять сервером Minecraft.\n"
        "Команды:\n"
        "/status - Состояние сервера (RCON)\n"
        "/sys - Нагрузка на ПК"
    )
    await message.answer(welcome_text)


@dp.message(Command("status"))
async def cmd_status(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("У вас нет прав для этой команды.")
        return

    try:
        # Пытаемся подключиться к серверу через RCON с паролем из server.properties
        with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
            resp = mcr.command("list")
            await message.answer(f"✅ Сервер работает!\nИнфо: {resp}")
    except Exception as e:
        await message.answer(f"❌ Сервер выключен или недоступен по RCON.\nОшибка: {e}")


@dp.message(Command("sys"))
async def cmd_sys(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("У вас нет прав для этой команды.")
        return

    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    await message.answer(f"💻 Системные ресурсы хоста:\n- CPU: {cpu}%\n- RAM: {ram}%")


async def main():
    print("Бот успешно запущен и готов к работе!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Остановка бота...")