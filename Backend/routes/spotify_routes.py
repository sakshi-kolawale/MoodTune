from flask import Blueprint, jsonify, request
from services.spotify_service import get_track_metadata

spotify_bp = Blueprint("spotify", __name__)

@spotify_bp.route("/track/<track_id>", methods=["GET"])
def fetch_track(track_id):
    metadata = get_track_metadata(track_id)
    return jsonify(metadata)
