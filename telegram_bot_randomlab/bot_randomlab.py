import os
import random
import secrets
import string
import uuid
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()

WORDS = ["lorem", "ipsum", "dolor", "sit", "amet", "consetetur",
         "adipiscing", "elit", "sed", "do", "eiusmod", "tempor",
         "incididunt", "ut", "labore", "et", "dolore", "magna", "aliqua"]

EIGHTBALL = [
    "Бесспорно", "Предрешено", "Никаких сомнений",
    "Определённо да", "Можешь быть уверен в этом",
    "Мне кажется — «да»", "Вероятнее всего", "Хорошие перспективы",
    "Знаки говорят — да", "Да",
    "Пока не ясно, попробуй снова", "Спроси позже",
    "Лучше не рассказывать", "Сейчас нельзя предсказать",
    "Сконцентрируйся и спроси опять",
    "Даже не думай", "Мой ответ — «нет»",
    "По моим данным — нет", "Перспективы не очень хорошие", "Весьма сомнительно"
]

def _parse_list_arg(arg: str):
    return [x for x in (s.strip() for s in arg.split("|")) if x]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Привет! Я RandomLab — набор простых рандом‑инструментов. Набери /help.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "/start — приветствие\n"
        "/help — справка\n"
        "/roll <NdM> — бросить N кубиков с M гранями (напр. 2d6)\n"
        "/coin — орёл/решка\n"
        "/rand <a> <b> — случайное целое [a, b]\n"
        "/choose a|b|c — выбрать один из списка\n"
        "/shuffle a|b|c — перемешать список\n"
        "/password <len> — пароль длины 8..64\n"
        "/uuid — UUID v4\n"
        "/color — случайный цвет #RRGGBB\n"
        "/eightball — магический шар\n"
        "/lorem <n> — n слов lorem\n"
        "/sample <k> a|b|c — выбрать k без повторов\n"
        "/permute <n> — перестановка 1..n (n≤10)"
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or "d" not in context.args[0]:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Использование: /roll NdM (например, 2d6)")
        return
    try:
        n_str, m_str = context.args[0].lower().split("d", 1)
        n = int(n_str); m = int(m_str)
        if n <= 0 or m <= 1 or n > 20 or m > 1000:
            raise ValueError
    except Exception:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Неверный формат. Пример: 3d6 (1≤n≤20, 2≤m≤1000)")
        return
    rolls = [random.randint(1, m) for _ in range(n)]
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Броски: {rolls} | сумма={sum(rolls)}")

async def coin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=random.choice(["Орёл", "Решка"]))

async def rand_int(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Использование: /rand <a> <b>")
        return
    try:
        a = int(context.args[0]); b = int(context.args[1])
    except ValueError:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="a и b должны быть целыми числами")
        return
    if a > b:
        a, b = b, a
    await context.bot.send_message(chat_id=update.effective_chat.id, text=str(random.randint(a, b)))

async def choose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Использование: /choose a|b|c")
        return
    items = _parse_list_arg(" ".join(context.args))
    if not items:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Список пуст.")
        return
    await context.bot.send_message(chat_id=update.effective_chat.id, text=random.choice(items))

async def shuffle_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Использование: /shuffle a|b|c")
        return
    items = _parse_list_arg(" ".join(context.args))
    if not items:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Список пуст.")
        return
    random.shuffle(items)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=" | ".join(items))

async def password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Использование: /password <len> (8..64)")
        return
    try:
        length = int(context.args[0])
    except ValueError:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Длина должна быть целым числом")
        return
    if not (8 <= length <= 64):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Длина должна быть от 8 до 64 символов")
        return
    alphabet = string.ascii_letters + string.digits
    pwd = "".join(secrets.choice(alphabet) for _ in range(length))
    await context.bot.send_message(chat_id=update.effective_chat.id, text=pwd)

async def uuid_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=str(uuid.uuid4()))

async def color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    val = random.randint(0, 0xFFFFFF)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"#{val:06X}")

async def eightball(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=random.choice(EIGHTBALL))

async def lorem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Использование: /lorem <n>")
        return
    try:
        n = int(context.args[0])
    except ValueError:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="n должно быть целым")
        return
    if not (1 <= n <= 50):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="n должно быть в диапазоне 1..50")
        return
    words = [random.choice(WORDS) for _ in range(n)]
    await context.bot.send_message(chat_id=update.effective_chat.id, text=" ".join(words))

async def sample(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Использование: /sample <k> a|b|c")
        return
    try:
        k = int(context.args[0])
    except ValueError:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="k должно быть целым")
        return
    items = _parse_list_arg(" ".join(context.args[1:]))
    if k < 0 or k > len(items):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="k должно быть в диапазоне 0..len(items)")
        return
    out = random.sample(items, k)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=" | ".join(out))

async def permute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Использование: /permute <n> (n≤10)")
        return
    try:
        n = int(context.args[0])
    except ValueError:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="n должно быть целым")
        return
    if not (1 <= n <= 10):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="n должно быть 1..10")
        return
    arr = list(range(1, n+1))
    random.shuffle(arr)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=" ".join(map(str, arr)))

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("Нет TELEGRAM_BOT_TOKEN в .env")
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("roll", roll))
    app.add_handler(CommandHandler("coin", coin))
    app.add_handler(CommandHandler("rand", rand_int))
    app.add_handler(CommandHandler("choose", choose))
    app.add_handler(CommandHandler("shuffle", shuffle_cmd))
    app.add_handler(CommandHandler("password", password))
    app.add_handler(CommandHandler("uuid", uuid_cmd))
    app.add_handler(CommandHandler("color", color))
    app.add_handler(CommandHandler("eightball", eightball))
    app.add_handler(CommandHandler("lorem", lorem))
    app.add_handler(CommandHandler("sample", sample))
    app.add_handler(CommandHandler("permute", permute))

    app.run_polling()

if __name__ == "__main__":
    main()
