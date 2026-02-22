import docx
import os

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

file_path = r'd:\ML\Agentic AI\AGA\Bnaking-Multi-Agent-System\Autonomous_Banking_Analytics_Master_Enterprise_Documentation.docx'
if os.path.exists(file_path):
    text = extract_text_from_docx(file_path)
    with open('fsd_content.txt', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Extraction successful. Content saved to fsd_content.txt")
else:
    print(f"File not found: {file_path}")
