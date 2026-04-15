# TeachClear.py
# -------------
# Telegram bot for TeachClear — Grade 6 Mathematics teaching assistant.
# Uses pyTelegramBotAPI (telebot) — synchronous polling.
# Gemini API via the google-genai SDK.
#
# USER FLOW:
#   /start    →  language picker → chapter list → teacher types query → Gemini responds
#   /chapter  →  chapter list again (switch anytime)
#   /help     →  how to use TeachClear
#   /examples →  example questions across all chapters
#
# MISMATCH DETECTION:
#   If teacher's question keywords match a different chapter than the one selected,
#   bot warns and offers two inline buttons:
#     [Answer from detected chapter — permanently switches session]
#     [Answer from selected chapter — keeps current session]
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

from rag import get_relevant_context, _find_chapter_by_keywords
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
# { chat_id: { "lang": "ta", "chapter": <chapter_dict>, "pending": <state> } }
# "pending" stores a mismatch state while waiting for teacher's decision:
# { "query": str, "selected": chapter_dict, "detected": chapter_dict }
user_sessions: dict[int, dict] = {}

def get_session(chat_id: int) -> dict:
    if chat_id not in user_sessions:
        user_sessions[chat_id] = {"lang": "en", "chapter": None, "pending": None}
    return user_sessions[chat_id]


# ── Static content ─────────────────────────────────────────────────────────────
HELP_TEXT = """
👋 <b>How to use TeachClear</b>

TeachClear helps Grade 6 Maths teachers with curriculum-aligned teaching support.

<b>Getting started:</b>
1. Send /start to choose your language
2. Pick a chapter from the list
3. Type your teaching question

<b>What you can ask:</b>
✏️ How do I explain this concept simply?
🎯 What activity can I do with limited resources?
⚠️ What mistakes do students usually make here?
🪜 Give me a step-by-step way to teach this topic

<b>What TeachClear gives you:</b>
📖 Concept overview grounded in the textbook
🪜 Step-by-step teaching approach
🎯 A classroom activity
⚠️ Common student misconceptions
💡 Practical teacher tips

<b>Useful commands:</b>
/start — restart and pick language and chapter
/chapter — switch to a different chapter
/help — show this message
/examples — see example questions to try

<b>Note:</b> TeachClear responds only based on the NCERT Ganita Prakash textbook content. It will not answer questions outside the Grade 6 curriculum.
"""

EXAMPLES_TEXT = """
💡 <b>Example questions to try</b>

Here are some questions you can ask TeachClear — pick any chapter first, then try a question from that chapter!

📘 <b>Ch 1 — Patterns in Mathematics</b>
→ How do I introduce triangular numbers to students visually?
→ What activity can I use to show the sum of odd numbers pattern?

📘 <b>Ch 2 — Lines and Angles</b>
→ How do I teach the difference between a ray and a line segment?
→ What are common mistakes students make when measuring angles?

📘 <b>Ch 3 — Number Play</b>
→ How do I explain Kaprekar numbers in a fun way?
→ What classroom activity can I use to explore palindromes?

📘 <b>Ch 4 — Data Handling and Presentation</b>
→ How do I teach students to draw a bar graph step by step?
→ What real-life examples can I use for data collection?

📘 <b>Ch 5 — Prime Time</b>
→ How do I explain the Sieve of Eratosthenes simply?
→ What activity helps students understand HCF and LCM?

📘 <b>Ch 6 — Perimeter and Area</b>
→ How do I help students understand the difference between perimeter and area?
→ What is a good hands-on activity for measuring area using unit squares?

📘 <b>Ch 7 — Fractions</b>
→ How do I explain equivalent fractions using a visual?
→ What mistakes do students make when adding unlike fractions?

📘 <b>Ch 8 — Playing with Constructions</b>
→ How do I teach students to construct a perpendicular bisector step by step?
→ What common errors do students make when using a compass?

📘 <b>Ch 9 — Symmetry</b>
→ How do I introduce line symmetry using everyday objects?
→ What activity helps students find lines of symmetry in regular polygons?

📘 <b>Ch 10 — The Other Side of Zero</b>
→ How do I explain negative numbers using a real-life context?
→ What is a good way to teach addition of integers on a number line?
"""


