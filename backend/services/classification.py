import re
import spacy
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import NLP_MODEL

# Load spaCy model
nlp = spacy.load(NLP_MODEL)

def classify_document(text):
    """
    Classify document type based on text content patterns
    """
    # Simple rule-based classification
    if re.search(r'invoice|payment|amount due|bill|total amount|tax', text, re.IGNORECASE):
        return "Invoice"
    elif re.search(r'contract|agreement|terms|parties|obligations|hereby agree', text, re.IGNORECASE):
        return "Contract"
    elif re.search(r'resume|cv|experience|skills|education|employment|objective', text, re.IGNORECASE):
        return "Resume"
    elif re.search(r'patient|diagnosis|treatment|medical|doctor|hospital|health', text, re.IGNORECASE):
        return "Medical"
    elif re.search(r'court|plaintiff|defendant|legal|law|attorney|judge|case', text, re.IGNORECASE):
        return "Legal"
    elif re.search(r'financial|statement|balance sheet|profit|loss|assets|liabilities', text, re.IGNORECASE):
        return "Financial"
    return "General"

def identify_document_domain(text):
    """
    Identify specific domain for the document
    """
    # Medical domain
    if re.search(r'patient|diagnosis|prescription|symptoms|treatment plan', text, re.IGNORECASE):
        return "Medical"
    # Legal domain
    elif re.search(r'court|legal|law|attorney|clause|contract|agreement', text, re.IGNORECASE):
        return "Legal"
    # Financial domain
    elif re.search(r'financial|invoice|payment|transaction|tax|budget', text, re.IGNORECASE):
        return "Financial"
    # Technical domain
    elif re.search(r'technical|specification|software|hardware|system|configuration', text, re.IGNORECASE):
        return "Technical"
    # Academic domain
    elif re.search(r'research|study|analysis|conclusion|findings|methodology', text, re.IGNORECASE):
        return "Academic"
    return "General"