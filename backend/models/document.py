from datetime import datetime

class Document:
    def __init__(self, id, filename, filepath, doc_type, metadata, summary, text, vector_id=None):
        self.id = id
        self.filename = filename
        self.filepath = filepath
        self.type = doc_type
        self.metadata = metadata
        self.summary = summary
        self.text = text
        self.vector_id = vector_id
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "filepath": self.filepath,
            "type": self.type,
            "metadata": self.metadata,
            "summary": self.summary,
            "text": self.text[:1000] + "..." if len(self.text) > 1000 else self.text,
            "vector_id": self.vector_id,
            "created_at": self.created_at
        }