# ── Keyboard builders ──────────────────────────────────────────────────────────
def language_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton(info["label"], callback_data=f"lang:{code}")
        for code, info in LANGUAGES.items()
    ]
    kb.add(*buttons)
    return kb


def chapter_keyboard(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    for ch in CHAPTER_METADATA:
        label = f"Ch {ch['chapter']}. {get_title(ch, lang)}"
        kb.add(InlineKeyboardButton(label, callback_data=f"chapter:{ch['chapter']}"))
    return kb


def mismatch_keyboard(detected_n: int, selected_n: int) -> InlineKeyboardMarkup:
    """Two buttons shown when a chapter mismatch is detected."""
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(
            f"✅ Switch to Chapter {detected_n} and answer",
            callback_data=f"mismatch:switch:{detected_n}",
        ),
        InlineKeyboardButton(
            f"📖 Answer using Chapter {selected_n} (current)",
            callback_data=f"mismatch:keep:{selected_n}",
        ),
    )
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
        title  = get_title(chapter_info, lang)
        header = f"📚 <b>Chapter {chapter_info['chapter']}: {title}</b>"
    else:
        header = "📚 <b>Topic not found in curriculum</b>"

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
    for i in range(0, len(text), 4096):
        bot.send_message(chat_id, text[i : i + 4096], parse_mode="HTML")


# ── Gemini call ────────────────────────────────────────────────────────────────
def call_gemini_and_respond(chat_id: int, user_query: str, chapter: dict, lang: str) -> None:
    """Retrieves context, calls Gemini, formats and sends the response."""
    context_text, chapter_info = get_relevant_context(
        user_query, forced_chapter=chapter
    )
    prompt       = build_prompt(user_query, context_text, chapter_info, lang)
    raw_response = gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    ).text
    formatted = format_response(raw_response, chapter_info, lang)
    send_long_message(chat_id, formatted)


# ── /start ─────────────────────────────────────────────────────────────────────
@bot.message_handler(commands=["start"])
def handle_start(message: telebot.types.Message) -> None:
    chat_id = message.chat.id
    user_sessions[chat_id] = {"lang": "en", "chapter": None, "pending": None}
    bot.send_message(
        chat_id,
        "👋 <b>Welcome to TeachClear!</b>\n"
        "Your Grade 6 Maths teaching assistant — <i>Ganita Prakash</i> (NCERT 2024).\n\n"
        "🌐 <b>Please choose your language:</b>",
        parse_mode="HTML",
        reply_markup=language_keyboard(),
    )


# ── /chapter ───────────────────────────────────────────────────────────────────
@bot.message_handler(commands=["chapter"])
def handle_chapter_command(message: telebot.types.Message) -> None:
    chat_id = message.chat.id
    session = get_session(chat_id)
    lang    = session["lang"]
    bot.send_message(
        chat_id,
        SWITCH_CHAPTER_MSG[lang],
        parse_mode="HTML",
        reply_markup=chapter_keyboard(lang),
    )


# ── /help ──────────────────────────────────────────────────────────────────────
@bot.message_handler(commands=["help"])
def handle_help(message: telebot.types.Message) -> None:
    bot.send_message(message.chat.id, HELP_TEXT, parse_mode="HTML")


# ── /examples ──────────────────────────────────────────────────────────────────
@bot.message_handler(commands=["examples"])
def handle_examples(message: telebot.types.Message) -> None:
    bot.send_message(message.chat.id, EXAMPLES_TEXT, parse_mode="HTML")


