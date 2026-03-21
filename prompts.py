# prompts.py
# ----------
# Builds the Gemini prompt for every teacher query.
#
# Now accepts a `lang` parameter so Gemini is told explicitly which
# language to respond in, rather than relying on detecting the query language.

# Maps language codes to full language names for the prompt instruction
LANGUAGE_NAMES = {
    "en": "English",
    "ta": "Tamil",
    "hi": "Hindi",
    "te": "Telugu",
    "kn": "Kannada",
}


def build_prompt(
    user_query: str,
    context_text: str,
    chapter_info: dict | None,
    lang: str = "en",
) -> str:
    """
    Constructs the full prompt for Gemini.

    Args:
        user_query   : The teacher's question as typed in Telegram.
        context_text : Textbook excerpt returned by rag.get_relevant_context().
        chapter_info : Matched chapter dict from CHAPTER_METADATA, or None.
        lang         : Language code from user session (e.g. "ta", "hi").

    Returns:
        A fully-formed prompt string ready to pass to the Gemini API.
    """
    language_name = LANGUAGE_NAMES.get(lang, "English")

    if chapter_info:
        # Use English title for the prompt — Gemini understands it best
        chapter_label = f"Chapter {chapter_info['chapter']}: {chapter_info['title']['en']}"
        chapter_desc  = chapter_info["description"]
        context_available = True
    else:
        chapter_label     = "Unknown / Out of Curriculum"
        chapter_desc      = ""
        context_available = False

    if context_available:
        grounding_rule = (
            "You MUST base your response only on the [Textbook Content] provided. "
            "Do NOT introduce concepts, formulas, or examples not present in the excerpt. "
            "If the excerpt does not contain enough information to answer fully, say so "
            "clearly and ask the teacher to refer to the full textbook chapter."
        )
    else:
        grounding_rule = (
            "No matching textbook content was found for this query. "
            "Politely inform the teacher that this topic does not appear to be part of "
            "the Grade 6 Ganita Prakash curriculum, and suggest the appropriate chapter "
            "or grade level if possible. Do NOT answer from general knowledge."
        )

    return f"""You are an expert Grade 6 Mathematics teacher trainer for Indian classrooms.
You support teachers using the NCERT textbook Ganita Prakash (Grade 6, 2024).

Classroom context:
- Class size: 30-50 students
- Mixed ability levels
- Limited resources (chalk, blackboard, basic stationery)

---
Chapter: {chapter_label}
{f"About this chapter: {chapter_desc}" if chapter_desc else ""}

[Textbook Content]
{context_text}
[End of Textbook Content]

---
Teacher's Question:
{user_query}

---
GROUNDING RULE: {grounding_rule}

LANGUAGE RULE: You MUST respond entirely in {language_name}.
Every word of your response — including section content — must be in {language_name}.

CRITICAL FORMATTING RULES — follow exactly:
- Do NOT use any Markdown symbols: no **, no *, no #, no _
- Do NOT use bullet points with - or *
- Use ONLY the section markers below, exactly as written
- Each section marker must be on its own line
- Use plain sentences and numbered points (1. 2. 3.) inside sections

Structure your response using these exact markers:

SECTION:OVERVIEW
Write 3-5 plain sentences explaining the concept as it appears in the textbook.

SECTION:TEACHING
Write 3-5 numbered steps a teacher can follow in class.

SECTION:ACTIVITY
Describe one low-resource classroom activity in plain sentences.

SECTION:MISCONCEPTIONS
Write 2-3 numbered common student mistakes and how to address each.

SECTION:TIPS
Write 2-3 numbered practical tips for the teacher.
"""
