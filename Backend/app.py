from flask import Flask, request, jsonify
from flask_cors import CORS
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import os
from dotenv import load_dotenv
from datetime import datetime
import traceback
import requests

# Load environment variables from .env file
load_dotenv()

# Get Spotify API credentials
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:5173/callback")

print("=" * 50)
print("SPOTIFY CREDENTIALS CHECK:")
print("=" * 50)
print("SPOTIFY_CLIENT_ID:", SPOTIFY_CLIENT_ID)
print("SPOTIFY_CLIENT_SECRET:", "SET" if SPOTIFY_CLIENT_SECRET else "MISSING!")
print("SPOTIFY_REDIRECT_URI:", SPOTIFY_REDIRECT_URI)
print("=" * 50)

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}})

# Check credentials
if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
    raise ValueError("❌ Spotify credentials are missing! Please check your .env file.")

# Test Spotify connection immediately
def test_spotify_connection():
    """Test if we can connect to Spotify API"""
    try:
        # Create a temporary client to test connection
        test_sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=SPOTIFY_CLIENT_ID,
                client_secret=SPOTIFY_CLIENT_SECRET
            )
        )
        # Simple API call to test connection
        test_sp.search(q='test', type='track', limit=1)
        print("✅ Spotify API connection successful!")
        return True
    except Exception as e:
        print(f"❌ Spotify API connection failed: {str(e)}")
        return False

# Test connection on startup
test_spotify_connection()

# Spotipy clients
sp_public = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    )
)
sp_oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="user-library-read user-top-read playlist-modify-public playlist-modify-private user-read-private"
)

@app.route('/test-spotify', methods=['GET'])
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

@app.route('/test-genres', methods=['GET'])
def test_genres():
    try:
        genres = sp_public.recommendation_genre_seeds()
        return jsonify({"status": "success", "genres": genres})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "Flask backend is running",
        "timestamp": datetime.now().isoformat(),
        "spotify_configured": bool(SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET)
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"message": "pong", "timestamp": datetime.now().isoformat()})

@app.route('/genres', methods=['GET'])
def get_available_genres():
    """Get available genres from Spotify or fallback to hardcoded list"""
    try:
        genres = sp_public.recommendation_genre_seeds()
        return jsonify({"genres": genres['genres']})
    except Exception as e:
        print(f"Error getting genres: {str(e)}")
        # Fallback: hardcoded genres
        fallback_genres = [
            "acoustic", "afrobeat", "alt-rock", "alternative", "ambient", "anime", "black-metal",
            "bluegrass", "blues", "bossanova", "brazil", "breakbeat", "british", "cantopop",
            "chicago-house", "children", "chill", "classical", "club", "comedy", "country",
            "dance", "dancehall", "death-metal", "deep-house", "detroit-techno", "disco", "disney",
            "drum-and-bass", "dub", "dubstep", "edm", "electro", "electronic", "emo", "folk",
            "forro", "french", "funk", "garage", "german", "gospel", "goth", "grindcore", "groove",
            "grunge", "guitar", "happy", "hard-rock", "hardcore", "hardstyle", "heavy-metal",
            "hip-hop", "holidays", "honky-tonk", "house", "idm", "indian", "indie", "indie-pop",
            "industrial", "iranian", "j-dance", "j-idol", "j-pop", "j-rock", "jazz", "k-pop",
            "kids", "latin", "latino", "malay", "mandopop", "metal", "metal-misc", "metalcore",
            "minimal-techno", "movies", "mpb", "new-age", "new-release", "opera", "pagode",
            "party", "philippines-opm", "piano", "pop", "pop-film", "post-dubstep", "power-pop",
            "progressive-house", "psych-rock", "punk", "punk-rock", "r-n-b", "rainy-day", "reggae",
            "reggaeton", "road-trip", "rock", "rock-n-roll", "rockabilly", "romance", "sad",
            "salsa", "samba", "sertanejo", "show-tunes", "singer-songwriter", "ska", "sleep",
            "songwriter", "soul", "soundtracks", "spanish", "study", "summer", "swedish", "synth-pop",
            "tango", "techno", "trance", "trip-hop", "turkish", "work-out", "world-music"
        ]
        return jsonify({"genres": fallback_genres}), 200

