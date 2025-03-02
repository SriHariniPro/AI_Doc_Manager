from collections import Counter
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.document_service import get_all_documents

def get_document_type_stats():
    """Get distribution of document types"""
    documents = get_all_documents()
    types = [doc.type for doc in documents]
    type_counts = Counter(types)
    
    return {
        "labels": list(type_counts.keys()),
        "values": list(type_counts.values())
    }

def get_entity_distribution():
    """Get distribution of entity types across all documents"""
    documents = get_all_documents()
    
    entity_types = []
    for doc in documents:
        for entity in doc.metadata.get("entities", []):
            entity_types.append(entity.get("type"))
    
    type_counts = Counter(entity_types)
    
    return {
        "labels": list(type_counts.keys()),
        "values": list(type_counts.values())
    }

def get_keyword_frequency():
    """Get frequency of keywords across all documents"""
    documents = get_all_documents()
    
    all_keywords = []
    for doc in documents:
        all_keywords.extend(doc.metadata.get("key_terms", []))
    
    keyword_counts = Counter(all_keywords)
    
    # Get top 20 keywords
    top_keywords = keyword_counts.most_common(20)
    
    return {
        "keywords": [k for k, v in top_keywords],
        "frequencies": [v for k, v in top_keywords]
    }

def get_document_stats():
    """Get general statistics about the document collection"""
    documents = get_all_documents()
    
    # Count documents by type
    doc_types = Counter([doc.type for doc in documents])
    
    # Count entities by type
    entity_types = Counter()
    for doc in documents:
        for entity in doc.metadata.get("entities", []):
            entity_types[entity.get("type")] += 1
    
    return {
        "total_documents": len(documents),
        "document_types": dict(doc_types),
        "entity_types": dict(entity_types)
    }