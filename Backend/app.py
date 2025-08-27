from flask import Flask
from flask_cors import CORS
from datetime import datetime
import os
from dotenv import load_dotenv

# Import route blueprints
from routes.auth_routes import auth_bp
from routes.search_routes import search_bp
from routes.playlist_routes import playlist_bp
from routes.track_routes import track_bp
from routes.test_routes import test_bp

# Load environment variables
load_dotenv()

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configure CORS
    CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}})
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(search_bp)
    app.register_blueprint(playlist_bp, url_prefix='/playlist')
    app.register_blueprint(track_bp, url_prefix='/track')
    app.register_blueprint(test_bp)
    
    # Basic routes
    @app.route('/', methods=['GET'])
    def home():
        from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
        return {
            "status": "Flask backend is running",
            "timestamp": datetime.now().isoformat(),
            "spotify_configured": bool(SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET)
        }
    
    @app.route('/health', methods=['GET'])
    def health_check():
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}
    
    @app.route("/ping", methods=["GET"])
    def ping():
        return {"message": "pong", "timestamp": datetime.now().isoformat()}
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Endpoint not found"}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Internal server error"}, 500
    
    return app

if __name__ == '__main__':
    from config import test_spotify_connection, SPOTIFY_CLIENT_ID
    
    print("🚀 Starting Flask server...")
    print(f"📡 Frontend should connect to: http://localhost:5000")
    print(f"🎵 Spotify Client ID: {SPOTIFY_CLIENT_ID}")
    print("Testing Spotify connection...")
    
    # Test connection before starting
    if test_spotify_connection():
        app = create_app()
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("❌ Cannot start server: Spotify API connection failed!")
        print("Please check your .env file and Spotify credentials.")