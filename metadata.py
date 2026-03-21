# metadata.py
# -----------
# Curriculum metadata for TeachClear — Grade 6 Mathematics
# Textbook: Ganita Prakash (NCERT, 2024 edition, Reprint 2025-26)
#
# Each entry maps to a .txt file in textbook_chunks/:
#   chapter_1.txt  →  Chapter 1: Patterns in Mathematics, etc.
#
# TRANSLATIONS: Chapter titles are provided in all 5 supported languages
# so the chapter selection menu can be shown in the teacher's chosen language.

# ── Language config ────────────────────────────────────────────────────────────

LANGUAGES = {
    "en": {"label": "🇬🇧 English",  "greeting": "Welcome to TeachClear!",      "pick_chapter": "Please pick a chapter to begin:"},
    "ta": {"label": "🇮🇳 Tamil",    "greeting": "TeachClear-க்கு வரவேற்கிறோம்!", "pick_chapter": "தொடங்க ஒரு அத்தியாயத்தை தேர்ந்தெடுக்கவும்:"},
    "hi": {"label": "🇮🇳 Hindi",    "greeting": "TeachClear में आपका स्वागत है!", "pick_chapter": "शुरू करने के लिए एक अध्याय चुनें:"},
    "te": {"label": "🇮🇳 Telugu",   "greeting": "TeachClear కి స్వాగతం!",        "pick_chapter": "ప్రారంభించడానికి ఒక అధ్యాయాన్ని ఎంచుకోండి:"},
    "kn": {"label": "🇮🇳 Kannada",  "greeting": "TeachClear ಗೆ ಸ್ವಾಗತ!",         "pick_chapter": "ಪ್ರಾರಂಭಿಸಲು ಒಂದು ಅಧ್ಯಾಯವನ್ನು ಆರಿಸಿ:"},
}

LANGUAGE_PICKER_PROMPT = {
    "en": "🌐 Please choose your language:",
    "ta": "🌐 உங்கள் மொழியை தேர்ந்தெடுக்கவும்:",
    "hi": "🌐 कृपया अपनी भाषा चुनें:",
    "te": "🌐 దయచేసి మీ భాషను ఎంచుకోండి:",
    "kn": "🌐 ದಯವಿಟ್ಟು ನಿಮ್ಮ ಭಾಷೆಯನ್ನು ಆರಿಸಿ:",
}

# Shown after a chapter is selected
CHAPTER_SELECTED_MSG = {
    "en": "✅ You've selected <b>Chapter {n}: {title}</b>.\n\nAsk me anything about teaching this chapter!",
    "ta": "✅ <b>அத்தியாயம் {n}: {title}</b> தேர்ந்தெடுக்கப்பட்டது.\n\nஇந்த அத்தியாயத்தை கற்பிப்பதைப் பற்றி என்னிடம் கேளுங்கள்!",
    "hi": "✅ आपने <b>अध्याय {n}: {title}</b> चुना है।\n\nइस अध्याय को पढ़ाने के बारे में मुझसे कुछ भी पूछें!",
    "te": "✅ మీరు <b>అధ్యాయం {n}: {title}</b> ఎంచుకున్నారు.\n\nఈ అధ్యాయాన్ని బోధించడం గురించి నన్ను ఏదైనా అడగండి!",
    "kn": "✅ ನೀವು <b>ಅಧ್ಯಾಯ {n}: {title}</b> ಆಯ್ಕೆ ಮಾಡಿದ್ದೀರಿ.\n\nಈ ಅಧ್ಯಾಯವನ್ನು ಕಲಿಸುವ ಬಗ್ಗೆ ನನ್ನನ್ನು ಏನಾದರೂ ಕೇಳಿ!",
}

# Shown when user types /chapter to switch
SWITCH_CHAPTER_MSG = {
    "en": "📚 Switch chapter — pick a new one below:",
    "ta": "📚 அத்தியாயத்தை மாற்றவும் — கீழே புதியதை தேர்ந்தெடுக்கவும்:",
    "hi": "📚 अध्याय बदलें — नीचे से नया चुनें:",
    "te": "📚 అధ్యాయాన్ని మార్చండి — క్రింద కొత్తది ఎంచుకోండి:",
    "kn": "📚 ಅಧ್ಯಾಯ ಬದಲಾಯಿಸಿ — ಕೆಳಗೆ ಹೊಸದನ್ನು ಆರಿಸಿ:",
}

# Prompt shown while waiting for a question
READY_PROMPT = {
    "en": "💬 Go ahead — type your teaching question!",
    "ta": "💬 தொடரவும் — உங்கள் கற்பித்தல் கேள்வியை தட்டச்சு செய்யுங்கள்!",
    "hi": "💬 आगे बढ़ें — अपना शिक्षण प्रश्न टाइप करें!",
    "te": "💬 ముందుకు వెళ్ళండి — మీ బోధన ప్రశ్నను టైప్ చేయండి!",
    "kn": "💬 ಮುಂದುವರಿಯಿರಿ — ನಿಮ್ಮ ಬೋಧನಾ ಪ್ರಶ್ನೆಯನ್ನು ಟೈಪ್ ಮಾಡಿ!",
}

