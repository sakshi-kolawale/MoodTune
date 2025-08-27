from flask import Blueprint, jsonify, request
from services.mood_service import predict_mood

mood_bp = Blueprint("mood", __name__)

@mood_bp.route("/classify", methods=["POST"])
def classify_mood():
    data = request.json
    text = data.get("lyrics", "")
    mood = predict_mood(text)
    return jsonify({"mood": mood})
