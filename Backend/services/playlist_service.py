def generate_playlist(mood: str):
    # Dummy playlist generator
    playlists = {
        "happy": ["Happy Song 1", "Happy Song 2"],
        "sad": ["Sad Song 1", "Sad Song 2"],
        "energetic": ["Energetic Song 1", "Energetic Song 2"],
    }
    return playlists.get(mood, playlists["happy"])
