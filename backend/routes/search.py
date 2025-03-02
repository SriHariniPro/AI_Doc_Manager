from flask import Blueprint, request, jsonify
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.document_service import search_documents, find_related_documents

search_bp = Blueprint('search', __name__)

@search_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify({"results": []}), 200
    
    limit = int(request.args.get('limit', 10))
    
    results = search_documents(query, limit=limit)
    
    return jsonify({"results": results}), 200

@search_bp.route('/related/<int:doc_id>', methods=['GET'])
def find_related(doc_id):
    limit = int(request.args.get('limit', 5))
    
    related = find_related_documents(doc_id, limit=limit)
    if related is None:
        return jsonify({"error": "Document not found"}), 404
    
    return jsonify({"related": related}), 200