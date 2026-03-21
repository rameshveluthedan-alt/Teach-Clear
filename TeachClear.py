# TeachClear.py
# -------------
# Telegram bot for TeachClear — Grade 6 Mathematics teaching assistant.
# Uses pyTelegramBotAPI (telebot) — synchronous polling.
# Gemini API via the google-genai SDK.
#
# USER FLOW:
#   /start  →  language picker (inline buttons)
#           →  chapter list in chosen language (inline buttons)
#           →  teacher types query  →  Gemini responds
#   /chapter  →  chapter list again (to switch chapter anytime)
#
# Required environment variables in .env:
#   TELEGRAM_TOKEN   — from @BotFather on Telegram
#   GEMINI_API_KEY   — from https://aistudio.google.com/app/apikey

import os
import logging
from dotenv import load_dotenv

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from google import genai

from rag import get_relevant_context
from prompts import build_prompt
from metadata import (
    CHAPTER_METADATA,
    LANGUAGES,
    LANGUAGE_PICKER_PROMPT,
    CHAPTER_SELECTED_MSG,
    SWITCH_CHAPTER_MSG,
    READY_PROMPT,
    get_chapter_by_number,
    get_title,
)

# ── Setup ──────────────────────────────────────────────────────────────────────
load_dotenv()

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL   = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite-preview")

if not TELEGRAM_TOKEN:
    raise EnvironmentError("TELEGRAM_TOKEN is missing from your .env file.")
if not GEMINI_API_KEY:
    raise EnvironmentError("GEMINI_API_KEY is missing from your .env file.")

bot           = telebot.TeleBot(TELEGRAM_TOKEN)
gemini_client = genai.Client(api_key=GEMINI_API_KEY)


# ── Session state ──────────────────────────────────────────────────────────────
# Stores per-user state in memory.
# { chat_id: { "lang": "ta", "chapter": <chapter_dict> } }
# Resets when the bot restarts — fine for MVP.
user_sessions: dict[int, dict] = {}

def get_session(chat_id: int) -> dict:
    if chat_id not in user_sessions:
        user_sessions[chat_id] = {"lang": "en", "chapter": None}
    return user_sessions[chat_id]


# ── Keyboard builders ──────────────────────────────────────────────────────────
def language_keyboard() -> InlineKeyboardMarkup:
    """One button per supported language, 2 per row."""
    kb = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton(info["label"], callback_data=f"lang:{code}")
        for code, info in LANGUAGES.items()
    ]
    kb.add(*buttons)
    return kb


def chapter_keyboard(lang: str) -> InlineKeyboardMarkup:
    """One button per chapter showing number + title in chosen language, 1 per row."""
    kb = InlineKeyboardMarkup(row_width=1)
    for ch in CHAPTER_METADATA:
        label = f"Ch {ch['chapter']}. {get_title(ch, lang)}"
        kb.add(InlineKeyboardButton(label, callback_data=f"chapter:{ch['chapter']}"))
    return kb


# ── Formatting ─────────────────────────────────────────────────────────────────
SECTION_CONFIG = {
    "OVERVIEW":       ("📖", "Concept Overview"),
    "TEACHING":       ("🪜", "Step-by-Step Teaching"),
    "ACTIVITY":       ("🎯", "Classroom Activity"),
    "MISCONCEPTIONS": ("⚠️", "Common Misconceptions"),
    "TIPS":           ("💡", "Teacher Tips"),
}

