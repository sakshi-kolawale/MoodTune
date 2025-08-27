from flask import Blueprint, request, jsonify
from config import sp_oauth

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET'])
def login():
    """Get Spotify authorization URL"""
    try:
        auth_url = sp_oauth.get_authorize_url()
        return jsonify({"auth_url": auth_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/callback', methods=['POST'])
def callback():
    """Handle Spotify callback and get access token"""
    code = request.json.get('code')
    if not code:
        return jsonify({"error": "Authorization code required"}), 400
    
    try:
        token_info = sp_oauth.get_access_token(code)
        return jsonify({"access_token": token_info['access_token']})
    except Exception as e:
        return jsonify({"error": str(e)}), 400