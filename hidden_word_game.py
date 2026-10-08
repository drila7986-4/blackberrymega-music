import random
import re
import time

WORDS = [
    ("apple", "🍎 Fruit you can eat"), ("music", "🎵 You listen to it"),
    ("tiger", "🐯 Big striped wild cat"), ("planet", "🪐 It moves around a star"),
    ("camera", "📷 Takes photos"), ("diamond", "💎 A precious stone"),
    ("rainbow", "🌈 Appears in the sky after rain"), ("holiday", "🏖️ A break from work/school"),
    ("teacher", "📚 A person who teaches"), ("station", "🚉 Trains stop here"),
    ("journey", "🧳 Travel from one place to another"), ("library", "📖 Place full of books"),
    ("monster", "👾 Imaginary scary creature"), ("morning", "🌅 Start of the day"),
    ("phone", "📱 You use it to call people"), ("river", "🌊 Flowing natural water"),
    ("garden", "🌷 Place where plants grow"), ("school", "🏫 Place where students study"),
    ("football", "⚽ Popular ball sport"), ("computer", "💻 Electronic machine for work"),
    ("beautiful", "✨ Pleasant to look at"), ("adventure", "🗺️ Exciting experience"),
    ("knowledge", "🧠 Information and understanding"), ("technology", "🤖 Science used to make useful things"),
    ("wonderful", "🌟 Extremely good"), ("celebrate", "🎉 Do something special for an occasion"),
    ("friendship", "🤝 Bond between friends"), ("sunshine", "☀️ Light from the sun"),
    ("chocolate", "🍫 Sweet food made from cocoa"), ("butterfly", "🦋 Insect with colorful wings"),
]

GAME_TIME = 90
ROUNDS = 10
ACTIVE = {}


def normalize(s: str) -> str:
    return re.sub(r"[^a-z]", "", (s or "").lower())


def mask_word(word: str) -> str:
    if len(word) <= 4:
        hide = 1
    else:
        hide = max(2, len(word) // 3)
    indexes = set(random.sample(range(len(word)), min(hide, len(word) - 1)))
    return " ".join("_" if i in indexes else ch for i, ch in enumerate(word))


def _new_word():
    word, clue = random.choice(WORDS)
    return {"answer": word, "clue": clue, "masked": mask_word(word)}


def start_game(chat_id: int):
    first = _new_word()
    ACTIVE[chat_id] = {
        "round": 1,
        "word": first,
        "started": time.monotonic(),
        "progress": {},
    }
    return render(chat_id)


def render(chat_id: int):
    g = ACTIVE[chat_id]
    return (
        "╭━━━〔 🕵️ BLACKBERRY HIDDEN WORD 〕━━━╮\n"
        f"┃ 🔥 Round: <b>{g['round']}/{ROUNDS}</b>\n"
        f"┃ 💡 Clue: <b>{g['word']['clue']}</b>\n"
        f"┃ 🔤 Word: <code>{g['word']['masked']}</code>\n"
        "┃ ⏱️ Time: <b>90 seconds</b>\n"
        "┃ 🏆 First player to solve all 10 wins\n"
        "┃ 💰 Winner reward: <b>3000 🪙</b>\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
        "💬 Hidden word type karke guess karo!"
    )


def answer(chat_id: int, user_id: int, text: str):
    g = ACTIVE.get(chat_id)
    if not g:
        return None
    if time.monotonic() - g["started"] > GAME_TIME:
        ACTIVE.pop(chat_id, None)
        return {"status": "timeout", "answer": g["word"]["answer"]}
    if normalize(text) != normalize(g["word"]["answer"]):
        return {"status": "wrong"}

    progress = g["progress"]
    progress[user_id] = progress.get(user_id, 0) + 1
    solved = progress[user_id]
    if solved >= ROUNDS:
        ACTIVE.pop(chat_id, None)
        return {"status": "winner", "answer": g["word"]["answer"], "solved": solved}

    g["round"] += 1
    g["word"] = _new_word()
    g["started"] = time.monotonic()
    return {"status": "correct", "answer": text, "solved": solved, "round": g["round"], "board": render(chat_id)}


def cancel(chat_id: int):
    return ACTIVE.pop(chat_id, None)
