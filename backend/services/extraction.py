import spacy
import nltk
from nltk.tokenize import word_tokenize
import re
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import NLP_MODEL

# Initialize NLP components
nlp = spacy.load(NLP_MODEL)
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab')

def extract_metadata(text, doc_type):
    """
    Extract key metadata from document text based on document type
    """
    metadata = {
        "entities": [],
        "dates": [],
        "key_terms": [],
        "domain_specific": {}
    }
    
    # Extract entities using spaCy
    doc = nlp(text[:10000])  # Limit text for processing speed
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG", "GPE", "MONEY", "DATE", "CARDINAL"]:
            metadata["entities"].append({"text": ent.text, "type": ent.label_})
    
    # Extract dates with regex
    date_pattern = r'\b\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}\b'
    metadata["dates"] = re.findall(date_pattern, text)
    
    # Extract key terms based on frequency
    tokens = word_tokenize(text.lower())
    tokens = [t for t in tokens if len(t) > 3 and not t.isdigit()]
    freq_dist = nltk.FreqDist(tokens)
    metadata["key_terms"] = [term for term, freq in freq_dist.most_common(10)]
    
    # Domain-specific extraction
    if doc_type == "Invoice":
        metadata["domain_specific"] = extract_invoice_data(text)
    elif doc_type == "Contract":
        metadata["domain_specific"] = extract_contract_data(text)
    elif doc_type == "Medical":
        metadata["domain_specific"] = extract_medical_data(text)
    elif doc_type == "Legal":
        metadata["domain_specific"] = extract_legal_data(text)
    
    return metadata

def generate_summary(text):
    """Generate a short summary of the document"""
    doc = nlp(text[:5000])  # Limit text for processing speed
    sentences = [sent.text.strip() for sent in doc.sents]
    if not sentences:
        return "No text content available for summarization."
    
    # Return first 2-3 sentences as summary
    return " ".join(sentences[:min(3, len(sentences))])

def extract_invoice_data(text):
    """Extract specific data from invoices"""
    result = {}
    
    # Look for invoice number
    invoice_pattern = r'(?:invoice|bill|receipt)(?:\s+(?:no|num|number|#))?\s*[:#]?\s*([A-Z0-9\-]+)'
    invoice_match = re.search(invoice_pattern, text, re.IGNORECASE)
    if invoice_match:
        result["invoice_number"] = invoice_match.group(1)
    
    # Look for amounts
    amount_pattern = r'(?:total|amount|sum)(?:\s+(?:due|:))?\s*(?:\$|EUR|£)?\s*([0-9,]+\.[0-9]{2})'
    amount_match = re.search(amount_pattern, text, re.IGNORECASE)
    if amount_match:
        result["amount"] = amount_match.group(1)
    
    return result

def extract_contract_data(text):
    """Extract specific data from contracts"""
    result = {}
    
    # Look for effective date
    date_pattern = r'(?:effective|commencement|start)\s+date\s*:?\s*([A-Za-z]+\s+\d{1,2},?\s+\d{4})'
    date_match = re.search(date_pattern, text, re.IGNORECASE)
    if date_match:
        result["effective_date"] = date_match.group(1)
    
    # Look for parties
    parties_pattern = r'between\s+([A-Za-z\s,]+)(?:\s+and\s+|\s*,\s*)([A-Za-z\s,]+)'
    parties_match = re.search(parties_pattern, text, re.IGNORECASE)
    if parties_match:
        result["party1"] = parties_match.group(1).strip()
        result["party2"] = parties_match.group(2).strip()
    
    return result

def extract_medical_data(text):
    """Extract specific data from medical documents"""
    result = {}
    
    # Look for diagnosis
    diagnosis_pattern = r'diagnosis\s*:?\s*([A-Za-z\s,]+)'
    diagnosis_match = re.search(diagnosis_pattern, text, re.IGNORECASE)
    if diagnosis_match:
        result["diagnosis"] = diagnosis_match.group(1).strip()
    
    # Look for medication
    medication_pattern = r'(?:prescribed|medication|medicine)\s*:?\s*([A-Za-z0-9\s,]+)'
    medication_match = re.search(medication_pattern, text, re.IGNORECASE)
    if medication_match:
        result["medication"] = medication_match.group(1).strip()
    
    return result

def extract_legal_data(text):
    """Extract specific data from legal documents"""
    result = {}
    
    # Look for case number
    case_pattern = r'(?:case|docket|file)\s+(?:no|num|number|#)\s*[:#]?\s*([A-Z0-9\-]+)'
    case_match = re.search(case_pattern, text, re.IGNORECASE)
    if case_match:
        result["case_number"] = case_match.group(1)
    
    # Look for court information
    court_pattern = r'(?:in the|before the)\s+([A-Za-z\s]+Court)'
    court_match = re.search(court_pattern, text, re.IGNORECASE)
    if court_match:
        result["court"] = court_match.group(1).strip()
    
    return result