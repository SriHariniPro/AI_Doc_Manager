import sys
import os
import json
import uuid

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.document import Document
from services.classification import classify_document
from services.extraction import extract_metadata, generate_summary
from services.vector_store import VectorStore
from utils.file_utils import extract_text

# Initialize vector store
vector_store = VectorStore()

# In-memory document storage (replace with a database in production)
documents = {}
next_id = 1

def process_document(file_path, filename):
    """
    Process a document file and extract all relevant information
    """
    global next_id
    
    # Extract text from the document
    text = extract_text(file_path)
    
    # Classify the document
    doc_type = classify_document(text)
    
    # Extract metadata
    metadata = extract_metadata(text, doc_type)
    
    # Generate summary
    summary = generate_summary(text)
    
    # Create document record
    doc_id = next_id
    next_id += 1
    
    # Store document vector embeddings
    vector_id = vector_store.add_document(
        doc_id=doc_id,
        text=text,
        metadata={
            "filename": filename,
            "type": doc_type,
            "summary": summary
        }
    )
    
    # Create document object
    document = Document(
        id=doc_id,
        filename=filename,
        filepath=file_path,
        doc_type=doc_type,
        metadata=metadata,
        summary=summary,
        text=text,
        vector_id=vector_id
    )
    
    # Store document in memory
    documents[doc_id] = document
    
    return document

def get_document(doc_id):
    """Get a document by ID"""
    return documents.get(doc_id)

def get_all_documents():
    """Get all documents"""
    return list(documents.values())

def search_documents(query, limit=10):
    """
    Search for documents matching the query
    """
    # Use vector store for semantic search
    vector_results = vector_store.search_similar(query, limit=limit)
    
    results = []
    for result in vector_results:
        doc_id = result["doc_id"]
        if doc_id in documents:
            results.append({
                "document": documents[doc_id].to_dict(),
                "similarity": result["score"]
            })
    
    return results

def find_related_documents(doc_id, limit=5):
    """Find documents related to the given document"""
    doc = get_document(doc_id)
    if not doc:
        return []
    
    related = vector_store.find_related(doc_id, doc.text, limit=limit)
    
    results = []
    for result in related:
        related_doc_id = result["doc_id"]
        if related_doc_id in documents:
            results.append({
                "document": documents[related_doc_id].to_dict(),
                "similarity": result["score"]
            })
    
    return results

def delete_document(doc_id):
    """Delete a document"""
    if doc_id in documents:
        # Delete from vector store
        vector_store.delete_document(documents[doc_id].vector_id)
        
        # Delete file if exists
        try:
            if os.path.exists(documents[doc_id].filepath):
                os.remove(documents[doc_id].filepath)
        except:
            pass
        
        # Remove from memory
        del documents[doc_id]
        return True
    
    return False