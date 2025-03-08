

from flask import Flask
from flask_cors import CORS
import os

# Import route blueprints
from routes.documents import documents_bp
from routes.search import search_bp
from routes.analytics import analytics_bp

# Import configuration
from config import DEBUG, UPLOAD_FOLDER

# Create Flask application
app = Flask(__name__)
CORS(app)

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Register blueprints
app.register_blueprint(documents_bp)
app.register_blueprint(search_bp)
app.register_blueprint(analytics_bp)

@app.route('/health', methods=['GET'])
def health_check():
    return {"status": "healthy"}, 200

if __name__ == '__main__':
    app.run(debug=DEBUG)
