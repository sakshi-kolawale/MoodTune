from flask import Blueprint, request, jsonify
import traceback
from config import sp_public, get_user_spotify_client
from utils import (
    enhance_track_with_play_urls, get_mood_features, get_mood_search_terms,
    safe_get_genres, validate_and_get_seed_genres
)

playlist_bp = Blueprint('playlist', __name__)

@playlist_bp.route('/smart-generate', methods=['POST'])
def smart_generate_playlist():
    """Generate a smart playlist based on mood and genre with play URLs"""
    try:
        data = request.json
        mood = data.get('mood')
        genre = data.get('genre', '')
        limit = data.get('limit', 20)
        
        print(f"smart-generate called with: mood={mood}, genre={genre}, limit={limit}")
        
        if not mood:
            return jsonify({"error": "Mood parameter required"}), 400
        
        # Get mood features
        mood_features = get_mood_features()
        features = mood_features.get(mood.lower(), {})
        if not features:
            return jsonify({
                "error": f"Unknown mood: {mood}. Valid moods are: {list(mood_features.keys())}"
            }), 400
        
        # Get available genres
        available_genres = safe_get_genres(sp_public)
        seed_genres = validate_and_get_seed_genres(genre, available_genres)
        
        print(f"Using seed genres: {seed_genres}")
        
        # Prepare recommendation parameters
        rec_params = {
            'seed_genres': seed_genres,
            'limit': min(limit, 100),  # Spotify max is 100
            **features
        }
        
        print(f"Calling recommendations with params: {rec_params}")
        
        # Get recommendations from Spotify
        try:
            recommendations = sp_public.recommendations(**rec_params)
            
            if not recommendations.get('tracks'):
                # Try with fewer parameters if no results
                print("No tracks found, trying with minimal parameters...")
                minimal_params = {
                    'seed_genres': seed_genres,
                    'limit': limit
                }
                recommendations = sp_public.recommendations(**minimal_params)
            
            # Enhance each track with play URLs
            for track in recommendations.get('tracks', []):
                enhance_track_with_play_urls(track)
            
            return jsonify({
                "recommendations": recommendations,
                "mood": mood,
                "genre": seed_genres[0],
                "features_used": features,
                "seed_genres_used": seed_genres,
                "total_tracks": len(recommendations.get('tracks', []))
            })
            
        except Exception as e:
            print(f"Spotify recommendations API error: {str(e)}")
            
            # Try alternative approach: search for tracks and filter
            print("Trying alternative approach with search...")
            try:
                search_terms = get_mood_search_terms()
                search_query = search_terms.get(mood.lower(), 'popular music')
                if seed_genres[0] != 'pop':
                    search_query += f' {seed_genres[0]}'
                
                search_results = sp_public.search(q=search_query, type='track', limit=limit)
                
                # Enhance search results with play URLs
                for track in search_results['tracks']['items']:
                    enhance_track_with_play_urls(track)
                
                return jsonify({
                    "recommendations": {
                        "tracks": search_results['tracks']['items']
                    },
                    "mood": mood,
                    "genre": seed_genres[0],
                    "method": "search_fallback",
                    "search_query": search_query,
                    "total_tracks": len(search_results['tracks']['items'])
                })
                
            except Exception as search_error:
                print(f"Search fallback also failed: {str(search_error)}")
                raise e  # Re-raise original error
        
    except Exception as e:
        print(f"Error generating smart playlist: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            "error": f"Failed to generate playlist: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500

@playlist_bp.route('/create', methods=['POST'])
def create_playlist():
    """Create a new playlist with proper settings for persistence"""
    data = request.json
    access_token = data.get('access_token')
    name = data.get('name')
    description = data.get('description', '')
    track_uris = data.get('track_uris', [])
    public = data.get('public', True)
    
    if not access_token or not name:
        return jsonify({"error": "Access token and playlist name required"}), 400
    
    try:
        sp_user = get_user_spotify_client(access_token)
        user = sp_user.current_user()
        user_id = user['id']
        
        # Create playlist with proper settings
        playlist = sp_user.user_playlist_create(
            user_id, 
            name,
            public=public,
            collaborative=False,
            description=description
        )
        
        # Add tracks if provided
        if track_uris:
            # Add tracks in batches (Spotify limit is 100 per request)
            batch_size = 100
            for i in range(0, len(track_uris), batch_size):
                batch = track_uris[i:i + batch_size]
                sp_user.playlist_add_items(playlist['id'], batch)
        
        # Get full playlist details after creation
        created_playlist = sp_user.playlist(playlist['id'])
        
        return jsonify({
            "playlist_id": playlist['id'],
            "playlist_url": playlist['external_urls']['spotify'],
            "playlist_name": playlist['name'],
            "tracks_added": len(track_uris),
            "public": created_playlist['public'],
            "collaborative": created_playlist['collaborative'],
            "message": f"Playlist '{name}' created successfully with {len(track_uris)} tracks!",
            "playlist_details": created_playlist
        })
        
    except Exception as e:
        print(f"Error creating playlist: {str(e)}")
        return jsonify({"error": str(e)}), 500

@playlist_bp.route('/<playlist_id>/tracks', methods=['GET'])
def get_playlist_tracks(playlist_id):
    """Get tracks from a specific playlist"""
    access_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    try:
        if access_token:
            sp_user = get_user_spotify_client(access_token)
            tracks = sp_user.playlist_tracks(playlist_id)
        else:
            # Try with public client for public playlists
            tracks = sp_public.playlist_tracks(playlist_id)
        
        # Add play URLs to each track
        for item in tracks['items']:
            if item['track']:
                enhance_track_with_play_urls(item['track'])
        
        return jsonify(tracks)
        
    except Exception as e:
        print(f"Error fetching playlist tracks: {str(e)}")
        return jsonify({"error": str(e)}), 500

@playlist_bp.route('/user', methods=['GET'])
def get_user_playlists():
    """Get user's playlists (requires authentication)"""
    access_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if not access_token:
        return jsonify({"error": "Access token required"}), 401
    
    try:
        sp_user = get_user_spotify_client(access_token)
        playlists = sp_user.current_user_playlists(limit=50)
        
        return jsonify({
            "playlists": playlists['items'],
            "total": playlists['total']
        })
        
    except Exception as e:
        print(f"Error fetching user playlists: {str(e)}")
        return jsonify({"error": str(e)}), 500