@app.route('/auth/login', methods=['GET'])
def login():
    """Get Spotify authorization URL"""
    try:
        auth_url = sp_oauth.get_authorize_url()
        return jsonify({"auth_url": auth_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/auth/callback', methods=['POST'])
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

@app.route('/search', methods=['GET'])
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
                # Add Spotify play URLs
                track['play_urls'] = {
                    'spotify_web': track['external_urls']['spotify'],
                    'spotify_app': f"spotify:track:{track['id']}",
                    'preview_url': track.get('preview_url')  # 30-second preview
                }
                # Add formatted duration
                if track.get('duration_ms'):
                    duration_seconds = track['duration_ms'] // 1000
                    minutes = duration_seconds // 60
                    seconds = duration_seconds % 60
                    track['formatted_duration'] = f"{minutes}:{seconds:02d}"
        
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/test-recommendations', methods=['GET'])
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

@app.route('/playlist/smart-generate', methods=['POST'])
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
        
        # Mood features mapping - reduced values to be safer
        mood_features = {
            'happy': {'target_valence': 0.8, 'target_energy': 0.7, 'target_danceability': 0.7},
            'sad': {'target_valence': 0.2, 'target_energy': 0.3, 'target_acousticness': 0.7},
            'energetic': {'target_energy': 0.9, 'target_danceability': 0.8},
            'chill': {'target_valence': 0.5, 'target_energy': 0.2, 'target_acousticness': 0.8},
            'party': {'target_danceability': 0.9, 'target_energy': 0.8, 'target_valence': 0.7}
        }
        
        # Get features for the selected mood
        features = mood_features.get(mood.lower(), {})
        if not features:
            return jsonify({"error": f"Unknown mood: {mood}. Valid moods are: {list(mood_features.keys())}"}), 400
        
        # Get available genres first
        try:
            genres_response = sp_public.recommendation_genre_seeds()
            available_genres = genres_response.get('genres', [])
            print(f"Available genres from Spotify: {len(available_genres)} genres")
            
            # Determine seed genres
            if genre and genre.lower() in available_genres:
                seed_genres = [genre.lower()]
                print(f"Using requested genre: {genre}")
            else:
                # Use safe default genres that should always be available
                safe_defaults = ['pop', 'rock', 'electronic', 'hip-hop', 'indie']
                seed_genres = [g for g in safe_defaults if g in available_genres][:1]
                if not seed_genres:
                    seed_genres = [available_genres[0]]  # Use first available if none of our defaults work
                print(f"Using fallback genre: {seed_genres[0]} (requested '{genre}' not available)")
                
        except Exception as e:
            print(f"Could not get genres from Spotify: {e}")
            # Ultimate fallback
            seed_genres = ['pop']
            print("Using hardcoded fallback: pop")
        
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
            
            # Enhance each track with play URLs and additional info
            for track in recommendations.get('tracks', []):
                track['play_urls'] = {
                    'spotify_web': track['external_urls']['spotify'],
                    'spotify_app': f"spotify:track:{track['id']}",
                    'preview_url': track.get('preview_url')
                }
                # Add formatted duration
                if track.get('duration_ms'):
                    duration_seconds = track['duration_ms'] // 1000
                    minutes = duration_seconds // 60
                    seconds = duration_seconds % 60
                    track['formatted_duration'] = f"{minutes}:{seconds:02d}"
            
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
                # Search for mood-based terms
                search_terms = {
                    'happy': 'happy upbeat positive',
                    'sad': 'sad melancholy emotional',
                    'energetic': 'energetic pump up workout',
                    'chill': 'chill relaxing ambient',
                    'party': 'party dance club'
                }
                
                search_query = search_terms.get(mood.lower(), 'popular music')
                if seed_genres[0] != 'pop':
                    search_query += f' {seed_genres[0]}'
                
                search_results = sp_public.search(q=search_query, type='track', limit=limit)
                
                # Enhance search results with play URLs
                for track in search_results['tracks']['items']:
                    track['play_urls'] = {
                        'spotify_web': track['external_urls']['spotify'],
                        'spotify_app': f"spotify:track:{track['id']}",
                        'preview_url': track.get('preview_url')
                    }
                    if track.get('duration_ms'):
                        duration_seconds = track['duration_ms'] // 1000
                        minutes = duration_seconds // 60
                        seconds = duration_seconds % 60
                        track['formatted_duration'] = f"{minutes}:{seconds:02d}"
                
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

@app.route('/track/similar', methods=['POST'])
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
            track['play_urls'] = {
                'spotify_web': track['external_urls']['spotify'],
                'spotify_app': f"spotify:track:{track['id']}",
                'preview_url': track.get('preview_url')
            }
        
        return jsonify({
            "tracks": recommendations['tracks'],
            "seed_track": track_info,
            "audio_features": audio_features
        })
    except Exception as e:
        print(f"Error getting similar tracks: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/playlist/create', methods=['POST'])
def create_playlist():
    """Create a new playlist with proper settings for persistence"""
    data = request.json
    access_token = data.get('access_token')
    name = data.get('name')
    description = data.get('description', '')
    track_uris = data.get('track_uris', [])
    public = data.get('public', True)  # Allow setting public/private
    
    if not access_token or not name:
        return jsonify({"error": "Access token and playlist name required"}), 400
    
    try:
        sp_user = spotipy.Spotify(auth=access_token)
        user = sp_user.current_user()
        user_id = user['id']
        
        # Create playlist with proper settings
        playlist = sp_user.user_playlist_create(
            user_id, 
            name,
            public=public,
            collaborative=False,  # Explicitly set to false
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

@app.route('/user/playlists', methods=['GET'])
def get_user_playlists():
    """Get user's playlists (requires authentication)"""
    access_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if not access_token:
        return jsonify({"error": "Access token required"}), 401
    
    try:
        sp_user = spotipy.Spotify(auth=access_token)
        playlists = sp_user.current_user_playlists(limit=50)
        
        return jsonify({
            "playlists": playlists['items'],
            "total": playlists['total']
        })
        
    except Exception as e:
        print(f"Error fetching user playlists: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/playlist/<playlist_id>/tracks', methods=['GET'])
def get_playlist_tracks(playlist_id):
    """Get tracks from a specific playlist"""
    access_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    try:
        if access_token:
            sp_user = spotipy.Spotify(auth=access_token)
            tracks = sp_user.playlist_tracks(playlist_id)
        else:
            # Try with public client for public playlists
            tracks = sp_public.playlist_tracks(playlist_id)
        
        # Add play URLs to each track
        for item in tracks['items']:
            if item['track']:
                track = item['track']
                track['play_urls'] = {
                    'spotify_web': track['external_urls']['spotify'],
                    'spotify_app': f"spotify:track:{track['id']}",
                    'preview_url': track.get('preview_url')
                }
        
        return jsonify(tracks)
        
    except Exception as e:
        print(f"Error fetching playlist tracks: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/track/play-url', methods=['GET'])
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

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    print("🚀 Starting Flask server...")
    print(f"📡 Frontend should connect to: http://localhost:5000")
    print(f"🎵 Spotify Client ID: {SPOTIFY_CLIENT_ID}")
    print("Testing Spotify connection...")
    
    # Test connection before starting
    if test_spotify_connection():
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("❌ Cannot start server: Spotify API connection failed!")
        print("Please check your .env file and Spotify credentials.")


# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import spotipy
# from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
# import os
# from dotenv import load_dotenv
# from datetime import datetime
# import traceback
# import requests

# # Load environment variables from .env file
# load_dotenv()

# # Get Spotify API credentials
# SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
# SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
# SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:5173/callback")

# print("=" * 50)
# print("SPOTIFY CREDENTIALS CHECK:")
# print("=" * 50)
# print("SPOTIFY_CLIENT_ID:", SPOTIFY_CLIENT_ID)
# print("SPOTIFY_CLIENT_SECRET:", "SET" if SPOTIFY_CLIENT_SECRET else "MISSING!")
# print("SPOTIFY_REDIRECT_URI:", SPOTIFY_REDIRECT_URI)
# print("=" * 50)

# # Initialize Flask app
# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}})

# # Check credentials
# if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
#     raise ValueError("❌ Spotify credentials are missing! Please check your .env file.")

# # Test Spotify connection immediately
# def test_spotify_connection():
#     """Test if we can connect to Spotify API"""
#     try:
#         # Create a temporary client to test connection
#         test_sp = spotipy.Spotify(
#             auth_manager=SpotifyClientCredentials(
#                 client_id=SPOTIFY_CLIENT_ID,
#                 client_secret=SPOTIFY_CLIENT_SECRET
#             )
#         )
#         # Simple API call to test connection
#         test_sp.search(q='test', type='track', limit=1)
#         print("✅ Spotify API connection successful!")
#         return True
#     except Exception as e:
#         print(f"❌ Spotify API connection failed: {str(e)}")
#         return False

# # Test connection on startup
# test_spotify_connection()

# # Spotipy clients
# sp_public = spotipy.Spotify(
#     auth_manager=SpotifyClientCredentials(
#         client_id=SPOTIFY_CLIENT_ID,
#         client_secret=SPOTIFY_CLIENT_SECRET
#     )
# )
# sp_oauth = SpotifyOAuth(
#     client_id=SPOTIFY_CLIENT_ID,
#     client_secret=SPOTIFY_CLIENT_SECRET,
#     redirect_uri=SPOTIFY_REDIRECT_URI,
#     scope="user-library-read user-top-read playlist-modify-public playlist-modify-private user-read-private"
# )

# @app.route('/test-spotify', methods=['GET'])
# def test_spotify():
#     """Test Spotify API connection"""
#     try:
#         # Test a simple search
#         result = sp_public.search(q='Ed Sheeran', type='track', limit=1)
#         return jsonify({
#             "status": "success",
#             "message": "Spotify API is working!",
#             "test_result": result
#         })
#     except Exception as e:
#         return jsonify({
#             "status": "error",
#             "message": f"Spotify API failed: {str(e)}",
#             "credentials": {
#                 "client_id": SPOTIFY_CLIENT_ID,
#                 "client_secret_set": bool(SPOTIFY_CLIENT_SECRET)
#             }
#         }), 500

# @app.route('/test-genres', methods=['GET'])
# def test_genres():
#     try:
#         genres = sp_public.recommendation_genre_seeds()
#         return jsonify({"status": "success", "genres": genres})
#     except Exception as e:
#         return jsonify({"status": "error", "error": str(e)}), 500

# @app.route('/', methods=['GET'])
# def home():
#     return jsonify({
#         "status": "Flask backend is running",
#         "timestamp": datetime.now().isoformat(),
#         "spotify_configured": bool(SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET)
#     })

# @app.route('/health', methods=['GET'])
# def health_check():
#     return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

# @app.route("/ping", methods=["GET"])
# def ping():
#     return jsonify({"message": "pong", "timestamp": datetime.now().isoformat()})

# @app.route('/genres', methods=['GET'])
# def get_available_genres():
#     """Get available genres from Spotify or fallback to hardcoded list"""
#     try:
#         genres = sp_public.recommendation_genre_seeds()
#         return jsonify({"genres": genres['genres']})
#     except Exception as e:
#         print(f"Error getting genres: {str(e)}")
#         # Fallback: hardcoded genres
#         fallback_genres = [
#             "acoustic", "afrobeat", "alt-rock", "alternative", "ambient", "anime", "black-metal",
#             "bluegrass", "blues", "bossanova", "brazil", "breakbeat", "british", "cantopop",
#             "chicago-house", "children", "chill", "classical", "club", "comedy", "country",
#             "dance", "dancehall", "death-metal", "deep-house", "detroit-techno", "disco", "disney",
#             "drum-and-bass", "dub", "dubstep", "edm", "electro", "electronic", "emo", "folk",
#             "forro", "french", "funk", "garage", "german", "gospel", "goth", "grindcore", "groove",
#             "grunge", "guitar", "happy", "hard-rock", "hardcore", "hardstyle", "heavy-metal",
#             "hip-hop", "holidays", "honky-tonk", "house", "idm", "indian", "indie", "indie-pop",
#             "industrial", "iranian", "j-dance", "j-idol", "j-pop", "j-rock", "jazz", "k-pop",
#             "kids", "latin", "latino", "malay", "mandopop", "metal", "metal-misc", "metalcore",
#             "minimal-techno", "movies", "mpb", "new-age", "new-release", "opera", "pagode",
#             "party", "philippines-opm", "piano", "pop", "pop-film", "post-dubstep", "power-pop",
#             "progressive-house", "psych-rock", "punk", "punk-rock", "r-n-b", "rainy-day", "reggae",
#             "reggaeton", "road-trip", "rock", "rock-n-roll", "rockabilly", "romance", "sad",
#             "salsa", "samba", "sertanejo", "show-tunes", "singer-songwriter", "ska", "sleep",
#             "songwriter", "soul", "soundtracks", "spanish", "study", "summer", "swedish", "synth-pop",
#             "tango", "techno", "trance", "trip-hop", "turkish", "work-out", "world-music"
#         ]
#         return jsonify({"genres": fallback_genres}), 200

# @app.route('/auth/login', methods=['GET'])
# def login():
#     """Get Spotify authorization URL"""
#     try:
#         auth_url = sp_oauth.get_authorize_url()
#         return jsonify({"auth_url": auth_url})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route('/auth/callback', methods=['POST'])
# def callback():
#     """Handle Spotify callback and get access token"""
#     code = request.json.get('code')
#     if not code:
#         return jsonify({"error": "Authorization code required"}), 400
#     try:
#         token_info = sp_oauth.get_access_token(code)
#         return jsonify({"access_token": token_info['access_token']})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400

# @app.route('/search', methods=['GET'])
# def search_tracks():
#     """Search for tracks, artists, or albums with enhanced response including play URLs"""
#     query = request.args.get('q')
#     search_type = request.args.get('type', 'track')
#     limit = int(request.args.get('limit', 20))
#     if not query:
#         return jsonify({"error": "Query parameter required"}), 400
#     try:
#         results = sp_public.search(q=query, type=search_type, limit=limit)
        
#         # Enhanced response: Add play URLs and additional info for tracks
#         if search_type == 'track' and 'tracks' in results:
#             for track in results['tracks']['items']:
#                 # Add Spotify play URLs
#                 track['play_urls'] = {
#                     'spotify_web': track['external_urls']['spotify'],
#                     'spotify_app': f"spotify:track:{track['id']}",
#                     'preview_url': track.get('preview_url')  # 30-second preview
#                 }
#                 # Add formatted duration
#                 if track.get('duration_ms'):
#                     duration_seconds = track['duration_ms'] // 1000
#                     minutes = duration_seconds // 60
#                     seconds = duration_seconds % 60
#                     track['formatted_duration'] = f"{minutes}:{seconds:02d}"
        
#         return jsonify(results)
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route('/test-recommendations', methods=['GET'])
# def test_recommendations():
#     """Test the recommendations endpoint with debug info"""
#     try:
#         print("Testing recommendations with minimal parameters...")
        
#         # First, get available genres to ensure we use valid ones
#         try:
#             genres_response = sp_public.recommendation_genre_seeds()
#             available_genres = genres_response.get('genres', [])
#             print(f"Available genres: {available_genres[:10]}...")  # Print first 10
#         except Exception as e:
#             print(f"Could not get genres: {e}")
#             available_genres = ['pop', 'rock', 'jazz']  # Fallback
        
#         # Test with minimal parameters first
#         test_params = {
#             'seed_genres': available_genres[:1],  # Use only the first available genre
#             'limit': 5
#         }
        
#         print(f"Testing with params: {test_params}")
#         recommendations = sp_public.recommendations(**test_params)
        
#         return jsonify({
#             "status": "success",
#             "available_genres_count": len(available_genres),
#             "test_params": test_params,
#             "recommendations_count": len(recommendations.get('tracks', [])),
#             "first_track": recommendations['tracks'][0]['name'] if recommendations.get('tracks') else None
#         })
        
#     except Exception as e:
#         print(f"Recommendations test failed: {str(e)}")
#         print(traceback.format_exc())
#         return jsonify({
#             "status": "error",
#             "error": str(e),
#             "traceback": traceback.format_exc()
#         }), 500

# @app.route('/playlist/smart-generate', methods=['POST'])
# def smart_generate_playlist():
#     """Generate a smart playlist based on mood and genre with play URLs"""
#     try:
#         data = request.json
#         mood = data.get('mood')
#         genre = data.get('genre', '')
#         limit = data.get('limit', 20)
        
#         print(f"smart-generate called with: mood={mood}, genre={genre}, limit={limit}")
        
#         if not mood:
#             return jsonify({"error": "Mood parameter required"}), 400
        
#         # Mood features mapping - reduced values to be safer
#         mood_features = {
#             'happy': {'target_valence': 0.8, 'target_energy': 0.7, 'target_danceability': 0.7},
#             'sad': {'target_valence': 0.2, 'target_energy': 0.3, 'target_acousticness': 0.7},
#             'energetic': {'target_energy': 0.9, 'target_danceability': 0.8},
#             'chill': {'target_valence': 0.5, 'target_energy': 0.2, 'target_acousticness': 0.8},
#             'party': {'target_danceability': 0.9, 'target_energy': 0.8, 'target_valence': 0.7}
#         }
        
#         # Get features for the selected mood
#         features = mood_features.get(mood.lower(), {})
#         if not features:
#             return jsonify({"error": f"Unknown mood: {mood}. Valid moods are: {list(mood_features.keys())}"}), 400
        
#         # Get available genres first
#         try:
#             genres_response = sp_public.recommendation_genre_seeds()
#             available_genres = genres_response.get('genres', [])
#             print(f"Available genres from Spotify: {len(available_genres)} genres")
            
#             # Determine seed genres
#             if genre and genre.lower() in available_genres:
#                 seed_genres = [genre.lower()]
#                 print(f"Using requested genre: {genre}")
#             else:
#                 # Use safe default genres that should always be available
#                 safe_defaults = ['pop', 'rock', 'electronic', 'hip-hop', 'indie']
#                 seed_genres = [g for g in safe_defaults if g in available_genres][:1]
#                 if not seed_genres:
#                     seed_genres = [available_genres[0]]  # Use first available if none of our defaults work
#                 print(f"Using fallback genre: {seed_genres[0]} (requested '{genre}' not available)")
                
#         except Exception as e:
#             print(f"Could not get genres from Spotify: {e}")
#             # Ultimate fallback
#             seed_genres = ['pop']
#             print("Using hardcoded fallback: pop")
        
#         # Prepare recommendation parameters
#         rec_params = {
#             'seed_genres': seed_genres,
#             'limit': min(limit, 100),  # Spotify max is 100
#             **features
#         }
        
#         print(f"Calling recommendations with params: {rec_params}")
        
#         # Get recommendations from Spotify
#         try:
#             recommendations = sp_public.recommendations(**rec_params)
            
#             if not recommendations.get('tracks'):
#                 # Try with fewer parameters if no results
#                 print("No tracks found, trying with minimal parameters...")
#                 minimal_params = {
#                     'seed_genres': seed_genres,
#                     'limit': limit
#                 }
#                 recommendations = sp_public.recommendations(**minimal_params)
            
#             # Enhance each track with play URLs and additional info
#             for track in recommendations.get('tracks', []):
#                 track['play_urls'] = {
#                     'spotify_web': track['external_urls']['spotify'],
#                     'spotify_app': f"spotify:track:{track['id']}",
#                     'preview_url': track.get('preview_url')
#                 }
#                 # Add formatted duration
#                 if track.get('duration_ms'):
#                     duration_seconds = track['duration_ms'] // 1000
#                     minutes = duration_seconds // 60
#                     seconds = duration_seconds % 60
#                     track['formatted_duration'] = f"{minutes}:{seconds:02d}"
            
#             return jsonify({
#                 "recommendations": recommendations,
#                 "mood": mood,
#                 "genre": seed_genres[0],
#                 "features_used": features,
#                 "seed_genres_used": seed_genres,
#                 "total_tracks": len(recommendations.get('tracks', []))
#             })
            
#         except Exception as e:
#             print(f"Spotify recommendations API error: {str(e)}")
            
#             # Try alternative approach: search for tracks and filter
#             print("Trying alternative approach with search...")
#             try:
#                 # Search for mood-based terms
#                 search_terms = {
#                     'happy': 'happy upbeat positive',
#                     'sad': 'sad melancholy emotional',
#                     'energetic': 'energetic pump up workout',
#                     'chill': 'chill relaxing ambient',
#                     'party': 'party dance club'
#                 }
                
#                 search_query = search_terms.get(mood.lower(), 'popular music')
#                 if seed_genres[0] != 'pop':
#                     search_query += f' {seed_genres[0]}'
                
#                 search_results = sp_public.search(q=search_query, type='track', limit=limit)
                
#                 # Enhance search results with play URLs
#                 for track in search_results['tracks']['items']:
#                     track['play_urls'] = {
#                         'spotify_web': track['external_urls']['spotify'],
#                         'spotify_app': f"spotify:track:{track['id']}",
#                         'preview_url': track.get('preview_url')
#                     }
#                     if track.get('duration_ms'):
#                         duration_seconds = track['duration_ms'] // 1000
#                         minutes = duration_seconds // 60
#                         seconds = duration_seconds % 60
#                         track['formatted_duration'] = f"{minutes}:{seconds:02d}"
                
#                 return jsonify({
#                     "recommendations": {
#                         "tracks": search_results['tracks']['items']
#                     },
#                     "mood": mood,
#                     "genre": seed_genres[0],
#                     "method": "search_fallback",
#                     "search_query": search_query,
#                     "total_tracks": len(search_results['tracks']['items'])
#                 })
                
#             except Exception as search_error:
#                 print(f"Search fallback also failed: {str(search_error)}")
#                 raise e  # Re-raise original error
        
#     except Exception as e:
#         print(f"Error generating smart playlist: {str(e)}")
#         print(traceback.format_exc())
#         return jsonify({
#             "error": f"Failed to generate playlist: {str(e)}",
#             "traceback": traceback.format_exc()
#         }), 500

# @app.route('/track/similar', methods=['POST'])
# def get_similar_tracks():
#     """Get tracks similar to a given track"""
#     data = request.json
#     track_id = data.get('track_id')
#     limit = data.get('limit', 10)
#     if not track_id:
#         return jsonify({"error": "Track ID required"}), 400
#     try:
#         audio_features = sp_public.audio_features([track_id])[0]
#         if not audio_features:
#             return jsonify({"error": "Could not get audio features for track"}), 400
#         track_info = sp_public.track(track_id)
#         artist_id = track_info['artists'][0]['id'] if track_info['artists'] else None
#         recommendations = sp_public.recommendations(
#             seed_tracks=[track_id],
#             seed_artists=[artist_id] if artist_id else [],
#             limit=limit,
#             target_danceability=audio_features['danceability'],
#             target_energy=audio_features['energy'],
#             target_valence=audio_features['valence'],
#             target_acousticness=audio_features['acousticness'],
#             target_instrumentalness=audio_features['instrumentalness']
#         )
        
#         # Add play URLs to similar tracks
#         for track in recommendations['tracks']:
#             track['play_urls'] = {
#                 'spotify_web': track['external_urls']['spotify'],
#                 'spotify_app': f"spotify:track:{track['id']}",
#                 'preview_url': track.get('preview_url')
#             }
        
#         return jsonify({
#             "tracks": recommendations['tracks'],
#             "seed_track": track_info,
#             "audio_features": audio_features
#         })
#     except Exception as e:
#         print(f"Error getting similar tracks: {str(e)}")
#         return jsonify({"error": str(e)}), 500

# @app.route('/playlist/create', methods=['POST'])
# def create_playlist():
#     """Create a new playlist with proper settings for persistence"""
#     data = request.json
#     access_token = data.get('access_token')
#     name = data.get('name')
#     description = data.get('description', '')
#     track_uris = data.get('track_uris', [])
#     public = data.get('public', True)  # Allow setting public/private
    
#     if not access_token or not name:
#         return jsonify({"error": "Access token and playlist name required"}), 400
    
#     try:
#         sp_user = spotipy.Spotify(auth=access_token)
#         user = sp_user.current_user()
#         user_id = user['id']
        
#         # Create playlist with proper settings
#         playlist = sp_user.user_playlist_create(
#             user_id, 
#             name,
#             public=public,
#             collaborative=False,  # Explicitly set to false
#             description=description
#         )
        
#         # Add tracks if provided
#         if track_uris:
#             # Add tracks in batches (Spotify limit is 100 per request)
#             batch_size = 100
#             for i in range(0, len(track_uris), batch_size):
#                 batch = track_uris[i:i + batch_size]
#                 sp_user.playlist_add_items(playlist['id'], batch)
        
#         # Get full playlist details after creation
#         created_playlist = sp_user.playlist(playlist['id'])
        
#         return jsonify({
#             "playlist_id": playlist['id'],
#             "playlist_url": playlist['external_urls']['spotify'],
#             "playlist_name": playlist['name'],
#             "tracks_added": len(track_uris),
#             "public": created_playlist['public'],
#             "collaborative": created_playlist['collaborative'],
#             "message": f"Playlist '{name}' created successfully with {len(track_uris)} tracks!",
#             "playlist_details": created_playlist
#         })
        
#     except Exception as e:
#         print(f"Error creating playlist: {str(e)}")
#         return jsonify({"error": str(e)}), 500

# @app.route('/user/playlists', methods=['GET'])
# def get_user_playlists():
#     """Get user's playlists (requires authentication)"""
#     access_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
#     if not access_token:
#         return jsonify({"error": "Access token required"}), 401
    
#     try:
#         sp_user = spotipy.Spotify(auth=access_token)
#         playlists = sp_user.current_user_playlists(limit=50)
        
#         return jsonify({
#             "playlists": playlists['items'],
#             "total": playlists['total']
#         })
        
#     except Exception as e:
#         print(f"Error fetching user playlists: {str(e)}")
#         return jsonify({"error": str(e)}), 500

# @app.route('/playlist/<playlist_id>/tracks', methods=['GET'])
# def get_playlist_tracks(playlist_id):
#     """Get tracks from a specific playlist"""
#     access_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
#     try:
#         if access_token:
#             sp_user = spotipy.Spotify(auth=access_token)
#             tracks = sp_user.playlist_tracks(playlist_id)
#         else:
#             # Try with public client for public playlists
#             tracks = sp_public.playlist_tracks(playlist_id)
        
#         # Add play URLs to each track
#         for item in tracks['items']:
#             if item['track']:
#                 track = item['track']
#                 track['play_urls'] = {
#                     'spotify_web': track['external_urls']['spotify'],
#                     'spotify_app': f"spotify:track:{track['id']}",
#                     'preview_url': track.get('preview_url')
#                 }
        
#         return jsonify(tracks)
        
#     except Exception as e:
#         print(f"Error fetching playlist tracks: {str(e)}")
#         return jsonify({"error": str(e)}), 500

# @app.route('/track/play-url', methods=['GET'])
# def get_track_play_url():
#     """Get play URLs for a specific track"""
#     track_id = request.args.get('track_id')
    
#     if not track_id:
#         return jsonify({"error": "Track ID required"}), 400
    
#     try:
#         track = sp_public.track(track_id)
        
#         play_urls = {
#             'spotify_web': track['external_urls']['spotify'],
#             'spotify_app': f"spotify:track:{track['id']}",
#             'preview_url': track.get('preview_url'),
#             'track_name': track['name'],
#             'artist_name': ', '.join([artist['name'] for artist in track['artists']])
#         }
        
#         return jsonify(play_urls)
        
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.errorhandler(404)
# def not_found(error):
#     return jsonify({"error": "Endpoint not found"}), 404

# @app.errorhandler(500)
# def internal_error(error):
#     return jsonify({"error": "Internal server error"}), 500

# if __name__ == '__main__':
#     print("🚀 Starting Flask server...")
#     print(f"📡 Frontend should connect to: http://localhost:5000")
#     print(f"🎵 Spotify Client ID: {SPOTIFY_CLIENT_ID}")
#     print("Testing Spotify connection...")
    
#     # Test connection before starting
#     if test_spotify_connection():
#         app.run(debug=True, host='0.0.0.0', port=5000)
#     else:
#         print("❌ Cannot start server: Spotify API connection failed!")
#         print("Please check your .env file and Spotify credentials.")


# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import spotipy
# from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
# import os
# from dotenv import load_dotenv
# from datetime import datetime
# import traceback
# import requests

# # Load environment variables from .env file
# load_dotenv()

# # Get Spotify API credentials
# SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
# SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
# SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:5173/callback")

# print("=" * 50)
# print("SPOTIFY CREDENTIALS CHECK:")
# print("=" * 50)
# print("SPOTIFY_CLIENT_ID:", SPOTIFY_CLIENT_ID)
# print("SPOTIFY_CLIENT_SECRET:", "SET" if SPOTIFY_CLIENT_SECRET else "MISSING!")
# print("SPOTIFY_REDIRECT_URI:", SPOTIFY_REDIRECT_URI)
# print("=" * 50)

# # Initialize Flask app
# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}})

# # Check credentials
# if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
#     raise ValueError("❌ Spotify credentials are missing! Please check your .env file.")

# # Test Spotify connection immediately
# def test_spotify_connection():
#     """Test if we can connect to Spotify API"""
#     try:
#         # Create a temporary client to test connection
#         test_sp = spotipy.Spotify(
#             auth_manager=SpotifyClientCredentials(
#                 client_id=SPOTIFY_CLIENT_ID,
#                 client_secret=SPOTIFY_CLIENT_SECRET
#             )
#         )
#         # Simple API call to test connection
#         test_sp.search(q='test', type='track', limit=1)
#         print("✅ Spotify API connection successful!")
#         return True
#     except Exception as e:
#         print(f"❌ Spotify API connection failed: {str(e)}")
#         return False

# # Test connection on startup
# test_spotify_connection()

# # Spotipy clients
# sp_public = spotipy.Spotify(
#     auth_manager=SpotifyClientCredentials(
#         client_id=SPOTIFY_CLIENT_ID,
#         client_secret=SPOTIFY_CLIENT_SECRET
#     )
# )
# sp_oauth = SpotifyOAuth(
#     client_id=SPOTIFY_CLIENT_ID,
#     client_secret=SPOTIFY_CLIENT_SECRET,
#     redirect_uri=SPOTIFY_REDIRECT_URI,
#     scope="user-library-read user-top-read playlist-modify-public playlist-modify-private"
# )

# @app.route('/test-spotify', methods=['GET'])
# def test_spotify():
#     """Test Spotify API connection"""
#     try:
#         # Test a simple search
#         result = sp_public.search(q='Ed Sheeran', type='track', limit=1)
#         return jsonify({
#             "status": "success",
#             "message": "Spotify API is working!",
#             "test_result": result
#         })
#     except Exception as e:
#         return jsonify({
#             "status": "error",
#             "message": f"Spotify API failed: {str(e)}",
#             "credentials": {
#                 "client_id": SPOTIFY_CLIENT_ID,
#                 "client_secret_set": bool(SPOTIFY_CLIENT_SECRET)
#             }
#         }), 500

# @app.route('/test-genres', methods=['GET'])
# def test_genres():
#     try:
#         genres = sp_public.recommendation_genre_seeds()
#         return jsonify({"status": "success", "genres": genres})
#     except Exception as e:
#         return jsonify({"status": "error", "error": str(e)}), 500

# @app.route('/', methods=['GET'])
# def home():
#     return jsonify({
#         "status": "Flask backend is running",
#         "timestamp": datetime.now().isoformat(),
#         "spotify_configured": bool(SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET)
#     })

# @app.route('/health', methods=['GET'])
# def health_check():
#     return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

# @app.route("/ping", methods=["GET"])
# def ping():
#     return jsonify({"message": "pong", "timestamp": datetime.now().isoformat()})

# @app.route('/genres', methods=['GET'])
# def get_available_genres():
#     """Get available genres from Spotify or fallback to hardcoded list"""
#     try:
#         genres = sp_public.recommendation_genre_seeds()
#         return jsonify({"genres": genres['genres']})
#     except Exception as e:
#         print(f"Error getting genres: {str(e)}")
#         # Fallback: hardcoded genres
#         fallback_genres = [
#             "acoustic", "afrobeat", "alt-rock", "alternative", "ambient", "anime", "black-metal",
#             "bluegrass", "blues", "bossanova", "brazil", "breakbeat", "british", "cantopop",
#             "chicago-house", "children", "chill", "classical", "club", "comedy", "country",
#             "dance", "dancehall", "death-metal", "deep-house", "detroit-techno", "disco", "disney",
#             "drum-and-bass", "dub", "dubstep", "edm", "electro", "electronic", "emo", "folk",
#             "forro", "french", "funk", "garage", "german", "gospel", "goth", "grindcore", "groove",
#             "grunge", "guitar", "happy", "hard-rock", "hardcore", "hardstyle", "heavy-metal",
#             "hip-hop", "holidays", "honky-tonk", "house", "idm", "indian", "indie", "indie-pop",
#             "industrial", "iranian", "j-dance", "j-idol", "j-pop", "j-rock", "jazz", "k-pop",
#             "kids", "latin", "latino", "malay", "mandopop", "metal", "metal-misc", "metalcore",
#             "minimal-techno", "movies", "mpb", "new-age", "new-release", "opera", "pagode",
#             "party", "philippines-opm", "piano", "pop", "pop-film", "post-dubstep", "power-pop",
#             "progressive-house", "psych-rock", "punk", "punk-rock", "r-n-b", "rainy-day", "reggae",
#             "reggaeton", "road-trip", "rock", "rock-n-roll", "rockabilly", "romance", "sad",
#             "salsa", "samba", "sertanejo", "show-tunes", "singer-songwriter", "ska", "sleep",
#             "songwriter", "soul", "soundtracks", "spanish", "study", "summer", "swedish", "synth-pop",
#             "tango", "techno", "trance", "trip-hop", "turkish", "work-out", "world-music"
#         ]
#         return jsonify({"genres": fallback_genres}), 200

# @app.route('/auth/login', methods=['GET'])
# def login():
#     """Get Spotify authorization URL"""
#     try:
#         auth_url = sp_oauth.get_authorize_url()
#         return jsonify({"auth_url": auth_url})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route('/auth/callback', methods=['POST'])
# def callback():
#     """Handle Spotify callback and get access token"""
#     code = request.json.get('code')
#     if not code:
#         return jsonify({"error": "Authorization code required"}), 400
#     try:
#         token_info = sp_oauth.get_access_token(code)
#         return jsonify({"access_token": token_info['access_token']})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400

# @app.route('/search', methods=['GET'])
# def search_tracks():
#     """Search for tracks, artists, or albums"""
#     query = request.args.get('q')
#     search_type = request.args.get('type', 'track')
#     limit = int(request.args.get('limit', 20))
#     if not query:
#         return jsonify({"error": "Query parameter required"}), 400
#     try:
#         results = sp_public.search(q=query, type=search_type, limit=limit)
#         return jsonify(results)
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route('/test-recommendations', methods=['GET'])
# def test_recommendations():
#     """Test the recommendations endpoint with debug info"""
#     try:
#         print("Testing recommendations with minimal parameters...")
        
#         # First, get available genres to ensure we use valid ones
#         try:
#             genres_response = sp_public.recommendation_genre_seeds()
#             available_genres = genres_response.get('genres', [])
#             print(f"Available genres: {available_genres[:10]}...")  # Print first 10
#         except Exception as e:
#             print(f"Could not get genres: {e}")
#             available_genres = ['pop', 'rock', 'jazz']  # Fallback
        
#         # Test with minimal parameters first
#         test_params = {
#             'seed_genres': available_genres[:1],  # Use only the first available genre
#             'limit': 5
#         }
        
#         print(f"Testing with params: {test_params}")
#         recommendations = sp_public.recommendations(**test_params)
        
#         return jsonify({
#             "status": "success",
#             "available_genres_count": len(available_genres),
#             "test_params": test_params,
#             "recommendations_count": len(recommendations.get('tracks', [])),
#             "first_track": recommendations['tracks'][0]['name'] if recommendations.get('tracks') else None
#         })
        
#     except Exception as e:
#         print(f"Recommendations test failed: {str(e)}")
#         print(traceback.format_exc())
#         return jsonify({
#             "status": "error",
#             "error": str(e),
#             "traceback": traceback.format_exc()
#         }), 500

# @app.route('/playlist/smart-generate', methods=['POST'])
# def smart_generate_playlist():
#     """Generate a smart playlist based on mood and genre"""
#     try:
#         data = request.json
#         mood = data.get('mood')
#         genre = data.get('genre', '')
#         limit = data.get('limit', 20)
        
#         print(f"smart-generate called with: mood={mood}, genre={genre}, limit={limit}")
        
#         if not mood:
#             return jsonify({"error": "Mood parameter required"}), 400
        
#         # Mood features mapping - reduced values to be safer
#         mood_features = {
#             'happy': {'target_valence': 0.8, 'target_energy': 0.7, 'target_danceability': 0.7},
#             'sad': {'target_valence': 0.2, 'target_energy': 0.3, 'target_acousticness': 0.7},
#             'energetic': {'target_energy': 0.9, 'target_danceability': 0.8},
#             'chill': {'target_valence': 0.5, 'target_energy': 0.2, 'target_acousticness': 0.8},
#             'party': {'target_danceability': 0.9, 'target_energy': 0.8, 'target_valence': 0.7}
#         }
        
#         # Get features for the selected mood
#         features = mood_features.get(mood.lower(), {})
#         if not features:
#             return jsonify({"error": f"Unknown mood: {mood}. Valid moods are: {list(mood_features.keys())}"}), 400
        
#         # Get available genres first
#         try:
#             genres_response = sp_public.recommendation_genre_seeds()
#             available_genres = genres_response.get('genres', [])
#             print(f"Available genres from Spotify: {len(available_genres)} genres")
            
#             # Determine seed genres
#             if genre and genre.lower() in available_genres:
#                 seed_genres = [genre.lower()]
#                 print(f"Using requested genre: {genre}")
#             else:
#                 # Use safe default genres that should always be available
#                 safe_defaults = ['pop', 'rock', 'electronic', 'hip-hop', 'indie']
#                 seed_genres = [g for g in safe_defaults if g in available_genres][:1]
#                 if not seed_genres:
#                     seed_genres = [available_genres[0]]  # Use first available if none of our defaults work
#                 print(f"Using fallback genre: {seed_genres[0]} (requested '{genre}' not available)")
                
#         except Exception as e:
#             print(f"Could not get genres from Spotify: {e}")
#             # Ultimate fallback
#             seed_genres = ['pop']
#             print("Using hardcoded fallback: pop")
        
#         # Prepare recommendation parameters
#         rec_params = {
#             'seed_genres': seed_genres,
#             'limit': min(limit, 100),  # Spotify max is 100
#             **features
#         }
        
#         print(f"Calling recommendations with params: {rec_params}")
        
#         # Get recommendations from Spotify
#         try:
#             recommendations = sp_public.recommendations(**rec_params)
            
#             if not recommendations.get('tracks'):
#                 # Try with fewer parameters if no results
#                 print("No tracks found, trying with minimal parameters...")
#                 minimal_params = {
#                     'seed_genres': seed_genres,
#                     'limit': limit
#                 }
#                 recommendations = sp_public.recommendations(**minimal_params)
            
#             return jsonify({
#                 "recommendations": recommendations,
#                 "mood": mood,
#                 "genre": seed_genres[0],
#                 "features_used": features,
#                 "seed_genres_used": seed_genres,
#                 "total_tracks": len(recommendations.get('tracks', []))
#             })
            
#         except Exception as e:
#             print(f"Spotify recommendations API error: {str(e)}")
            
#             # Try alternative approach: search for tracks and filter
#             print("Trying alternative approach with search...")
#             try:
#                 # Search for mood-based terms
#                 search_terms = {
#                     'happy': 'happy upbeat positive',
#                     'sad': 'sad melancholy emotional',
#                     'energetic': 'energetic pump up workout',
#                     'chill': 'chill relaxing ambient',
#                     'party': 'party dance club'
#                 }
                
#                 search_query = search_terms.get(mood.lower(), 'popular music')
#                 if seed_genres[0] != 'pop':
#                     search_query += f' {seed_genres[0]}'
                
#                 search_results = sp_public.search(q=search_query, type='track', limit=limit)
                
#                 return jsonify({
#                     "recommendations": {
#                         "tracks": search_results['tracks']['items']
#                     },
#                     "mood": mood,
#                     "genre": seed_genres[0],
#                     "method": "search_fallback",
#                     "search_query": search_query,
#                     "total_tracks": len(search_results['tracks']['items'])
#                 })
                
#             except Exception as search_error:
#                 print(f"Search fallback also failed: {str(search_error)}")
#                 raise e  # Re-raise original error
        
#     except Exception as e:
#         print(f"Error generating smart playlist: {str(e)}")
#         print(traceback.format_exc())
#         return jsonify({
#             "error": f"Failed to generate playlist: {str(e)}",
#             "traceback": traceback.format_exc()
#         }), 500

# @app.route('/track/similar', methods=['POST'])
# def get_similar_tracks():
#     """Get tracks similar to a given track"""
#     data = request.json
#     track_id = data.get('track_id')
#     limit = data.get('limit', 10)
#     if not track_id:
#         return jsonify({"error": "Track ID required"}), 400
#     try:
#         audio_features = sp_public.audio_features([track_id])[0]
#         if not audio_features:
#             return jsonify({"error": "Could not get audio features for track"}), 400
#         track_info = sp_public.track(track_id)
#         artist_id = track_info['artists'][0]['id'] if track_info['artists'] else None
#         recommendations = sp_public.recommendations(
#             seed_tracks=[track_id],
#             seed_artists=[artist_id] if artist_id else [],
#             limit=limit,
#             target_danceability=audio_features['danceability'],
#             target_energy=audio_features['energy'],
#             target_valence=audio_features['valence'],
#             target_acousticness=audio_features['acousticness'],
#             target_instrumentalness=audio_features['instrumentalness']
#         )
#         return jsonify({
#             "tracks": recommendations['tracks'],
#             "seed_track": track_info,
#             "audio_features": audio_features
#         })
#     except Exception as e:
#         print(f"Error getting similar tracks: {str(e)}")
#         return jsonify({"error": str(e)}), 500

# @app.route('/playlist/create', methods=['POST'])
# def create_playlist():
#     """Create a new playlist (requires user authentication)"""
#     data = request.json
#     access_token = data.get('access_token')
#     name = data.get('name')
#     description = data.get('description', '')
#     track_uris = data.get('track_uris', [])
#     if not access_token or not name:
#         return jsonify({"error": "Access token and playlist name required"}), 400
#     try:
#         sp_user = spotipy.Spotify(auth=access_token)
#         user = sp_user.current_user()
#         user_id = user['id']
#         playlist = sp_user.user_playlist_create(
#             user_id, 
#             name,
#             public=True,
#             description=description
#         )
#         if track_uris:
#             sp_user.playlist_add_items(playlist['id'], track_uris)
#         return jsonify({
#             "playlist_id": playlist['id'],
#             "playlist_url": playlist['external_urls']['spotify'],
#             "message": f"Playlist '{name}' created successfully!"
#         })
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.errorhandler(404)
# def not_found(error):
#     return jsonify({"error": "Endpoint not found"}), 404

# @app.errorhandler(500)
# def internal_error(error):
#     return jsonify({"error": "Internal server error"}), 500

# if __name__ == '__main__':
#     print("🚀 Starting Flask server...")
#     print(f"📡 Frontend should connect to: http://localhost:5000")
#     print(f"🎵 Spotify Client ID: {SPOTIFY_CLIENT_ID}")
#     print("Testing Spotify connection...")
    
#     # Test connection before starting
#     if test_spotify_connection():
#         app.run(debug=True, host='0.0.0.0', port=5000)
#     else:
#         print("❌ Cannot start server: Spotify API connection failed!")
#         print("Please check your .env file and Spotify credentials.")


# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import spotipy
# from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
# import os
# from dotenv import load_dotenv
# from datetime import datetime
# import traceback
# import requests

# # Load environment variables from .env file
# load_dotenv()

# # Get Spotify API credentials
# SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
# SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
# SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:5173/callback")

# print("=" * 50)
# print("SPOTIFY CREDENTIALS CHECK:")
# print("=" * 50)
# print("SPOTIFY_CLIENT_ID:", SPOTIFY_CLIENT_ID)
# print("SPOTIFY_CLIENT_SECRET:", "SET" if SPOTIFY_CLIENT_SECRET else "MISSING!")
# print("SPOTIFY_REDIRECT_URI:", SPOTIFY_REDIRECT_URI)
# print("=" * 50)

# # Initialize Flask app
# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}})

# # Check credentials
# if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
#     raise ValueError("❌ Spotify credentials are missing! Please check your .env file.")

# # Test Spotify connection immediately
# def test_spotify_connection():
#     """Test if we can connect to Spotify API"""
#     try:
#         # Create a temporary client to test connection
#         test_sp = spotipy.Spotify(
#             auth_manager=SpotifyClientCredentials(
#                 client_id=SPOTIFY_CLIENT_ID,
#                 client_secret=SPOTIFY_CLIENT_SECRET
#             )
#         )
#         # Simple API call to test connection
#         test_sp.search(q='test', type='track', limit=1)
#         print("✅ Spotify API connection successful!")
#         return True
#     except Exception as e:
#         print(f"❌ Spotify API connection failed: {str(e)}")
#         return False

# # Test connection on startup
# test_spotify_connection()

# # Spotipy clients
# sp_public = spotipy.Spotify(
#     auth_manager=SpotifyClientCredentials(
#         client_id=SPOTIFY_CLIENT_ID,
#         client_secret=SPOTIFY_CLIENT_SECRET
#     )
# )
# sp_oauth = SpotifyOAuth(
#     client_id=SPOTIFY_CLIENT_ID,
#     client_secret=SPOTIFY_CLIENT_SECRET,
#     redirect_uri=SPOTIFY_REDIRECT_URI,
#     scope="user-library-read user-top-read playlist-modify-public playlist-modify-private"
# )

# @app.route('/test-spotify', methods=['GET'])
# def test_spotify():
#     """Test Spotify API connection"""
#     try:
#         # Test a simple search
#         result = sp_public.search(q='Ed Sheeran', type='track', limit=1)
#         return jsonify({
#             "status": "success",
#             "message": "Spotify API is working!",
#             "test_result": result
#         })
#     except Exception as e:
#         return jsonify({
#             "status": "error",
#             "message": f"Spotify API failed: {str(e)}",
#             "credentials": {
#                 "client_id": SPOTIFY_CLIENT_ID,
#                 "client_secret_set": bool(SPOTIFY_CLIENT_SECRET)
#             }
#         }), 500

# @app.route('/test-genres', methods=['GET'])
# def test_genres():
#     try:
#         genres = sp_public.recommendation_genre_seeds()
#         return jsonify({"status": "success", "genres": genres})
#     except Exception as e:
#         return jsonify({"status": "error", "error": str(e)}), 500

# @app.route('/', methods=['GET'])
# def home():
#     return jsonify({
#         "status": "Flask backend is running",
#         "timestamp": datetime.now().isoformat(),
#         "spotify_configured": bool(SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET)
#     })

# @app.route('/health', methods=['GET'])
# def health_check():
#     return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

# @app.route("/ping", methods=["GET"])
# def ping():
#     return jsonify({"message": "pong", "timestamp": datetime.now().isoformat()})

# @app.route('/genres', methods=['GET'])
# def get_available_genres():
#     """Get available genres from Spotify or fallback to hardcoded list"""
#     try:
#         genres = sp_public.recommendation_genre_seeds()
#         return jsonify({"genres": genres['genres']})
#     except Exception as e:
#         print(f"Error getting genres: {str(e)}")
#         # Fallback: hardcoded genres
#         fallback_genres = [
#             "acoustic", "afrobeat", "alt-rock", "alternative", "ambient", "anime", "black-metal",
#             "bluegrass", "blues", "bossanova", "brazil", "breakbeat", "british", "cantopop",
#             "chicago-house", "children", "chill", "classical", "club", "comedy", "country",
#             "dance", "dancehall", "death-metal", "deep-house", "detroit-techno", "disco", "disney",
#             "drum-and-bass", "dub", "dubstep", "edm", "electro", "electronic", "emo", "folk",
#             "forro", "french", "funk", "garage", "german", "gospel", "goth", "grindcore", "groove",
#             "grunge", "guitar", "happy", "hard-rock", "hardcore", "hardstyle", "heavy-metal",
#             "hip-hop", "holidays", "honky-tonk", "house", "idm", "indian", "indie", "indie-pop",
#             "industrial", "iranian", "j-dance", "j-idol", "j-pop", "j-rock", "jazz", "k-pop",
#             "kids", "latin", "latino", "malay", "mandopop", "metal", "metal-misc", "metalcore",
#             "minimal-techno", "movies", "mpb", "new-age", "new-release", "opera", "pagode",
#             "party", "philippines-opm", "piano", "pop", "pop-film", "post-dubstep", "power-pop",
#             "progressive-house", "psych-rock", "punk", "punk-rock", "r-n-b", "rainy-day", "reggae",
#             "reggaeton", "road-trip", "rock", "rock-n-roll", "rockabilly", "romance", "sad",
#             "salsa", "samba", "sertanejo", "show-tunes", "singer-songwriter", "ska", "sleep",
#             "songwriter", "soul", "soundtracks", "spanish", "study", "summer", "swedish", "synth-pop",
#             "tango", "techno", "trance", "trip-hop", "turkish", "work-out", "world-music"
#         ]
#         return jsonify({"genres": fallback_genres}), 200

# @app.route('/auth/login', methods=['GET'])
# def login():
#     """Get Spotify authorization URL"""
#     try:
#         auth_url = sp_oauth.get_authorize_url()
#         return jsonify({"auth_url": auth_url})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route('/auth/callback', methods=['POST'])
# def callback():
#     """Handle Spotify callback and get access token"""
#     code = request.json.get('code')
#     if not code:
#         return jsonify({"error": "Authorization code required"}), 400
#     try:
#         token_info = sp_oauth.get_access_token(code)
#         return jsonify({"access_token": token_info['access_token']})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400

# @app.route('/search', methods=['GET'])
# def search_tracks():
#     """Search for tracks, artists, or albums"""
#     query = request.args.get('q')
#     search_type = request.args.get('type', 'track')
#     limit = int(request.args.get('limit', 20))
#     if not query:
#         return jsonify({"error": "Query parameter required"}), 400
#     try:
#         results = sp_public.search(q=query, type=search_type, limit=limit)
#         return jsonify(results)
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route('/playlist/smart-generate', methods=['POST'])
# def smart_generate_playlist():
#     """Generate a smart playlist based on mood and genre"""
#     try:
#         data = request.json
#         mood = data.get('mood')
#         genre = data.get('genre', '')
#         limit = data.get('limit', 20)
        
#         print(f"smart-generate called with: mood={mood}, genre={genre}, limit={limit}")
        
#         if not mood:
#             return jsonify({"error": "Mood parameter required"}), 400
        
#         # Mood features mapping
#         mood_features = {
#             'happy': {'target_valence': 0.8, 'target_energy': 0.7, 'target_danceability': 0.7},
#             'sad': {'target_valence': 0.2, 'target_energy': 0.3, 'target_acousticness': 0.7},
#             'energetic': {'target_energy': 0.9, 'target_danceability': 0.8, 'target_tempo': 140},
#             'chill': {'target_valence': 0.5, 'target_energy': 0.2, 'target_acousticness': 0.8},
#             'party': {'target_danceability': 0.9, 'target_energy': 0.8, 'target_valence': 0.7}
#         }
        
#         # Get features for the selected mood
#         features = mood_features.get(mood.lower(), {})
#         if not features:
#             return jsonify({"error": f"Unknown mood: {mood}. Valid moods are: {list(mood_features.keys())}"}), 400
        
#         # Use a safe default genre if none provided or invalid
#         seed_genres = ['pop']  # Always use pop as default
        
#         print(f"Using seed_genres: {seed_genres}, features: {features}")
        
#         # Get recommendations from Spotify
#         recommendations = sp_public.recommendations(
#             seed_genres=seed_genres[:5],
#             limit=limit,
#             **features
#         )
        
#         return jsonify({
#             "recommendations": recommendations,
#             "mood": mood,
#             "genre": 'pop',  # Always return pop for now
#             "features_used": features,
#             "seed_genres_used": seed_genres
#         })
        
#     except Exception as e:
#         print(f"Error generating smart playlist: {str(e)}")
#         print(traceback.format_exc())
#         return jsonify({"error": f"Failed to generate playlist: {str(e)}"}), 500

# @app.route('/track/similar', methods=['POST'])
# def get_similar_tracks():
#     """Get tracks similar to a given track"""
#     data = request.json
#     track_id = data.get('track_id')
#     limit = data.get('limit', 10)
#     if not track_id:
#         return jsonify({"error": "Track ID required"}), 400
#     try:
#         audio_features = sp_public.audio_features([track_id])[0]
#         if not audio_features:
#             return jsonify({"error": "Could not get audio features for track"}), 400
#         track_info = sp_public.track(track_id)
#         artist_id = track_info['artists'][0]['id'] if track_info['artists'] else None
#         recommendations = sp_public.recommendations(
#             seed_tracks=[track_id],
#             seed_artists=[artist_id] if artist_id else [],
#             limit=limit,
#             target_danceability=audio_features['danceability'],
#             target_energy=audio_features['energy'],
#             target_valence=audio_features['valence'],
#             target_acousticness=audio_features['acousticness'],
#             target_instrumentalness=audio_features['instrumentalness']
#         )
#         return jsonify({
#             "tracks": recommendations['tracks'],
#             "seed_track": track_info,
#             "audio_features": audio_features
#         })
#     except Exception as e:
#         print(f"Error getting similar tracks: {str(e)}")
#         return jsonify({"error": str(e)}), 500

# @app.route('/playlist/create', methods=['POST'])
# def create_playlist():
#     """Create a new playlist (requires user authentication)"""
#     data = request.json
#     access_token = data.get('access_token')
#     name = data.get('name')
#     description = data.get('description', '')
#     track_uris = data.get('track_uris', [])
#     if not access_token or not name:
#         return jsonify({"error": "Access token and playlist name required"}), 400
#     try:
#         sp_user = spotipy.Spotify(auth=access_token)
#         user = sp_user.current_user()
#         user_id = user['id']
#         playlist = sp_user.user_playlist_create(
#             user_id, 
#             name,
#             public=True,
#             description=description
#         )
#         if track_uris:
#             sp_user.playlist_add_items(playlist['id'], track_uris)
#         return jsonify({
#             "playlist_id": playlist['id'],
#             "playlist_url": playlist['external_urls']['spotify'],
#             "message": f"Playlist '{name}' created successfully!"
#         })
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.errorhandler(404)
# def not_found(error):
#     return jsonify({"error": "Endpoint not found"}), 404

# @app.errorhandler(500)
# def internal_error(error):
#     return jsonify({"error": "Internal server error"}), 500

# if __name__ == '__main__':
#     print("🚀 Starting Flask server...")
#     print(f"📡 Frontend should connect to: http://localhost:5000")
#     print(f"🎵 Spotify Client ID: {SPOTIFY_CLIENT_ID}")
#     print("Testing Spotify connection...")
    
#     # Test connection before starting
#     if test_spotify_connection():
#         app.run(debug=True, host='0.0.0.0', port=5000)
#     else:
#         print("❌ Cannot start server: Spotify API connection failed!")
#         print("Please check your .env file and Spotify credentials.")



# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import spotipy
# from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
# import os
# from dotenv import load_dotenv
# from datetime import datetime

# # Load environment variables from .env file
# load_dotenv()


# # Get Spotify API credentials
# SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
# SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
# SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:5173/callback")

# print("SPOTIFY_CLIENT_ID:", SPOTIFY_CLIENT_ID)
# print("SPOTIFY_CLIENT_SECRET:", SPOTIFY_CLIENT_SECRET)
# print("SPOTIFY_REDIRECT_URI:", SPOTIFY_REDIRECT_URI)


# # Initialize Flask app
# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}})

# # Check credentials
# if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
#     raise ValueError("❌ Spotify credentials are missing! Please check your .env file.")

# # Spotipy clients
# sp_public = spotipy.Spotify(
#     auth_manager=SpotifyClientCredentials(
#         client_id=SPOTIFY_CLIENT_ID,
#         client_secret=SPOTIFY_CLIENT_SECRET
#     )
# )
# sp_oauth = SpotifyOAuth(
#     client_id=SPOTIFY_CLIENT_ID,
#     client_secret=SPOTIFY_CLIENT_SECRET,
#     redirect_uri=SPOTIFY_REDIRECT_URI,
#     scope="user-library-read user-top-read playlist-modify-public playlist-modify-private"
# )

# @app.route('/test-genres', methods=['GET'])
# def test_genres():
#     try:
#         genres = sp_public.recommendation_genre_seeds()
#         return jsonify(genres)
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route('/', methods=['GET'])
# def home():
#     return jsonify({"status": "Flask backend is running", "timestamp": datetime.now().isoformat()})

# @app.route('/health', methods=['GET'])
# def health_check():
#     return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

# @app.route("/ping", methods=["GET"])
# def ping():
#     return jsonify({"message": "pong", "timestamp": datetime.now().isoformat()})

# # @app.route('/genres', methods=['GET'])
# # def get_available_genres():
# #     """Get available genres from Spotify"""
# #     try:
# #         genres = sp_public.recommendation_genre_seeds()
# #         return jsonify({"genres": genres['genres']})
# #     except Exception as e:
# #         print(f"Error getting genres: {str(e)}")
# #         return jsonify({"error": "Failed to fetch genres from Spotify. " + str(e)}), 500

# @app.route('/genres', methods=['GET'])
# def get_available_genres():
#     """Get available genres from Spotify or fallback to hardcoded list"""
#     try:
#         genres = sp_public.recommendation_genre_seeds()
#         return jsonify({"genres": genres['genres']})
#     except Exception as e:
#         print(f"Error getting genres: {str(e)}")
#         # Fallback: hardcoded genres
#         fallback_genres = [
#             "acoustic", "afrobeat", "alt-rock", "alternative", "ambient", "anime", "black-metal",
#             "bluegrass", "blues", "bossanova", "brazil", "breakbeat", "british", "cantopop",
#             "chicago-house", "children", "chill", "classical", "club", "comedy", "country",
#             "dance", "dancehall", "death-metal", "deep-house", "detroit-techno", "disco", "disney",
#             "drum-and-bass", "dub", "dubstep", "edm", "electro", "electronic", "emo", "folk",
#             "forro", "french", "funk", "garage", "german", "gospel", "goth", "grindcore", "groove",
#             "grunge", "guitar", "happy", "hard-rock", "hardcore", "hardstyle", "heavy-metal",
#             "hip-hop", "holidays", "honky-tonk", "house", "idm", "indian", "indie", "indie-pop",
#             "industrial", "iranian", "j-dance", "j-idol", "j-pop", "j-rock", "jazz", "k-pop",
#             "kids", "latin", "latino", "malay", "mandopop", "metal", "metal-misc", "metalcore",
#             "minimal-techno", "movies", "mpb", "new-age", "new-release", "opera", "pagode",
#             "party", "philippines-opm", "piano", "pop", "pop-film", "post-dubstep", "power-pop",
#             "progressive-house", "psych-rock", "punk", "punk-rock", "r-n-b", "rainy-day", "reggae",
#             "reggaeton", "road-trip", "rock", "rock-n-roll", "rockabilly", "romance", "sad",
#             "salsa", "samba", "sertanejo", "show-tunes", "singer-songwriter", "ska", "sleep",
#             "songwriter", "soul", "soundtracks", "spanish", "study", "summer", "swedish", "synth-pop",
#             "tango", "techno", "trance", "trip-hop", "turkish", "work-out", "world-music"
#         ]
#         return jsonify({"genres": fallback_genres}), 200

# @app.route('/auth/login', methods=['GET'])
# def login():
#     """Get Spotify authorization URL"""
#     try:
#         auth_url = sp_oauth.get_authorize_url()
#         return jsonify({"auth_url": auth_url})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route('/auth/callback', methods=['POST'])
# def callback():
#     """Handle Spotify callback and get access token"""
#     code = request.json.get('code')
#     if not code:
#         return jsonify({"error": "Authorization code required"}), 400
#     try:
#         token_info = sp_oauth.get_access_token(code)
#         return jsonify({"access_token": token_info['access_token']})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400

# @app.route('/search', methods=['GET'])
# def search_tracks():
#     """Search for tracks, artists, or albums"""
#     query = request.args.get('q')
#     search_type = request.args.get('type', 'track')
#     limit = int(request.args.get('limit', 20))
#     if not query:
#         return jsonify({"error": "Query parameter required"}), 400
#     try:
#         results = sp_public.search(q=query, type=search_type, limit=limit)
#         return jsonify(results)
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# # @app.route('/playlist/smart-generate', methods=['POST'])
# # def smart_generate_playlist():
# #     """Generate a smart playlist based on mood and genre"""
# #     data = request.json
# #     mood = data.get('mood')
# #     genre = data.get('genre', '')
# #     limit = data.get('limit', 20)
# #     if not mood:
# #         return jsonify({"error": "Mood parameter required"}), 400
# #     try:
# #         mood_features = {
# #             'happy': {'target_valence': 0.8, 'target_energy': 0.7, 'target_danceability': 0.7},
# #             'sad': {'target_valence': 0.2, 'target_energy': 0.3, 'target_acousticness': 0.7},
# #             'energetic': {'target_energy': 0.9, 'target_danceability': 0.8, 'target_tempo': 140},
# #             'chill': {'target_valence': 0.5, 'target_energy': 0.2, 'target_acousticness': 0.8},
# #             'party': {'target_danceability': 0.9, 'target_energy': 0.8, 'target_valence': 0.7}
# #         }
# #         features = mood_features.get(mood.lower(), {})
# #         seed_genres = [genre.lower()] if genre else ['pop']
# #         recommendations = sp_public.recommendations(
# #             seed_genres=seed_genres[:5],
# #             limit=limit,
# #             **features
# #         )
# #         return jsonify({
# #             "recommendations": recommendations,
# #             "mood": mood,
# #             "genre": genre,
# #             "features_used": features
# #         })
# #     except Exception as e:
# #         print(f"Error generating smart playlist: {str(e)}")
# #         return jsonify({"error": str(e)}), 500



# @app.route('/track/similar', methods=['POST'])
# def get_similar_tracks():
#     """Get tracks similar to a given track"""
#     data = request.json
#     track_id = data.get('track_id')
#     limit = data.get('limit', 10)
#     if not track_id:
#         return jsonify({"error": "Track ID required"}), 400
#     try:
#         audio_features = sp_public.audio_features([track_id])[0]
#         if not audio_features:
#             return jsonify({"error": "Could not get audio features for track"}), 400
#         track_info = sp_public.track(track_id)
#         artist_id = track_info['artists'][0]['id'] if track_info['artists'] else None
#         recommendations = sp_public.recommendations(
#             seed_tracks=[track_id],
#             seed_artists=[artist_id] if artist_id else [],
#             limit=limit,
#             target_danceability=audio_features['danceability'],
#             target_energy=audio_features['energy'],
#             target_valence=audio_features['valence'],
#             target_acousticness=audio_features['acousticness'],
#             target_instrumentalness=audio_features['instrumentalness']
#         )
#         return jsonify({
#             "tracks": recommendations['tracks'],
#             "seed_track": track_info,
#             "audio_features": audio_features
#         })
#     except Exception as e:
#         print(f"Error getting similar tracks: {str(e)}")
#         return jsonify({"error": str(e)}), 500

# @app.route('/playlist/create', methods=['POST'])
# def create_playlist():
#     """Create a new playlist (requires user authentication)"""
#     data = request.json
#     access_token = data.get('access_token')
#     name = data.get('name')
#     description = data.get('description', '')
#     track_uris = data.get('track_uris', [])
#     if not access_token or not name:
#         return jsonify({"error": "Access token and playlist name required"}), 400
#     try:
#         sp_user = spotipy.Spotify(auth=access_token)
#         user = sp_user.current_user()
#         user_id = user['id']
#         playlist = sp_user.user_playlist_create(
#             user_id, 
#             name,
#             public=True,
#             description=description
#         )
#         if track_uris:
#             sp_user.playlist_add_items(playlist['id'], track_uris)
#         return jsonify({
#             "playlist_id": playlist['id'],
#             "playlist_url": playlist['external_urls']['spotify'],
#             "message": f"Playlist '{name}' created successfully!"
#         })
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.errorhandler(404)
# def not_found(error):
#     return jsonify({"error": "Endpoint not found"}), 404

# @app.errorhandler(500)
# def internal_error(error):
#     return jsonify({"error": "Internal server error"}), 500

# if __name__ == '__main__':
#     print("🚀 Starting Flask server...")
#     print(f"📡 Frontend should connect to: http://localhost:5000")
#     print(f"🎵 Spotify Client ID: {SPOTIFY_CLIENT_ID[:10]}...")
#     app.run(debug=True, host='0.0.0.0', port=5000)




# # from flask import Flask, request, jsonify
# # from flask_cors import CORS
# # import spotipy
# # from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
# # import os
# # from dotenv import load_dotenv
# # from datetime import datetime

# # # Load environment variables from .env file
# # load_dotenv()

# # # Initialize Flask app
# # app = Flask(__name__)

# # # Configure CORS properly
# # CORS(app, 
# #      resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}},
# #      allow_headers=["Content-Type", "Authorization"],
# #      methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# # # Get Spotify API credentials
# # SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
# # SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
# # SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:5173/callback")

# # if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
# #     raise ValueError("❌ Spotify credentials are missing! Please check your .env file.")

# # # Initialize Spotipy client (public, no user login required)
# # sp_public = spotipy.Spotify(
# #     auth_manager=SpotifyClientCredentials(
# #         client_id=SPOTIFY_CLIENT_ID,
# #         client_secret=SPOTIFY_CLIENT_SECRET
# #     )
# # )

# # # Initialize OAuth for user authentication
# # sp_oauth = SpotifyOAuth(
# #     client_id=SPOTIFY_CLIENT_ID,
# #     client_secret=SPOTIFY_CLIENT_SECRET,
# #     redirect_uri=SPOTIFY_REDIRECT_URI,
# #     scope="user-library-read user-top-read playlist-modify-public playlist-modify-private"
# # )

# # # Basic routes
# # @app.route('/', methods=['GET'])
# # def home():
# #     return jsonify({"status": "Flask backend is running", "timestamp": datetime.now().isoformat()})

# # @app.route('/health', methods=['GET'])
# # def health_check():
# #     return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

# # @app.route("/ping", methods=["GET"])
# # def ping():
# #     return jsonify({"message": "pong", "timestamp": datetime.now().isoformat()})

# # # Spotify genres endpoint (this is what your frontend is trying to call)
# # @app.route('/genres', methods=['GET'])
# # def get_available_genres():
# #     """Get available genres from Spotify"""
# #     try:
# #         # Get available genre seeds from Spotify
# #         genres = sp_public.recommendation_genre_seeds()
# #         return jsonify({"genres": genres['genres']})
# #     except Exception as e:
# #         print(f"Error getting genres: {str(e)}")
# #         return jsonify({"error": str(e)}), 500

# # # Authentication routes
# # @app.route('/auth/login', methods=['GET'])
# # def login():
# #     """Get Spotify authorization URL"""
# #     try:
# #         auth_url = sp_oauth.get_authorize_url()
# #         return jsonify({"auth_url": auth_url})
# #     except Exception as e:
# #         return jsonify({"error": str(e)}), 500

# # @app.route('/auth/callback', methods=['POST'])
# # def callback():
# #     """Handle Spotify callback and get access token"""
# #     code = request.json.get('code')
# #     if not code:
# #         return jsonify({"error": "Authorization code required"}), 400
    
# #     try:
# #         token_info = sp_oauth.get_access_token(code)
# #         return jsonify({"access_token": token_info['access_token']})
# #     except Exception as e:
# #         return jsonify({"error": str(e)}), 400

# # # Search and recommendations
# # @app.route('/search', methods=['GET'])
# # def search_tracks():
# #     """Search for tracks, artists, or albums"""
# #     query = request.args.get('q')
# #     search_type = request.args.get('type', 'track')
# #     limit = int(request.args.get('limit', 20))
    
# #     if not query:
# #         return jsonify({"error": "Query parameter required"}), 400
    
# #     try:
# #         results = sp_public.search(q=query, type=search_type, limit=limit)
# #         return jsonify(results)
# #     except Exception as e:
# #         return jsonify({"error": str(e)}), 500

# # @app.route('/recommendations', methods=['POST'])
# # def get_recommendations():
# #     """Get track recommendations based on seed tracks, artists, or genres"""
# #     data = request.json
    
# #     seed_tracks = data.get('seed_tracks', [])
# #     seed_artists = data.get('seed_artists', [])
# #     seed_genres = data.get('seed_genres', [])
# #     limit = data.get('limit', 20)
    
# #     # Audio features for tuning recommendations
# #     target_danceability = data.get('target_danceability')
# #     target_energy = data.get('target_energy')
# #     target_valence = data.get('target_valence')
# #     target_tempo = data.get('target_tempo')
    
# #     if not any([seed_tracks, seed_artists, seed_genres]):
# #         return jsonify({"error": "At least one seed parameter required"}), 400
    
# #     try:
# #         recommendations = sp_public.recommendations(
# #             seed_tracks=seed_tracks[:5],  # Max 5 seeds
# #             seed_artists=seed_artists[:5],
# #             seed_genres=seed_genres[:5],
# #             limit=limit,
# #             target_danceability=target_danceability,
# #             target_energy=target_energy,
# #             target_valence=target_valence,
# #             target_tempo=target_tempo
# #         )
# #         return jsonify(recommendations)
# #     except Exception as e:
# #         return jsonify({"error": str(e)}), 500

# # @app.route('/audio-features/<track_id>', methods=['GET'])
# # def get_audio_features(track_id):
# #     """Get audio features for a specific track"""
# #     try:
# #         features = sp_public.audio_features(track_id)
# #         return jsonify(features[0] if features else None)
# #     except Exception as e:
# #         return jsonify({"error": str(e)}), 500

# # @app.route('/playlist/create', methods=['POST'])
# # def create_playlist():
# #     """Create a new playlist (requires user authentication)"""
# #     data = request.json
# #     access_token = data.get('access_token')
# #     name = data.get('name')
# #     description = data.get('description', '')
# #     track_uris = data.get('track_uris', [])
    
# #     if not access_token or not name:
# #         return jsonify({"error": "Access token and playlist name required"}), 400
    
# #     try:
# #         # Create authenticated Spotify client
# #         sp_user = spotipy.Spotify(auth=access_token)
        
# #         # Get user profile
# #         user = sp_user.current_user()
# #         user_id = user['id']
        
# #         # Create playlist
# #         playlist = sp_user.user_playlist_create(
# #             user_id, 
# #             name,
# #             public=True,
# #             description=description
# #         )
        
# #         # Add tracks if provided
# #         if track_uris:
# #             sp_user.playlist_add_items(playlist['id'], track_uris)
        
# #         return jsonify({
# #             "playlist_id": playlist['id'],
# #             "playlist_url": playlist['external_urls']['spotify'],
# #             "message": f"Playlist '{name}' created successfully!"
# #         })
    
# #     except Exception as e:
# #         return jsonify({"error": str(e)}), 500

# # @app.route('/user/top-tracks', methods=['POST'])
# # def get_user_top_tracks():
# #     """Get user's top tracks (requires user authentication)"""
# #     data = request.json
# #     access_token = data.get('access_token')
# #     time_range = data.get('time_range', 'medium_term')  # short_term, medium_term, long_term
# #     limit = data.get('limit', 20)
    
# #     if not access_token:
# #         return jsonify({"error": "Access token required"}), 400
    
# #     try:
# #         sp_user = spotipy.Spotify(auth=access_token)
# #         top_tracks = sp_user.current_user_top_tracks(
# #             limit=limit, 
# #             time_range=time_range
# #         )
# #         return jsonify(top_tracks)
# #     except Exception as e:
# #         return jsonify({"error": str(e)}), 500

# # @app.route('/test', methods=['GET'])
# # def test_spotify():
# #     """Test endpoint to verify Spotify API connection"""
# #     try:
# #         # This should return 5 tracks of "lofi" if API works
# #         results = sp_public.search(q="lofi", type="track", limit=5)
# #         return jsonify({
# #             "status": "success",
# #             "message": "Spotify API connection working",
# #             "sample_results": results
# #         })
# #     except Exception as e:
# #         return jsonify({"error": str(e)}), 500

# # # Error handlers
# # @app.errorhandler(404)
# # def not_found(error):
# #     return jsonify({"error": "Endpoint not found"}), 404

# # @app.errorhandler(500)
# # def internal_error(error):
# #     return jsonify({"error": "Internal server error"}), 500

# # if __name__ == '__main__':
# #     print("🚀 Starting Flask server...")
# #     print(f"📡 Frontend should connect to: http://localhost:5000")
# #     print(f"🎵 Spotify Client ID: {SPOTIFY_CLIENT_ID[:10]}...")
# #     app.run(debug=True, host='0.0.0.0', port=5000)


# # # from flask import Flask, request, jsonify
# # # from flask_cors import CORS
# # # import spotipy
# # # from spotipy.oauth2 import SpotifyClientCredentials
# # # import os
# # # from dotenv import load_dotenv

# # # # Load environment variables from .env file
# # # load_dotenv()

# # # # Initialize Flask app
# # # # app = Flask(__name__)
# # # # CORS(app, resources={r"/*": {"origins": "*"}})
# # # from flask import Flask
# # # from flask_cors import CORS

# # # app = Flask(__name__)

# # # # Allow React frontend to access backend
# # # # CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)
# # # CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)



# # # # Get Spotify API credentials
# # # SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
# # # SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# # # if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
# # #     raise ValueError("❌ Spotify credentials are missing! Please check your .env file.")

# # # # Initialize Spotipy client (public, no user login required)
# # # sp_public = spotipy.Spotify(
# # #     auth_manager=SpotifyClientCredentials(
# # #         client_id=SPOTIFY_CLIENT_ID,
# # #         client_secret=SPOTIFY_CLIENT_SECRET
# # #     )
# # # )

# # # # Example test route
# # # @app.route("/ping", methods=["GET"])
# # # def ping():
# # #     return jsonify({"message": "Flask + Spotify API working ✅"})


# # # # from flask import Flask, request, jsonify
# # # # from flask_cors import CORS
# # # # import spotipy
# # # # from spotipy.oauth2 import SpotifyClientCredentials
# # # # import os
# # # # from dotenv import load_dotenv

# # # # # Load environment variables
# # # # load_dotenv()

# # # # # Initialize Flask
# # # # app = Flask(__name__)
# # # # CORS(app, resources={r"/*": {"origins": "*"}})

# # # # # Spotify API credentials
# # # # SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
# # # # SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

# # # # print("SPOTIFY_CLIENT_ID:", SPOTIFY_CLIENT_ID)
# # # # print("SPOTIFY_CLIENT_SECRET:", SPOTIFY_CLIENT_SECRET)

# # # # # Public Spotify client (no login required, only client credentials)
# # # # sp_public = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
# # # #     client_id=SPOTIFY_CLIENT_ID,
# # # #     client_secret=SPOTIFY_CLIENT_SECRET
# # # # ))


# # # # from flask import Flask, request, jsonify
# # # # from flask_cors import CORS
# # # # import spotipy
# # # # from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
# # # # import os
# # # # from dotenv import load_dotenv

# # # # # Load environment variables
# # # # load_dotenv()

# # # # # Initialize Flask
# # # # app = Flask(__name__)
# # # # CORS(app, resources={r"/*": {"origins": "*"}})

# # # # # Spotify API credentials
# # # # SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
# # # # SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
# # # # SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:3000/callback')

# # # # print("SPOTIFY_CLIENT_ID:", SPOTIFY_CLIENT_ID)
# # # # print("SPOTIFY_CLIENT_SECRET:", SPOTIFY_CLIENT_SECRET)

# # # # # Public Spotify client (for recommendations, genres, search, etc.)
# # # # sp_public = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
# # # #     client_id=SPOTIFY_CLIENT_ID,
# # # #     client_secret=SPOTIFY_CLIENT_SECRET
# # # # ))

# # # # # OAuth client (for user-specific actions like creating playlists)
# # # # sp_oauth = SpotifyOAuth(
# # # #     client_id=SPOTIFY_CLIENT_ID,
# # # #     client_secret=SPOTIFY_CLIENT_SECRET,
# # # #     redirect_uri=SPOTIFY_REDIRECT_URI,
# # # #     scope="playlist-modify-public playlist-modify-private user-library-read user-top-read"
# # # # )


# # # # from flask import Flask, request, jsonify
# # # # from flask_cors import CORS
# # # # import spotipy
# # # # from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
# # # # import os
# # # # from datetime import datetime
# # # # import random
# # # # from flask import Flask
# # # # # from flask_cors import CORS

# # # # # app = Flask(__name__)

# # # # # # Allow requests from your React frontend (http://localhost:5173)
# # # # # CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
# # # # from flask import Flask
# # # # from flask_cors import CORS

# # # # app = Flask(__name__)
# # # # CORS(app, resources={r"/*": {"origins": "*"}})  # allow frontend




# # # # from dotenv import load_dotenv
# # # # load_dotenv()

# # # # CORS(app)

# # # # # Spotify API credentials - Set these as environment variables

# # # # SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
# # # # SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
# # # # SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:3000/callback')
# # # # # print("Client ID from .env:", os.getenv("SPOTIFY_CLIENT_ID"))

# # # # print("SPOTIFY_CLIENT_ID:", os.getenv("SPOTIFY_CLIENT_ID"))
# # # # print("SPOTIFY_CLIENT_SECRET:", os.getenv("SPOTIFY_CLIENT_SECRET"))
# # # # # Initialize Spotify client for public data (no user auth needed)
# # # # # client_credentials_manager = SpotifyClientCredentials(
# # # # #     client_id=SPOTIFY_CLIENT_ID,
# # # # #     client_secret=SPOTIFY_CLIENT_SECRET
# # # # # )
# # # # # sp_public = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
# # # # SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
# # # # SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
# # # # SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:3000/callback')

# # # # print("SPOTIFY_CLIENT_ID:", SPOTIFY_CLIENT_ID)
# # # # print("SPOTIFY_CLIENT_SECRET:", SPOTIFY_CLIENT_SECRET)

# # # # # Public Spotify client (for recommendations, genres, search, etc.)
# # # # sp_public = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
# # # #     client_id=SPOTIFY_CLIENT_ID,
# # # #     client_secret=SPOTIFY_CLIENT_SECRET
# # # # ))
# # # # # Spotify OAuth for user-specific operations
# # # # sp_oauth = SpotifyOAuth(
# # # #     client_id=SPOTIFY_CLIENT_ID,
# # # #     client_secret=SPOTIFY_CLIENT_SECRET,
# # # #     redirect_uri=SPOTIFY_REDIRECT_URI,
# # # #     scope="playlist-modify-public playlist-modify-private user-library-read user-top-read"
# # # # )

# # # @app.route('/health', methods=['GET'])
# # # def health_check():
# # #     return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

# # # @app.route('/auth/login', methods=['GET'])
# # # def login():
# # #     """Get Spotify authorization URL"""
# # #     auth_url = sp_oauth.get_authorize_url()
# # #     return jsonify({"auth_url": auth_url})

# # # @app.route('/auth/callback', methods=['POST'])
# # # def callback():
# # #     """Handle Spotify callback and get access token"""
# # #     code = request.json.get('code')
# # #     if not code:
# # #         return jsonify({"error": "Authorization code required"}), 400
    
# # #     try:
# # #         token_info = sp_oauth.get_access_token(code)
# # #         return jsonify({"access_token": token_info['access_token']})
# # #     except Exception as e:
# # #         return jsonify({"error": str(e)}), 400

# # # @app.route('/search', methods=['GET'])
# # # def search_tracks():
# # #     """Search for tracks, artists, or albums"""
# # #     query = request.args.get('q')
# # #     search_type = request.args.get('type', 'track')
# # #     limit = int(request.args.get('limit', 20))
    
# # #     if not query:
# # #         return jsonify({"error": "Query parameter required"}), 400
    
# # #     try:
# # #         results = sp_public.search(q=query, type=search_type, limit=limit)
# # #         return jsonify(results)
# # #     except Exception as e:
# # #         return jsonify({"error": str(e)}), 500

# # # @app.route('/recommendations', methods=['POST'])
# # # def get_recommendations():
# # #     """Get track recommendations based on seed tracks, artists, or genres"""
# # #     data = request.json
    
# # #     seed_tracks = data.get('seed_tracks', [])
# # #     seed_artists = data.get('seed_artists', [])
# # #     seed_genres = data.get('seed_genres', [])
# # #     limit = data.get('limit', 20)
    
# # #     # Audio features for tuning recommendations
# # #     target_danceability = data.get('target_danceability')
# # #     target_energy = data.get('target_energy')
# # #     target_valence = data.get('target_valence')
# # #     target_tempo = data.get('target_tempo')
    
# # #     if not any([seed_tracks, seed_artists, seed_genres]):
# # #         return jsonify({"error": "At least one seed parameter required"}), 400
    
# # #     try:
# # #         recommendations = sp_public.recommendations(
# # #             seed_tracks=seed_tracks[:5],  # Max 5 seeds
# # #             seed_artists=seed_artists[:5],
# # #             seed_genres=seed_genres[:5],
# # #             limit=limit,
# # #             target_danceability=target_danceability,
# # #             target_energy=target_energy,
# # #             target_valence=target_valence,
# # #             target_tempo=target_tempo
# # #         )
# # #         return jsonify(recommendations)
# # #     except Exception as e:
# # #         return jsonify({"error": str(e)}), 500

# # # # @app.route('/genres', methods=['GET'])
# # # # def get_available_genres():
# # # #     """Get available genres for recommendations"""
# # # #     try:
# # # #         genres = sp_public.recommendation_genre_seeds()
# # # #         return jsonify(genres)
# # # #     except Exception as e:
# # # #         return jsonify({"error": str(e)}), 500

# # # # @app.route('/genres', methods=['GET'])
# # # # def get_genres():
# # # #     try:
# # # #         available_genres = sp_public.recommendation_genre_seeds()
# # # #         return jsonify({"genres": available_genres['genres']})
# # # #     except Exception as e:
# # # #         print("Error fetching genres:", e)  # log it in console
# # # #         return jsonify({"error": str(e)}), 500

# # # # @app.route('/genres', methods=['GET'])
# # # # def get_genres():
# # # #     try:
# # # #         available_genres = sp_public.recommendation_genre_seeds()
# # # #         return jsonify({"genres": available_genres['genres']})
# # # #     except Exception as e:
# # # #         print("Error fetching genres:", e)
# # # #         return jsonify({"error": str(e)}), 500

# # # import requests

# # # SPOTIFY_API_URL = "https://api.spotify.com/v1/recommendations/available-genre-seeds"

# # # def get_genres(access_token):
# # #     headers = {
# # #         "Authorization": f"Bearer {access_token}"
# # #     }
# # #     response = requests.get(SPOTIFY_API_URL, headers=headers)

# # #     if response.status_code != 200:
# # #         print("Error:", response.status_code, response.text)
# # #         return None

# # #     return response.json().get("genres", [])

    
# # # @app.route('/audio-features/<track_id>', methods=['GET'])
# # # def get_audio_features(track_id):
# # #     """Get audio features for a specific track"""
# # #     try:
# # #         features = sp_public.audio_features(track_id)
# # #         return jsonify(features[0] if features else None)
# # #     except Exception as e:
# # #         return jsonify({"error": str(e)}), 500

# # # @app.route('/playlist/create', methods=['POST'])
# # # def create_playlist():
# # #     """Create a new playlist (requires user authentication)"""
# # #     data = request.json
# # #     access_token = data.get('access_token')
# # #     name = data.get('name')
# # #     description = data.get('description', '')
# # #     track_uris = data.get('track_uris', [])
    
# # #     if not access_token or not name:
# # #         return jsonify({"error": "Access token and playlist name required"}), 400
    
# # #     try:
# # #         # Create authenticated Spotify client
# # #         sp_user = spotipy.Spotify(auth=access_token)
        
# # #         # Get user profile
# # #         user = sp_user.current_user()
# # #         user_id = user['id']
        
# # #         # Create playlist
# # #         playlist = sp_user.user_playlist_create(
# # #             user_id, 
# # #             name, 
# # #             public=True, 
# # #             description=description
# # #         )
        
# # #         # Add tracks if provided
# # #         if track_uris:
# # #             sp_user.playlist_add_items(playlist['id'], track_uris)
        
# # #         return jsonify({
# # #             "playlist_id": playlist['id'],
# # #             "playlist_url": playlist['external_urls']['spotify'],
# # #             "message": f"Playlist '{name}' created successfully!"
# # #         })
    
# # #     except Exception as e:
# # #         return jsonify({"error": str(e)}), 500

# # # @app.route('/user/top-tracks', methods=['POST'])
# # # def get_user_top_tracks():
# # #     """Get user's top tracks (requires user authentication)"""
# # #     data = request.json
# # #     access_token = data.get('access_token')
# # #     time_range = data.get('time_range', 'medium_term')  # short_term, medium_term, long_term
# # #     limit = data.get('limit', 20)
    
# # #     if not access_token:
# # #         return jsonify({"error": "Access token required"}), 400
    
# # #     try:
# # #         sp_user = spotipy.Spotify(auth=access_token)
# # #         top_tracks = sp_user.current_user_top_tracks(
# # #             limit=limit, 
# # #             time_range=time_range
# # #         )
# # #         return jsonify(top_tracks)
# # #     except Exception as e:
# # #         return jsonify({"error": str(e)}), 500

# # # @app.route("/")
# # # def home():
# # #     return {"status": "Flask backend is running"}
# # # @app.route('/test', methods=['GET'])
# # # def test_spotify():
# # #     try:
# # #         # This should return 20 tracks of "lofi" if API works
# # #         results = sp_public.search(q="lofi", type="track", limit=5)
# # #         return jsonify(results)
# # #     except Exception as e:
# # #         return jsonify({"error": str(e)}), 500



# # # # @app.route('/playlist/smart-generate', methods=['POST'])
# # # # def smart_playlist_generator():
# # # #     data = request.json
# # # #     mood = data.get('mood', 'happy')
# # # #     genre = data.get('genre')
# # # #     limit = data.get('limit', 20)

# # # #     # Mood → audio features
# # # #     mood_mapping = {
# # # #         'happy': {'target_valence': 0.8, 'target_energy': 0.7, 'target_danceability': 0.7},
# # # #         'sad': {'target_valence': 0.2, 'target_energy': 0.3, 'target_danceability': 0.4},
# # # #         'energetic': {'target_energy': 0.9, 'target_danceability': 0.8, 'target_tempo': 120},
# # # #         'chill': {'target_valence': 0.5, 'target_energy': 0.4, 'target_danceability': 0.5},
# # # #         'party': {'target_danceability': 0.9, 'target_energy': 0.8, 'target_valence': 0.7}
# # # #     }

# # # #     mood_params = mood_mapping.get(mood, mood_mapping['happy'])

# # # #     # Validate genre
# # # #     valid_genres = sp_public.recommendation_genre_seeds()['genres']
# # # #     seed_genres = []
# # # #     if genre and genre.strip():
# # # #         if genre in valid_genres:
# # # #             seed_genres = [genre]
# # # #         else:
# # # #             return jsonify({
# # # #                 "error": f"Invalid genre '{genre}'. Must be one of {valid_genres}"
# # # #             }), 400
# # # #     else:
# # # #         seed_genres = ['pop']  # default if none provided

# # # #     try:
# # # #         recommendations = sp_public.recommendations(
# # # #             seed_genres=seed_genres,
# # # #             limit=limit,
# # # #             **mood_params
# # # #         )
# # # #         return jsonify({
# # # #             "mood": mood,
# # # #             "genre": genre,
# # # #             "recommendations": recommendations
# # # #         })
# # # #     except Exception as e:
# # # #         import traceback
# # # #         print("ERROR in /playlist/smart-generate:", traceback.format_exc())
# # # #         return jsonify({"error": str(e)}), 500
# # # @app.route('/playlist/smart-generate', methods=['POST'])
# # # def smart_playlist_generator():
# # #     data = request.json
# # #     mood = data.get('mood', 'happy')
# # #     genre = data.get('genre')
# # #     limit = data.get('limit', 20)

# # #     mood_mapping = {
# # #         'happy': {'target_valence': 0.8, 'target_energy': 0.7, 'target_danceability': 0.7},
# # #         'sad': {'target_valence': 0.2, 'target_energy': 0.3, 'target_danceability': 0.4},
# # #         'energetic': {'target_energy': 0.9, 'target_danceability': 0.8, 'target_tempo': 120},
# # #         'chill': {'target_valence': 0.5, 'target_energy': 0.4, 'target_danceability': 0.5},
# # #         'party': {'target_danceability': 0.9, 'target_energy': 0.8, 'target_valence': 0.7}
# # #     }

# # #     mood_params = mood_mapping.get(mood, mood_mapping['happy'])

# # #     try:
# # #         valid_genres = sp_public.recommendation_genre_seeds()['genres']
# # #         seed_genres = [genre] if genre and genre in valid_genres else ['pop', 'rock', 'indie']

# # #         recommendations = sp_public.recommendations(
# # #             seed_genres=seed_genres,
# # #             limit=limit,
# # #             **mood_params
# # #         )

# # #         return jsonify({
# # #             "mood": mood,
# # #             "genre": genre,
# # #             "recommendations": recommendations
# # #         })

# # #     except Exception as e:
# # #         print("Error in smart_playlist_generator:", e)
# # #         return jsonify({"error": str(e)}), 500



# # # @app.route('/track/similar', methods=['POST'])
# # # def find_similar_tracks():
# # #     """Find tracks similar to a given track"""
# # #     data = request.json
# # #     track_id = data.get('track_id')
# # #     limit = data.get('limit', 10)
    
# # #     if not track_id:
# # #         return jsonify({"error": "Track ID required"}), 400
    
# # #     try:
# # #         # Get audio features of the seed track
# # #         features = sp_public.audio_features(track_id)[0]
        
# # #         if not features:
# # #             return jsonify({"error": "Track not found"}), 404
        
# # #         # Use audio features to find similar tracks
# # #         recommendations = sp_public.recommendations(
# # #             seed_tracks=[track_id],
# # #             limit=limit,
# # #             target_danceability=features['danceability'],
# # #             target_energy=features['energy'],
# # #             target_valence=features['valence'],
# # #             target_tempo=features['tempo']
# # #         )
        
# # #         return jsonify(recommendations)
# # #     except Exception as e:
# # #         return jsonify({"error": str(e)}), 500

# # # if __name__ == '__main__':
# # #     # Check if Spotify credentials are set
# # #     if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
# # #         print("Error: Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables")
# # #         exit(1)
    
# # #     app.run(debug=True, port=5000)




# # # # from flask import Flask, request, jsonify, redirect
# # # # import spotipy
# # # # from spotipy.oauth2 import SpotifyOAuth
# # # # import os
# # # # import random

# # # # app = Flask(__name__)

# # # # # Spotify Auth setup
# # # # sp_oauth = SpotifyOAuth(
# # # #     client_id=os.getenv("SPOTIPY_CLIENT_ID"),
# # # #     client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
# # # #     redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI", "http://127.0.0.1:5000/callback"),
# # # #     scope="user-read-email playlist-modify-public user-library-read user-read-playback-state user-modify-playback-state"
# # # # )

# # # # # Dummy mood classifier (replace with TensorFlow model later)
# # # # def classify_mood(text: str) -> str:
# # # #     text = text.lower()
# # # #     if any(word in text for word in ["sad", "down", "lonely", "tired"]):
# # # #         return "sad"
# # # #     elif any(word in text for word in ["happy", "excited", "joy", "party"]):
# # # #         return "happy"
# # # #     elif any(word in text for word in ["angry", "mad", "frustrated"]):
# # # #         return "angry"
# # # #     else:
# # # #         return random.choice(["happy", "sad", "angry"])

# # # # @app.route("/api/mood/classify", methods=["POST"])
# # # # def mood_classify():
# # # #     data = request.get_json()
# # # #     text = data.get("text", "")
# # # #     mood = classify_mood(text)
# # # #     return jsonify({"mood": mood})

# # # # @app.route("/api/playlist/generate", methods=["POST"])
# # # # def generate_playlist():
# # # #     data = request.get_json()
# # # #     mood = data.get("mood", "happy")

# # # #     # Map moods to Spotify genres
# # # #     mood_to_genres = {
# # # #         "happy": ["pop", "dance", "party"],
# # # #         "sad": ["acoustic", "piano", "chill"],
# # # #         "angry": ["metal", "rock", "hardcore"]
# # # #     }

# # # #     genres = mood_to_genres.get(mood, ["pop"])

# # # #     # Get recommendations
# # # #     sp = spotipy.Spotify(auth_manager=sp_oauth)
# # # #     results = sp.recommendations(seed_genres=genres, limit=10)
# # # #     tracks = []
# # # #     for track in results["tracks"]:
# # # #         tracks.append({
# # # #             "id": track["id"],
# # # #             "name": track["name"],
# # # #             "artist": track["artists"][0]["name"],
# # # #             "preview_url": track["preview_url"],
# # # #             "external_url": track["external_urls"]["spotify"]
# # # #         })

# # # #     return jsonify({"playlist": tracks})

# # # # # Spotify OAuth callback
# # # # @app.route("/callback")
# # # # def callback():
# # # #     code = request.args.get("code")
# # # #     token_info = sp_oauth.get_access_token(code, as_dict=True)
# # # #     return jsonify(token_info)

# # # # if __name__ == "__main__":
# # # #     app.run(port=5000, debug=True)



# # # # # from flask import Flask, request, jsonify
# # # # # import spotipy
# # # # # from spotipy.oauth2 import SpotifyOAuth
# # # # # import os
# # # # # import random

# # # # # app = Flask(__name__)

# # # # # # Spotify Auth setup
# # # # # sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
# # # # #     client_id=os.getenv("SPOTIFY_CLIENT_ID"),
# # # # #     client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
# # # # #     redirect_uri=os.getenv("FRONTEND_URL", "http://localhost:5173/callback"),
# # # # #     scope="user-read-email playlist-modify-public"
# # # # # ))

# # # # # # Dummy mood classifier (replace with TensorFlow model later)
# # # # # def classify_mood(text: str) -> str:
# # # # #     text = text.lower()
# # # # #     if any(word in text for word in ["sad", "down", "lonely", "tired"]):
# # # # #         return "sad"
# # # # #     elif any(word in text for word in ["happy", "excited", "joy", "party"]):
# # # # #         return "happy"
# # # # #     elif any(word in text for word in ["angry", "mad", "frustrated"]):
# # # # #         return "angry"
# # # # #     else:
# # # # #         return random.choice(["happy", "sad", "angry"])

# # # # # @app.route("/api/mood/classify", methods=["POST"])
# # # # # def mood_classify():
# # # # #     data = request.get_json()
# # # # #     text = data.get("text", "")
# # # # #     mood = classify_mood(text)
# # # # #     return jsonify({"mood": mood})

# # # # # @app.route("/api/playlist/generate", methods=["POST"])
# # # # # def generate_playlist():
# # # # #     data = request.get_json()
# # # # #     mood = data.get("mood", "happy")

# # # # #     # Map moods to Spotify genres
# # # # #     mood_to_genres = {
# # # # #         "happy": ["pop", "dance", "party"],
# # # # #         "sad": ["acoustic", "piano", "chill"],
# # # # #         "angry": ["metal", "rock", "hardcore"]
# # # # #     }

# # # # #     genres = mood_to_genres.get(mood, ["pop"])

# # # # #     # Get recommendations
# # # # #     results = sp.recommendations(seed_genres=genres, limit=10)
# # # # #     tracks = []
# # # # #     for track in results["tracks"]:
# # # # #         tracks.append({
# # # # #             "id": track["id"],
# # # # #             "name": track["name"],
# # # # #             "artist": track["artists"][0]["name"],
# # # # #             "preview_url": track["preview_url"],
# # # # #             "external_url": track["external_urls"]["spotify"]
# # # # #         })

# # # # #     return jsonify({"playlist": tracks})

# # # # # if __name__ == "__main__":
# # # # #     app.run(port=5000, debug=True)
