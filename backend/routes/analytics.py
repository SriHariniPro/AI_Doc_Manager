from flask import Blueprint, jsonify
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.analytics import get_document_type_stats, get_entity_distribution, get_keyword_frequency, get_document_stats

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics/document-types', methods=['GET'])
def document_types():
    stats = get_document_type_stats()
    return jsonify(stats), 200

@analytics_bp.route('/analytics/entity-distribution', methods=['GET'])
def entity_distribution():
    stats = get_entity_distribution()
    return jsonify(stats), 200

@analytics_bp.route('/analytics/keyword-frequency', methods=['GET'])
def keyword_frequency():
    stats = get_keyword_frequency()
    return jsonify(stats), 200

@analytics_bp.route('/analytics/document-stats', methods=['GET'])
def document_stats():
    stats = get_document_stats()
    return jsonify(stats), 200