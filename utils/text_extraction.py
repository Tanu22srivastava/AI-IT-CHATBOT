from PyPDF2 import PdfReader
from docx import Document

def extract_text_from_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    except Exception as e:
        print(f"Error extracting text from PDF {file_path}: {e}")
        return ""

def extract_text_from_docx(file_path):
    try:
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"Error extracting text from DOCX {file_path}: {e}")
        return ""