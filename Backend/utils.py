def enhance_track_with_play_urls(track):
    """Add play URLs and formatted duration to a track object"""
    if not track:
        return track
    
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
    
    return track

def enhance_tracks_list(tracks):
    """Enhance a list of tracks with play URLs"""
    return [enhance_track_with_play_urls(track) for track in tracks]

def get_fallback_genres():
    """Get fallback list of genres when Spotify API fails"""
    return [
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

def get_mood_features():
    """Get audio features mapping for different moods"""
    return {
        'happy': {'target_valence': 0.8, 'target_energy': 0.7, 'target_danceability': 0.7},
        'sad': {'target_valence': 0.2, 'target_energy': 0.3, 'target_acousticness': 0.7},
        'energetic': {'target_energy': 0.9, 'target_danceability': 0.8},
        'chill': {'target_valence': 0.5, 'target_energy': 0.2, 'target_acousticness': 0.8},
        'party': {'target_danceability': 0.9, 'target_energy': 0.8, 'target_valence': 0.7}
    }

def get_mood_search_terms():
    """Get search terms for different moods as fallback"""
    return {
        'happy': 'happy upbeat positive',
        'sad': 'sad melancholy emotional',
        'energetic': 'energetic pump up workout',
        'chill': 'chill relaxing ambient',
        'party': 'party dance club'
    }

def safe_get_genres(sp_client, fallback_genres=None):
    """Safely get available genres with fallback"""
    if fallback_genres is None:
        fallback_genres = ['pop', 'rock', 'jazz']
    
    try:
        genres_response = sp_client.recommendation_genre_seeds()
        return genres_response.get('genres', fallback_genres)
    except Exception as e:
        print(f"Could not get genres from Spotify: {e}")
        return fallback_genres

def validate_and_get_seed_genres(requested_genre, available_genres):
    """Validate requested genre and return appropriate seed genres"""
    if requested_genre and requested_genre.lower() in available_genres:
        return [requested_genre.lower()]
    
    # Use safe default genres
    safe_defaults = ['pop', 'rock', 'electronic', 'hip-hop', 'indie']
    seed_genres = [g for g in safe_defaults if g in available_genres][:1]
    
    if not seed_genres and available_genres:
        seed_genres = [available_genres[0]]
    elif not seed_genres:
        seed_genres = ['pop']  # Ultimate fallback
    
    return seed_genres