def format_response(raw_text: str, chapter_info: dict | None, lang: str) -> str:
    """Parses SECTION: markers from Gemini output and returns clean Telegram HTML."""
    if chapter_info:
        title   = get_title(chapter_info, lang)
        header  = f"📚 <b>Chapter {chapter_info['chapter']}: {title}</b>"
    else:
        header  = "📚 <b>Topic not found in curriculum</b>"

    divider = "─────────────────────"

    lines   = raw_text.strip().splitlines()
    blocks  = {}
    current = None

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("SECTION:"):
            current = stripped.replace("SECTION:", "").strip().upper()
            blocks[current] = []
        elif current is not None:
            blocks[current].append(line)

    sections_html = []
    for key, (icon, title_label) in SECTION_CONFIG.items():
        content_lines = blocks.get(key, [])

        while content_lines and not content_lines[0].strip():
            content_lines.pop(0)
        while content_lines and not content_lines[-1].strip():
            content_lines.pop()

        if not content_lines:
            continue

        content = "\n".join(content_lines).strip()
        content = (
            content
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        sections_html.append(f"{icon} <b>{title_label}</b>\n{content}")

    if not sections_html:
        fallback = (
            raw_text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        return f"{header}\n{divider}\n\n{fallback}"

    body = f"\n\n{divider}\n\n".join(sections_html)
    return f"{header}\n{divider}\n\n{body}"


def send_long_message(chat_id: int, text: str) -> None:
    """Splits messages longer than Telegram's 4096-char limit."""
    for i in range(0, len(text), 4096):
        bot.send_message(chat_id, text[i : i + 4096], parse_mode="HTML")


# ── /start command ─────────────────────────────────────────────────────────────
@bot.message_handler(commands=["start"])
def handle_start(message: telebot.types.Message) -> None:
    """Resets session and shows the language picker."""
    chat_id = message.chat.id
    user_sessions[chat_id] = {"lang": "en", "chapter": None}  # fresh session

    bot.send_message(
        chat_id,
        "👋 <b>Welcome to TeachClear!</b>\n"
        "Your Grade 6 Maths teaching assistant — <i>Ganita Prakash</i> (NCERT 2024).\n\n"
        "🌐 <b>Please choose your language:</b>",
        parse_mode="HTML",
        reply_markup=language_keyboard(),
    )


# ── /chapter command ───────────────────────────────────────────────────────────
@bot.message_handler(commands=["chapter"])
def handle_chapter_command(message: telebot.types.Message) -> None:
    """Lets a teacher switch chapter mid-session without resetting language."""
    chat_id = message.chat.id
    session = get_session(chat_id)
    lang    = session["lang"]

    bot.send_message(
        chat_id,
        SWITCH_CHAPTER_MSG[lang],
        parse_mode="HTML",
        reply_markup=chapter_keyboard(lang),
    )


# ── Inline button callbacks ────────────────────────────────────────────────────
@bot.callback_query_handler(func=lambda call: call.data.startswith("lang:"))
def handle_language_pick(call: telebot.types.CallbackQuery) -> None:
    """Saves language choice and immediately shows the chapter list."""
    chat_id  = call.message.chat.id
    lang     = call.data.split(":")[1]          # e.g. "ta"
    session  = get_session(chat_id)
    session["lang"] = lang

    lang_info = LANGUAGES[lang]

    # Acknowledge the button tap (removes the loading spinner)
    bot.answer_callback_query(call.id, f"Language set to {lang_info['label']}")

    # Edit the original message to confirm language, then send chapter list
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=(
            f"✅ Language set to <b>{lang_info['label']}</b>\n\n"
            f"{lang_info['greeting']}\n\n"
            f"📚 <b>{lang_info['pick_chapter']}</b>"
        ),
        parse_mode="HTML",
    )

    bot.send_message(
        chat_id,
        f"📚 <b>{lang_info['pick_chapter']}</b>",
        parse_mode="HTML",
        reply_markup=chapter_keyboard(lang),
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("chapter:"))
def handle_chapter_pick(call: telebot.types.CallbackQuery) -> None:
    """Saves chapter choice and prompts the teacher to ask a question."""
    chat_id    = call.message.chat.id
    chapter_n  = int(call.data.split(":")[1])
    session    = get_session(chat_id)
    lang       = session["lang"]

    chapter = get_chapter_by_number(chapter_n)
    if not chapter:
        bot.answer_callback_query(call.id, "Chapter not found.")
        return

    session["chapter"] = chapter

    title = get_title(chapter, lang)

    bot.answer_callback_query(call.id, f"Chapter {chapter_n} selected!")

    # Confirm selection
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=CHAPTER_SELECTED_MSG[lang].format(n=chapter_n, title=title),
        parse_mode="HTML",
    )

    # Prompt to ask a question
    bot.send_message(
        chat_id,
        READY_PROMPT[lang],
        parse_mode="HTML",
    )


# ── Message handler ────────────────────────────────────────────────────────────
@bot.message_handler(func=lambda message: True)
def handle_message(message: telebot.types.Message) -> None:
    """
    Handles teacher queries after language + chapter have been selected.
    If setup is incomplete, nudges the teacher to complete it first.
    """
    chat_id    = message.chat.id
    user_query = message.text.strip()
    session    = get_session(chat_id)
    lang       = session["lang"]
    chapter    = session["chapter"]

    logger.info(
        "Query from %s (lang=%s, chapter=%s): %s",
        message.from_user.username, lang,
        chapter["chapter"] if chapter else "None",
        user_query,
    )

    # Guard: no chapter selected yet
    if chapter is None:
        lang_info = LANGUAGES[lang]
        bot.send_message(
            chat_id,
            f"📚 <b>{lang_info['pick_chapter']}</b>",
            parse_mode="HTML",
            reply_markup=chapter_keyboard(lang),
        )
        return

    bot.send_chat_action(chat_id, "typing")

    try:
        # Force RAG to use the teacher's selected chapter
        context_text, chapter_info = get_relevant_context(
            user_query,
            forced_chapter=chapter,
        )

        prompt       = build_prompt(user_query, context_text, chapter_info, lang)
        raw_response = gemini_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        ).text

        formatted = format_response(raw_response, chapter_info, lang)
        send_long_message(chat_id, formatted)

    except Exception as e:
        logger.error("Error: %s", e, exc_info=True)
        bot.reply_to(
            message,
            "⚠️ Something went wrong. Please try again in a moment.",
        )


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logger.info("🚀 TeachClear bot running (model: %s)...", GEMINI_MODEL)
    bot.infinity_polling()
