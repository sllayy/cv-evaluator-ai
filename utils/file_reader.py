import fitz  # PyMuPDF
from docx import Document
import os

def extract_text_from_pdf(pdf_path):
    """PDF dosyasından metni çıkarır"""
    print(f"[DEBUG] PDF okunuyor: {pdf_path}")
    try:
        text = ""
        with fitz.open(pdf_path) as doc:
            for i, page in enumerate(doc):
                page_text = page.get_text()
                print(f"[DEBUG] Sayfa {i+1} uzunluğu: {len(page_text)} karakter")
                text += page_text
        return text
    except Exception as e:
        print(f"[HATA] PDF okuma hatası ({pdf_path}): {e}")
        return ""

def extract_text_from_docx(docx_path):
    """DOCX dosyasından metni çıkarır"""
    print(f"[DEBUG] DOCX okunuyor: {docx_path}")
    try:
        doc = Document(docx_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        print(f"[DEBUG] DOCX metin uzunluğu: {len(text)} karakter")
        return text
    except Exception as e:
        print(f"[HATA] DOCX okuma hatası ({docx_path}): {e}")
        return ""

def read_cv(file_path):
    """Dosya türüne göre uygun okuma fonksiyonunu çağırır"""
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    else:
        print(f"[UYARI] Desteklenmeyen dosya türü: {file_path}")
        return ""
