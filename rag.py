# rag.py
# ------
# Retrieves textbook content for a teacher's query.
#
# Two retrieval modes:
#   1. forced_chapter — teacher has selected a chapter via the inline menu.
#      Always load that chapter's .txt file directly. No scoring needed.
#   2. Auto-detect    — score chapters by keyword overlap (fallback only,
#      used if forced_chapter is not provided).
#
# Folder structure expected:
#   textbook_chunks/
#       chapter_1.txt
#       chapter_2.txt
#       ...  (named chapter_<N>.txt)

import os
from metadata import CHAPTER_METADATA

BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
TEXTBOOK_FOLDER = os.path.join(BASE_DIR, "textbook_chunks")
MAX_CONTEXT_CHARS = 3000


def _load_chapter_file(chapter: dict) -> str | None:
    """
    Reads the .txt file for a given chapter dict.
    Returns file content as a string, or None if the file doesn't exist.
    """
    filename = os.path.join(TEXTBOOK_FOLDER, f"chapter_{chapter['chapter']}.txt")
    if not os.path.exists(filename):
        return None
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()


def _find_chapter_by_keywords(query: str) -> dict | None:
    """
    Fallback: score every chapter by keyword overlap and return the best match.
    Returns None if no keywords match.
    """
    query_lower = query.lower()
    best_score  = 0
    best_chapter = None

    for chapter in CHAPTER_METADATA:
        score = sum(1 for kw in chapter["keywords"] if kw in query_lower)
        if score > best_score:
            best_score  = score
            best_chapter = chapter

    return best_chapter if best_score > 0 else None


def get_relevant_context(
    query: str,
    forced_chapter: dict | None = None,
) -> tuple[str, dict | None]:
    """
    Main entry point called by TeachClear.py.

    Args:
        query           : The teacher's question.
        forced_chapter  : Chapter dict from the user's session selection.
                          If provided, skips keyword scoring entirely.

    Returns:
        (context_text, chapter_info)
    """
    # ── Mode 1: Teacher selected a chapter — use it directly ──
    if forced_chapter is not None:
        content = _load_chapter_file(forced_chapter)
        if content is None:
            return (
                f"Chapter {forced_chapter['chapter']} was selected, but its textbook "
                f"file was not found in {TEXTBOOK_FOLDER}/. "
                f"Please add chapter_{forced_chapter['chapter']}.txt to the folder.",
                forced_chapter,
            )
        if len(content) > MAX_CONTEXT_CHARS:
            content = (
                content[:MAX_CONTEXT_CHARS]
                + "\n\n[Note: Content was truncated. Answer only from the excerpt above.]"
            )
        return content, forced_chapter

    # ── Mode 2: No chapter selected — auto-detect by keyword ──
    chapter = _find_chapter_by_keywords(query)
    if chapter is None:
        return "No matching chapter found in the textbook for this query.", None

    content = _load_chapter_file(chapter)
    if content is None:
        return (
            f"Chapter {chapter['chapter']} was identified as relevant, but its file "
            f"was not found in {TEXTBOOK_FOLDER}/.",
            chapter,
        )

    if len(content) > MAX_CONTEXT_CHARS:
        content = (
            content[:MAX_CONTEXT_CHARS]
            + "\n\n[Note: Content was truncated. Answer only from the excerpt above.]"
        )
    return content, chapter
