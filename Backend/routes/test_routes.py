from flask import Blueprint, jsonify
import traceback
from config import sp_public, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

test_bp = Blueprint('test', __name__)

@test_bp.route('/test-spotify', methods=['GET'])
def test_spotify():
    """Test Spotify API connection"""
    try:
        # Test a simple search
        result = sp_public.search(q='Ed Sheeran', type='track', limit=1)
        return jsonify({
            "status": "success",
            "message": "Spotify API is working!",
            "test_result": result
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Spotify API failed: {str(e)}",
            "credentials": {
                "client_id": SPOTIFY_CLIENT_ID,
                "client_secret_set": bool(SPOTIFY_CLIENT_SECRET)
            }
        }), 500

@test_bp.route('/test-genres', methods=['GET'])
def test_genres():
    """Test getting available genres"""
    try:
        genres = sp_public.recommendation_genre_seeds()
        return jsonify({"status": "success", "genres": genres})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@test_bp.route('/test-recommendations', methods=['GET'])
def test_recommendations():
    """Test the recommendations endpoint with debug info"""
    try:
        print("Testing recommendations with minimal parameters...")
        
        # First, get available genres to ensure we use valid ones
        try:
            genres_response = sp_public.recommendation_genre_seeds()
            available_genres = genres_response.get('genres', [])
            print(f"Available genres: {available_genres[:10]}...")  # Print first 10
        except Exception as e:
            print(f"Could not get genres: {e}")
            available_genres = ['pop', 'rock', 'jazz']  # Fallback
        
        # Test with minimal parameters first
        test_params = {
            'seed_genres': available_genres[:1],  # Use only the first available genre
            'limit': 5
        }
        
        print(f"Testing with params: {test_params}")
        recommendations = sp_public.recommendations(**test_params)
        
        return jsonify({
            "status": "success",
            "available_genres_count": len(available_genres),
            "test_params": test_params,
            "recommendations_count": len(recommendations.get('tracks', [])),
            "first_track": recommendations['tracks'][0]['name'] if recommendations.get('tracks') else None
        })
        
    except Exception as e:
        print(f"Recommendations test failed: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500