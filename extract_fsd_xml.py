import zipfile
import xml.etree.ElementTree as ET
import os

def extract_text_from_docx_xml(file_path):
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    text = []
    try:
        with zipfile.ZipFile(file_path) as z:
            xml_content = z.read('word/document.xml')
            tree = ET.fromstring(xml_content)
            for para in tree.findall('.//w:p', ns):
                para_text = []
                for node in para.findall('.//w:t', ns):
                    if node.text:
                        para_text.append(node.text)
                text.append(''.join(para_text))
    except Exception as e:
        return f"Error: {e}"
    return '\n'.join(text)

file_path = r'd:\ML\Agentic AI\AGA\Bnaking-Multi-Agent-System\Autonomous_Banking_Analytics_Master_Enterprise_Documentation.docx'
if os.path.exists(file_path):
    text = extract_text_from_docx_xml(file_path)
    with open('fsd_content.txt', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Extraction successful using XML parsing. Content saved to fsd_content.txt")
else:
    print(f"File not found: {file_path}")
