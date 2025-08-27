import { BACKEND_URL } from '../constants/index.js';

// Generic API call handler
const apiCall = async (url, options = {}) => {
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });
     
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
     
    return await response.json();
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
};

// Fetch available genres
export const fetchGenres = async () => {
  const data = await apiCall(`${BACKEND_URL}/genres`);
  return data.genres || [];
};

// Search for tracks (now includes play URLs)
export const searchTracks = async (query, limit = 20) => {
  if (!query.trim()) return [];
   
  const data = await apiCall(`${BACKEND_URL}/search?q=${encodeURIComponent(query)}&type=track&limit=${limit}`);
  return data.tracks?.items || [];
};

// Get music recommendations (now includes play URLs)
export const getRecommendations = async (mood, genre = '', limit = 20) => {
  const data = await apiCall(`${BACKEND_URL}/playlist/smart-generate`, {
    method: 'POST',
    body: JSON.stringify({
      mood,
      genre,
      limit
    })
  });
  return data.recommendations?.tracks || [];
};

// Get similar tracks (now includes play URLs)
export const getSimilarTracks = async (trackId, limit = 10) => {
  const data = await apiCall(`${BACKEND_URL}/track/similar`, {
    method: 'POST',
    body: JSON.stringify({
       track_id: trackId,
       limit
     })
  });
  return data.tracks || [];
};

// Get play URLs for a specific track
export const getTrackPlayUrls = async (trackId) => {
  const data = await apiCall(`${BACKEND_URL}/track/play-url?track_id=${trackId}`);
  return data;
};

// Authenticate with Spotify
export const authenticateSpotify = async () => {
  const data = await apiCall(`${BACKEND_URL}/auth/login`);
  if (data.auth_url) {
    window.open(data.auth_url, '_blank', 'width=400,height=600');
  }
  return data;
};

// Handle Spotify callback
export const handleSpotifyCallback = async (code) => {
  const data = await apiCall(`${BACKEND_URL}/auth/callback`, {
    method: 'POST',
    body: JSON.stringify({ code })
  });
  return data;
};

// Create playlist on Spotify (enhanced with better persistence)
export const createSpotifyPlaylist = async (accessToken, name, description, trackUris, isPublic = true) => {
  const data = await apiCall(`${BACKEND_URL}/playlist/create`, {
    method: 'POST',
    body: JSON.stringify({
      access_token: accessToken,
      name,
      description: description || `Created by Music App on ${new Date().toLocaleDateString()}`,
      track_uris: trackUris,
      public: isPublic
    })
  });
  return data;
};

