import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from werkzeug.utils import secure_filename
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file):
    """Save uploaded file to disk and return the path"""
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    return filepath, filename

def extract_text(file_path):
    """Extract text from various file formats"""
    if file_path.endswith('.pdf'):
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        return text
    elif file_path.endswith(('.png', '.jpg', '.jpeg')):
        return pytesseract.image_to_string(Image.open(file_path))
    elif file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    elif file_path.endswith('.docx'):
        try:
            import docx
            doc = docx.Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except ImportError:
            return "DOCX support requires python-docx library."
    return ""