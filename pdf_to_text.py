from PyPDF2 import PdfReader
import os

INPUT_FOLDER = "textbook_raw"
OUTPUT_FOLDER = "textbook_chunks"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

for file in os.listdir(INPUT_FOLDER):
    if file.endswith(".pdf"):
        reader = PdfReader(os.path.join(INPUT_FOLDER, file))
        
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        output_file = file.replace(".pdf", ".txt")
        
        with open(os.path.join(OUTPUT_FOLDER, output_file), "w", encoding="utf-8") as f:
            f.write(text)

print("✅ PDFs converted to text files")