// Fetch user's playlists
export const fetchUserPlaylists = async (accessToken) => {
  const data = await apiCall(`${BACKEND_URL}/user/playlists`, {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  return data.playlists || [];
};

// Get tracks from a specific playlist
export const getPlaylistTracks = async (playlistId, accessToken = null) => {
  const headers = accessToken ? { 'Authorization': `Bearer ${accessToken}` } : {};
  
  const data = await apiCall(`${BACKEND_URL}/playlist/${playlistId}/tracks`, {
    headers
  });
  return data.items || [];
};

// Utility function to format track duration
export const formatDuration = (durationMs) => {
  if (!durationMs) return '0:00';
  
  const totalSeconds = Math.floor(durationMs / 1000);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  
  return `${minutes}:${seconds.toString().padStart(2, '0')}`;
};

// Utility function to extract track info for display
export const extractTrackInfo = (track) => {
  return {
    id: track.id,
    name: track.name,
    artist: track.artists?.map(artist => artist.name).join(', ') || 'Unknown Artist',
    album: track.album?.name || 'Unknown Album',
    duration: formatDuration(track.duration_ms),
    imageUrl: track.album?.images?.[0]?.url || null,
    playUrls: track.play_urls || {
      spotify_web: track.external_urls?.spotify,
      spotify_app: `spotify:track:${track.id}`,
      preview_url: track.preview_url
    },
    uri: track.uri
  };
};

// Audio preview management with subscription support
class AudioPreviewManager {
  constructor() {
    this.currentAudio = null;
    this.currentTrackId = null;
    this.isPlaying = false;
    this.volume = 0.7;
    this.subscribers = [];
    this.currentTime = 0;
    this.duration = 0;
  }

  notify() {
    const state = this.getPlaybackState();
    this.subscribers.forEach(cb => cb(state));
  }

  subscribe(cb) {
    this.subscribers.push(cb);
    // Immediately call with current state
    cb(this.getPlaybackState());
    // Return unsubscribe function
    return () => {
      this.subscribers = this.subscribers.filter(fn => fn !== cb);
    };
  }

  getPlaybackState() {
    return {
      currentTrackId: this.currentTrackId,
      isPlaying: this.isPlaying,
      currentTime: this.currentAudio ? this.currentAudio.currentTime : 0,
      duration: this.currentAudio ? this.currentAudio.duration : 0,
    };
  }

  getVolume() {
    return this.volume;
  }

  setVolume(vol) {
    this.volume = vol;
    if (this.currentAudio) {
      this.currentAudio.volume = vol;
    }
    this.notify();
  }

  async playPreview(track) {
    const trackInfo = extractTrackInfo(track);

    // If same track is playing, pause it
    if (this.currentTrackId === trackInfo.id && this.isPlaying) {
      this.pause();
      return { success: true, action: 'paused' };
    }

    // Stop current audio if playing
    this.stop();

    // Try to play preview
    if (trackInfo.playUrls.preview_url) {
      try {
        this.currentAudio = new Audio(trackInfo.playUrls.preview_url);
        this.currentAudio.volume = this.volume;
        this.currentTrackId = trackInfo.id;

        this.currentAudio.addEventListener('ended', () => {
          this.isPlaying = false;
          this.currentTrackId = null;
          this.notify();
        });

        this.currentAudio.addEventListener('timeupdate', () => {
          this.notify();
        });

        await this.currentAudio.play();
        this.isPlaying = true;
        this.notify();

        return { success: true, action: 'playing_preview' };
      } catch (error) {
        console.error('Preview playback failed:', error);
        // Fallback to Spotify
        this.openInSpotify(trackInfo);
        this.notify();
        return { success: true, action: 'opened_spotify' };
      }
    } else {
      // No preview available, open in Spotify
      this.openInSpotify(trackInfo);
      this.notify();
      return { success: true, action: 'opened_spotify' };
    }
  }

  pause() {
    if (this.currentAudio) {
      this.currentAudio.pause();
      this.isPlaying = false;
      this.notify();
    }
  }

  resume() {
    if (this.currentAudio && !this.isPlaying) {
      this.currentAudio.play();
      this.isPlaying = true;
      this.notify();
    }
  }

  stop() {
    if (this.currentAudio) {
      this.currentAudio.pause();
      this.currentAudio.currentTime = 0;
      this.isPlaying = false;
      this.currentTrackId = null;
      this.notify();
    }
  }

  seek(time) {
    if (this.currentAudio) {
      this.currentAudio.currentTime = time;
      this.notify();
    }
  }

  openInSpotify(trackInfo) {
    // Try to open in Spotify app first, fallback to web
    const userAgent = navigator.userAgent.toLowerCase();
    const isMobile = /android|iphone|ipad|ipod|blackberry|iemobile|opera mini/.test(userAgent);
    
    if (isMobile && trackInfo.playUrls.spotify_app) {
      // On mobile, try to open Spotify app
      window.location.href = trackInfo.playUrls.spotify_app;
      
      // Fallback to web after a short delay
      setTimeout(() => {
        window.open(trackInfo.playUrls.spotify_web, '_blank');
      }, 1000);
    } else {
      // On desktop, open web player
      window.open(trackInfo.playUrls.spotify_web, '_blank');
    }
  }

  getCurrentTrackId() {
    return this.currentTrackId;
  }

  isCurrentlyPlaying(trackId) {
    return this.currentTrackId === trackId && this.isPlaying;
  }
}

// Export singleton instance
export const audioPreviewManager = new AudioPreviewManager();

// Convenience function for playing tracks
export const playTrack = async (track) => {
  return await audioPreviewManager.playPreview(track);
};

