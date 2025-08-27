import React, { useState, useEffect } from 'react';
import { Play, Pause, ExternalLink, Music, Clock, User, Album } from 'lucide-react';
import { playTrack, audioPreviewManager, extractTrackInfo } from '../services/api';

// Individual Track Item Component
const TrackItem = ({ track, index, onPlay, isPlaying, showIndex = true }) => {
  const [isLoading, setIsLoading] = useState(false);
  const trackInfo = extractTrackInfo(track);

  const handlePlay = async () => {
    setIsLoading(true);
    try {
      await onPlay(track);
    } catch (error) {
      console.error('Play failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const openInSpotify = () => {
    if (trackInfo.playUrls.spotify_web) {
      window.open(trackInfo.playUrls.spotify_web, '_blank');
    }
  };

  return (
    <div className="flex items-center gap-4 p-4 hover:bg-gray-50 rounded-lg transition-colors group">
      {/* Index/Play Button */}
      <div className="flex-shrink-0 w-12 text-center">
        {showIndex && !isPlaying && !isLoading && (
          <span className="text-gray-500 group-hover:hidden">{index + 1}</span>
        )}
        <button
          onClick={handlePlay}
          disabled={isLoading}
          className="w-8 h-8 flex items-center justify-center rounded-full bg-green-500 text-white hover:bg-green-600 transition-colors group-hover:flex hidden disabled:opacity-50"
        >
          {isLoading ? (
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : isPlaying ? (
            <Pause size={16} />
          ) : (
            <Play size={16} />
          )}
        </button>
      </div>

      {/* Track Image */}
      <div className="flex-shrink-0 w-12 h-12">
        {trackInfo.imageUrl ? (
          <img
            src={trackInfo.imageUrl}
            alt={trackInfo.album}
            className="w-12 h-12 rounded object-cover"
          />
        ) : (
          <div className="w-12 h-12 bg-gray-200 rounded flex items-center justify-center">
            <Music size={20} className="text-gray-400" />
          </div>
        )}
      </div>

      {/* Track Info */}
      <div className="flex-grow min-w-0">
        <h3 className="font-medium text-gray-900 truncate">{trackInfo.name}</h3>
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <User size={14} />
          <span className="truncate">{trackInfo.artist}</span>
        </div>
        {trackInfo.album && (
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Album size={14} />
            <span className="truncate">{trackInfo.album}</span>
          </div>
        )}
      </div>

      {/* Duration */}
      <div className="flex-shrink-0 text-sm text-gray-500 flex items-center gap-1">
        <Clock size={14} />
        {trackInfo.duration}
      </div>

      {/* Spotify Link */}
      <button
        onClick={openInSpotify}
        className="flex-shrink-0 p-2 text-gray-400 hover:text-green-500 transition-colors"
        title="Open in Spotify"
      >
        <ExternalLink size={16} />
      </button>
    </div>
  );
};

// Main Track Player Component
const TrackPlayer = ({ tracks = [], title = "Tracks", showHeader = true, className = "" }) => {
  const [currentPlayingId, setCurrentPlayingId] = useState(null);

  useEffect(() => {
    // Listen for audio ended events to reset playing state
    const handleAudioEnd = () => {
      setCurrentPlayingId(null);
    };

    // Check current playing track on mount
    const currentId = audioPreviewManager.getCurrentTrackId();
    if (currentId && audioPreviewManager.isCurrentlyPlaying(currentId)) {
      setCurrentPlayingId(currentId);
    }

    return () => {
      // Cleanup if needed
    };
  }, []);

  const handleTrackPlay = async (track) => {
    const trackInfo = extractTrackInfo(track);
    
    try {
      const result = await playTrack(track);
      
      if (result.success) {
        if (result.action === 'playing_preview') {
          setCurrentPlayingId(trackInfo.id);
        } else if (result.action === 'paused') {
          setCurrentPlayingId(null);
        } else {
          // Opened in Spotify
          setCurrentPlayingId(null);
        }
      }
    } catch (error) {
      console.error('Error playing track:', error);
      setCurrentPlayingId(null);
    }
  };

  if (!tracks || tracks.length === 0) {
    return (
      <div className={`text-center py-8 text-gray-500 ${className}`}>
        <Music size={48} className="mx-auto mb-4 text-gray-300" />
        <p>No tracks available</p>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow-sm ${className}`}>
      {showHeader && (
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">{title}</h2>
          <p className="text-sm text-gray-600 mt-1">
            {tracks.length} track{tracks.length !== 1 ? 's' : ''}
          </p>
        </div>
      )}
      
      <div className="divide-y divide-gray-100">
        {tracks.map((track, index) => (
          <TrackItem
            key={track.id || index}
            track={track}
            index={index}
            onPlay={handleTrackPlay}
            isPlaying={currentPlayingId === extractTrackInfo(track).id}
          />
        ))}
      </div>
    </div>
  );
};

// Mini Player Component (for currently playing track)
export const MiniPlayer = () => {
  const [currentTrack, setCurrentTrack] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    const checkCurrentTrack = () => {
      const trackId = audioPreviewManager.getCurrentTrackId();
      const playing = audioPreviewManager.isCurrentlyPlaying(trackId);
      
      setIsPlaying(playing);
      
      // You might want to store current track info somewhere accessible
      // For now, this is a placeholder
    };

    const interval = setInterval(checkCurrentTrack, 1000);
    return () => clearInterval(interval);
  }, []);

  const handlePlayPause = async () => {
    if (isPlaying) {
      audioPreviewManager.pause();
      setIsPlaying(false);
    }
    // Note: To resume, you'd need to store the current track and replay it
  };

  if (!currentTrack && !isPlaying) {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-4 bg-white shadow-lg rounded-lg p-4 flex items-center gap-3 min-w-80">
      <button
        onClick={handlePlayPause}
        className="w-10 h-10 bg-green-500 text-white rounded-full flex items-center justify-center hover:bg-green-600 transition-colors"
      >
        {isPlaying ? <Pause size={16} /> : <Play size={16} />}
      </button>
      
      <div className="flex-grow">
        <p className="font-medium text-sm">Preview Playing</p>
        <p className="text-xs text-gray-600">30-second preview</p>
      </div>
      
      <button
        onClick={() => audioPreviewManager.stop()}
        className="text-gray-400 hover:text-gray-600"
      >
        ×
      </button>
    </div>
  );
};

// Playlist Component with Save Functionality
export const PlaylistManager = ({ tracks, onSavePlaylist }) => {
  const [playlistName, setPlaylistName] = useState('');
  const [isPublic, setIsPublic] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  const handleSavePlaylist = async () => {
    if (!playlistName.trim() || !tracks.length) return;

    setIsSaving(true);
    try {
      // You'll need to get the access token from your auth state
      const accessToken = localStorage.getItem('spotify_access_token'); // or from your auth context
      
      if (!accessToken) {
        alert('Please login to Spotify first');
        return;
      }

      const trackUris = tracks.map(track => extractTrackInfo(track).uri);
      await onSavePlaylist(accessToken, playlistName, '', trackUris, isPublic);
      
      setPlaylistName('');
      alert('Playlist saved successfully!');
    } catch (error) {
      console.error('Failed to save playlist:', error);
      alert('Failed to save playlist. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="bg-gray-50 p-4 rounded-lg mt-4">
      <h3 className="font-medium text-gray-900 mb-3">Save as Playlist</h3>
      
      <div className="space-y-3">
        <input
          type="text"
          value={playlistName}
          onChange={(e) => setPlaylistName(e.target.value)}
          placeholder="Enter playlist name..."
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-green-500"
        />
        
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="public-playlist"
            checked={isPublic}
            onChange={(e) => setIsPublic(e.target.checked)}
            className="rounded"
          />
          <label htmlFor="public-playlist" className="text-sm text-gray-700">
            Make playlist public
          </label>
        </div>
        
        <button
          onClick={handleSavePlaylist}
          disabled={!playlistName.trim() || !tracks.length || isSaving}
          className="w-full bg-green-500 text-white py-2 px-4 rounded-md hover:bg-green-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSaving ? 'Saving...' : `Save ${tracks.length} tracks to Spotify`}
        </button>
      </div>
    </div>
  );
};

export default TrackPlayer;