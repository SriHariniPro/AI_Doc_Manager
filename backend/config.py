import os

# Application settings
DEBUG = True
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'docx', 'txt'}

# Vector DB settings
CHROMA_PERSIST_DIRECTORY = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'chroma_db')

# NLP settings
NLP_MODEL = "en_core_web_md"