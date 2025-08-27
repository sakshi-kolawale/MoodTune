from flask import Blueprint, request, jsonify
from config import sp_public
from utils import enhance_track_with_play_urls

track_bp = Blueprint('track', __name__)

@track_bp.route('/similar', methods=['POST'])
def get_similar_tracks():
    """Get tracks similar to a given track"""
    data = request.json
    track_id = data.get('track_id')
    limit = data.get('limit', 10)
    
    if not track_id:
        return jsonify({"error": "Track ID required"}), 400
    
    try:
        audio_features = sp_public.audio_features([track_id])[0]
        if not audio_features:
            return jsonify({"error": "Could not get audio features for track"}), 400
        
        track_info = sp_public.track(track_id)
        artist_id = track_info['artists'][0]['id'] if track_info['artists'] else None
        
        recommendations = sp_public.recommendations(
            seed_tracks=[track_id],
            seed_artists=[artist_id] if artist_id else [],
            limit=limit,
            target_danceability=audio_features['danceability'],
            target_energy=audio_features['energy'],
            target_valence=audio_features['valence'],
            target_acousticness=audio_features['acousticness'],
            target_instrumentalness=audio_features['instrumentalness']
        )
        
        # Add play URLs to similar tracks
        for track in recommendations['tracks']:
            enhance_track_with_play_urls(track)
        
        return jsonify({
            "tracks": recommendations['tracks'],
            "seed_track": track_info,
            "audio_features": audio_features
        })
        
    except Exception as e:
        print(f"Error getting similar tracks: {str(e)}")
        return jsonify({"error": str(e)}), 500

@track_bp.route('/play-url', methods=['GET'])
def get_track_play_url():
    """Get play URLs for a specific track"""
    track_id = request.args.get('track_id')
    
    if not track_id:
        return jsonify({"error": "Track ID required"}), 400
    
    try:
        track = sp_public.track(track_id)
        
        play_urls = {
            'spotify_web': track['external_urls']['spotify'],
            'spotify_app': f"spotify:track:{track['id']}",
            'preview_url': track.get('preview_url'),
            'track_name': track['name'],
            'artist_name': ', '.join([artist['name'] for artist in track['artists']])
        }
        
        return jsonify(play_urls)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500