# ── Chapter metadata ───────────────────────────────────────────────────────────

CHAPTER_METADATA = [
    {
        "chapter": 1,
        "title": {
            "en": "Patterns in Mathematics",
            "ta": "கணிதத்தில் வடிவங்கள்",
            "hi": "गणित में पैटर्न",
            "te": "గణితంలో నమూనాలు",
            "kn": "ಗಣಿತದಲ್ಲಿ ಮಾದರಿಗಳು",
        },
        "keywords": [
            "patterns", "number patterns", "sequences", "odd numbers", "even numbers",
            "triangular numbers", "square numbers", "cube numbers", "number sequences",
            "visual patterns", "shape patterns", "virahanka", "fibonacci",
            "powers of 2", "powers of 3", "counting numbers",
            "complete graphs", "stacked squares", "stacked triangles",
            "koch snowflake", "regular polygons", "number theory",
            "sum of odd numbers", "what is mathematics",
        ],
        "description": (
            "Introduction to mathematics as the study of patterns. "
            "Covers number sequences (counting, odd, even, triangular, square, cube, "
            "Virahānka, powers of 2 and 3), visualising sequences with pictures, "
            "relations among sequences, and shape sequences (regular polygons, "
            "complete graphs, stacked squares and triangles, Koch snowflake)."
        ),
    },
    {
        "chapter": 2,
        "title": {
            "en": "Lines and Angles",
            "ta": "கோடுகள் மற்றும் கோணங்கள்",
            "hi": "रेखाएँ और कोण",
            "te": "రేఖలు మరియు కోణాలు",
            "kn": "ರೇಖೆಗಳು ಮತ್ತು ಕೋನಗಳು",
        },
        "keywords": [
            "lines", "angles", "line segment", "ray", "point",
            "acute angle", "right angle", "obtuse angle", "straight angle",
            "reflex angle", "measure angles", "protractor",
            "parallel lines", "perpendicular lines", "intersecting lines",
            "vertically opposite angles", "linear pair", "transversal",
        ],
        "description": (
            "Basic geometry: points, lines, rays, line segments. "
            "Types of angles (acute, right, obtuse, straight, reflex). "
            "Measuring and drawing angles with a protractor. "
            "Pairs of angles: linear pair, vertically opposite. "
            "Parallel and perpendicular lines."
        ),
    },
    {
        "chapter": 3,
        "title": {
            "en": "Number Play",
            "ta": "எண்களுடன் விளையாட்டு",
            "hi": "संख्याओं से खेलना",
            "te": "సంఖ్యలతో ఆట",
            "kn": "ಸಂಖ್ಯೆಗಳ ಆಟ",
        },
        "keywords": [
            "numbers", "digit sum", "palindrome", "kaprekar", "estimation",
            "number puzzles", "supercells", "number line", "collatz conjecture",
            "mental math", "place value", "magic squares",
            "interesting numbers", "digit patterns",
        ],
        "description": (
            "Exploring numbers through puzzles, games, and interesting properties. "
            "Topics include digit sums, palindromes, Kaprekar numbers, supercells, "
            "Collatz conjecture, estimation, and mental arithmetic."
        ),
    },
    {
        "chapter": 4,
        "title": {
            "en": "Data Handling and Presentation",
            "ta": "தரவு கையாளுதல் மற்றும் விளக்கம்",
            "hi": "डेटा प्रबंधन और प्रस्तुति",
            "te": "డేటా నిర్వహణ మరియు ప్రదర్శన",
            "kn": "ಡೇಟಾ ನಿರ್ವಹಣೆ ಮತ್ತು ಪ್ರಸ್ತುತಿ",
        },
        "keywords": [
            "data", "data handling", "bar graph", "pictograph", "table",
            "data interpretation", "data representation", "charts", "tally marks",
            "organising data", "reading graphs", "frequency", "data collection",
        ],
        "description": (
            "Collecting, organising, representing, and interpreting data. "
            "Tally marks, frequency tables, pictographs, and bar graphs. "
            "Reading and drawing graphs to answer questions."
        ),
    },
    {
        "chapter": 5,
        "title": {
            "en": "Prime Time",
            "ta": "பகா எண்களின் நேரம்",
            "hi": "अभाज्य समय",
            "te": "ప్రైమ్ టైమ్",
            "kn": "ಅವಿಭಾಜ್ಯ ಸಂಖ್ಯೆಗಳ ಸಮಯ",
        },
        "keywords": [
            "prime numbers", "composite numbers", "factors", "multiples",
            "prime factorisation", "hcf", "lcm", "divisibility", "divisibility rules",
            "common factors", "common multiples", "factor tree",
            "highest common factor", "lowest common multiple",
            "sieve of eratosthenes", "co-prime",
        ],
        "description": (
            "Prime and composite numbers. Factors and multiples. "
            "Divisibility rules. Prime factorisation and factor trees. "
            "HCF and LCM with applications. Sieve of Eratosthenes."
        ),
    },
    {
        "chapter": 6,
        "title": {
            "en": "Perimeter and Area",
            "ta": "சுற்றளவு மற்றும் பரப்பளவு",
            "hi": "परिमाप और क्षेत्रफल",
            "te": "చుట్టుకొలత మరియు వైశాల్యం",
            "kn": "ಪರಿಧಿ ಮತ್ತು ವಿಸ್ತೀರ್ಣ",
        },
        "keywords": [
            "perimeter", "area", "rectangle", "square", "triangle",
            "boundary", "measurement", "length", "breadth",
            "area of rectangle", "area of square",
            "perimeter of rectangle", "perimeter of square",
            "unit squares", "square centimetre", "square metre", "irregular shapes",
        ],
        "description": (
            "Measuring perimeter (boundary length) and area (surface covered). "
            "Formulas for rectangles and squares. "
            "Estimating area of irregular shapes using unit squares."
        ),
    },
    {
        "chapter": 7,
        "title": {
            "en": "Fractions",
            "ta": "பின்னங்கள்",
            "hi": "भिन्न",
            "te": "భిన్నాలు",
            "kn": "ಭಿನ್ನರಾಶಿಗಳು",
        },
        "keywords": [
            "fractions", "numerator", "denominator", "equivalent fractions",
            "fraction addition", "fraction subtraction", "compare fractions",
            "proper fraction", "improper fraction", "mixed numbers", "mixed fractions",
            "simplest form", "like fractions", "unlike fractions",
            "fraction on number line", "unit fraction",
        ],
        "description": (
            "Fractions as parts of a whole and collection. "
            "Proper, improper, and mixed fractions. Equivalent fractions. "
            "Comparing fractions. Fractions on a number line. "
            "Addition and subtraction with like and unlike denominators."
        ),
    },
    {
        "chapter": 8,
        "title": {
            "en": "Playing with Constructions",
            "ta": "வடிவியல் வரைதல்",
            "hi": "रचनाओं से खेलना",
            "te": "నిర్మాణాలతో ఆడటం",
            "kn": "ರಚನೆಗಳೊಂದಿಗೆ ಆಟ",
        },
        "keywords": [
            "construction", "geometry construction", "compass", "ruler",
            "perpendicular bisector", "angle bisector", "construct angles",
            "construct triangles", "arc", "radius",
            "constructing parallel lines", "set square",
        ],
        "description": (
            "Geometric constructions using compass and ruler. "
            "Drawing circles, perpendicular bisectors, and angle bisectors. "
            "Constructing specific angles and triangles."
        ),
    },
    {
        "chapter": 9,
        "title": {
            "en": "Symmetry",
            "ta": "சமச்சீர்நிலை",
            "hi": "सममिति",
            "te": "సమరూపత",
            "kn": "ಸಮಮಿತಿ",
        },
        "keywords": [
            "symmetry", "line symmetry", "reflection", "mirror image",
            "axis of symmetry", "lines of symmetry", "symmetrical shapes",
            "rotational symmetry", "order of symmetry", "symmetric figures",
        ],
        "description": (
            "Line symmetry and lines of symmetry in 2D shapes. "
            "Reflection and mirror images. Symmetry in regular polygons. "
            "Introduction to rotational symmetry."
        ),
    },
    {
        "chapter": 10,
        "title": {
            "en": "The Other Side of Zero",
            "ta": "பூஜ்யத்தின் மறுபக்கம்",
            "hi": "शून्य के पार",
            "te": "సున్నా యొక్క మరో వైపు",
            "kn": "ಸೊನ್ನೆಯ ಇನ್ನೊಂದು ಬದಿ",
        },
        "keywords": [
            "integers", "negative numbers", "positive numbers",
            "number line integers", "addition of integers", "subtraction of integers",
            "zero", "opposite numbers", "below zero", "temperature",
            "real life integers", "directed numbers",
        ],
        "description": (
            "Negative numbers through real-life contexts (temperature, floors below "
            "ground, debt). Integers on a number line. Ordering integers. "
            "Addition and subtraction of integers."
        ),
    },
]

# ── Lookup helpers ─────────────────────────────────────────────────────────────
def get_chapter_by_number(n: int) -> dict | None:
    """Return chapter dict for a given chapter number (1–10), or None."""
    for ch in CHAPTER_METADATA:
        if ch["chapter"] == n:
            return ch
    return None


def get_title(chapter: dict, lang: str) -> str:
    """Return the chapter title in the given language, falling back to English."""
    return chapter["title"].get(lang, chapter["title"]["en"])
