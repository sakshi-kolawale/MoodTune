from flask import Blueprint, request, jsonify
from config import sp_public
from utils import enhance_track_with_play_urls, get_fallback_genres

search_bp = Blueprint('search', __name__)

@search_bp.route('/search', methods=['GET'])
def search_tracks():
    """Search for tracks, artists, or albums with enhanced response including play URLs"""
    query = request.args.get('q')
    search_type = request.args.get('type', 'track')
    limit = int(request.args.get('limit', 20))
    
    if not query:
        return jsonify({"error": "Query parameter required"}), 400
    
    try:
        results = sp_public.search(q=query, type=search_type, limit=limit)
        
        # Enhanced response: Add play URLs and additional info for tracks
        if search_type == 'track' and 'tracks' in results:
            for track in results['tracks']['items']:
                enhance_track_with_play_urls(track)
        
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@search_bp.route('/genres', methods=['GET'])
def get_available_genres():
    """Get available genres from Spotify or fallback to hardcoded list"""
    try:
        genres = sp_public.recommendation_genre_seeds()
        return jsonify({"genres": genres['genres']})
    except Exception as e:
        print(f"Error getting genres: {str(e)}")
        # Fallback: hardcoded genres
        fallback_genres = get_fallback_genres()
        return jsonify({"genres": fallback_genres}), 200