# ── Inline button callbacks ────────────────────────────────────────────────────
@bot.callback_query_handler(func=lambda call: call.data.startswith("lang:"))
def handle_language_pick(call: telebot.types.CallbackQuery) -> None:
    chat_id  = call.message.chat.id
    lang     = call.data.split(":")[1]
    session  = get_session(chat_id)
    session["lang"] = lang
    lang_info = LANGUAGES[lang]
    bot.answer_callback_query(call.id, f"Language set to {lang_info['label']}")
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
    chat_id   = call.message.chat.id
    chapter_n = int(call.data.split(":")[1])
    session   = get_session(chat_id)
    lang      = session["lang"]
    chapter   = get_chapter_by_number(chapter_n)
    if not chapter:
        bot.answer_callback_query(call.id, "Chapter not found.")
        return
    session["chapter"] = chapter
    session["pending"] = None
    title = get_title(chapter, lang)
    bot.answer_callback_query(call.id, f"Chapter {chapter_n} selected!")
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=CHAPTER_SELECTED_MSG[lang].format(n=chapter_n, title=title),
        parse_mode="HTML",
    )
    bot.send_message(chat_id, READY_PROMPT[lang], parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data.startswith("mismatch:"))
def handle_mismatch_decision(call: telebot.types.CallbackQuery) -> None:
    """
    Handles the teacher's decision when a chapter mismatch is detected.
    mismatch:switch:<n> → permanently switch to detected chapter and answer
    mismatch:keep:<n>   → answer using currently selected chapter, no switch
    """
    chat_id = call.message.chat.id
    session = get_session(chat_id)
    pending = session.get("pending")
    lang    = session["lang"]

    if not pending:
        bot.answer_callback_query(call.id, "Session expired. Please ask your question again.")
        return

    parts    = call.data.split(":")
    decision = parts[1]   # "switch" or "keep"
    chapter_n = int(parts[2])

    bot.answer_callback_query(call.id)

    if decision == "switch":
        # Permanently switch session to the detected chapter
        new_chapter = get_chapter_by_number(chapter_n)
        session["chapter"] = new_chapter
        title = get_title(new_chapter, lang)
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=f"✅ Switched to <b>Chapter {chapter_n}: {title}</b>",
            parse_mode="HTML",
        )
        chapter_to_use = new_chapter
    else:
        # Keep the currently selected chapter
        chapter_to_use = pending["selected"]
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=f"📖 Answering using <b>Chapter {chapter_to_use['chapter']}: {get_title(chapter_to_use, lang)}</b>",
            parse_mode="HTML",
        )

    # Clear pending state
    session["pending"] = None

    # Now call Gemini and respond
    bot.send_chat_action(chat_id, "typing")
    try:
        call_gemini_and_respond(chat_id, pending["query"], chapter_to_use, lang)
    except Exception as e:
        logger.error("Error after mismatch decision: %s", e, exc_info=True)
        bot.send_message(chat_id, "⚠️ AI is busy right now. Please try again in a moment.")


# ── Message handler ────────────────────────────────────────────────────────────
@bot.message_handler(func=lambda message: True)
def handle_message(message: telebot.types.Message) -> None:
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

    # ── Mismatch detection ──
    # Score the query against all chapters to see if a different chapter
    # is a better match than the currently selected one
    detected = _find_chapter_by_keywords(user_query)

    if (
        detected is not None
        and detected["chapter"] != chapter["chapter"]
    ):
        # Mismatch found — store pending state and ask teacher what to do
        session["pending"] = {
            "query":    user_query,
            "selected": chapter,
            "detected": detected,
        }
        detected_title = get_title(detected, lang)
        selected_title = get_title(chapter, lang)

        bot.send_message(
            chat_id,
            f"⚠️ Your question seems to be about "
            f"<b>Chapter {detected['chapter']}: {detected_title}</b>, "
            f"but you have <b>Chapter {chapter['chapter']}: {selected_title}</b> selected.\n\n"
            f"What would you like me to do?",
            parse_mode="HTML",
            reply_markup=mismatch_keyboard(detected["chapter"], chapter["chapter"]),
        )
        return

    # ── No mismatch — answer normally ──
    bot.send_chat_action(chat_id, "typing")
    try:
        call_gemini_and_respond(chat_id, user_query, chapter, lang)
    except Exception as e:
        logger.error("Error handling message: %s", e, exc_info=True)
        bot.reply_to(
            message,
            "⚠️ Something went wrong. Please try again in a moment.",
        )


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logger.info("🚀 TeachClear bot running (model: %s)...", GEMINI_MODEL)
    bot.infinity_polling()
