from flask import Blueprint, jsonify, request
from services.playlist_service import generate_playlist

playlist_bp = Blueprint("playlist", __name__)

@playlist_bp.route("/generate", methods=["POST"])
def create_playlist():
    data = request.json
    mood = data.get("mood", "happy")
    playlist = generate_playlist(mood)
    return jsonify({"playlist": playlist})
