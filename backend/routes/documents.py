from flask import Blueprint, request, jsonify
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.document_service import process_document, get_document, get_all_documents, delete_document
from utils.file_utils import allowed_file, save_file

documents_bp = Blueprint('documents', __name__)

@documents_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Save the file
            filepath, filename = save_file(file)
            
            # Process the document
            document = process_document(filepath, filename)
            
            return jsonify({
                "success": True,
                "document": document.to_dict()
            }), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return jsonify({"error": "File type not allowed"}), 400

@documents_bp.route('/documents', methods=['GET'])
def get_documents():
    documents = get_all_documents()
    return jsonify({
        "documents": [doc.to_dict() for doc in documents]
    }), 200

@documents_bp.route('/documents/<int:doc_id>', methods=['GET'])
def get_single_document(doc_id):
    document = get_document(doc_id)
    if not document:
        return jsonify({"error": "Document not found"}), 404
    
    return jsonify({
        "document": document.to_dict()
    }), 200

@documents_bp.route('/documents/<int:doc_id>', methods=['DELETE'])
def remove_document(doc_id):
    success = delete_document(doc_id)
    if not success:
        return jsonify({"error": "Document not found"}), 404
    
    return jsonify({
        "success": True,
        "message": f"Document {doc_id} deleted successfully"
    }), 200