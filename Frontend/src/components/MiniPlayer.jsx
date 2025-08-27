import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, Volume2, VolumeX, SkipBack, SkipForward, Music, Plus, Trash2 } from 'lucide-react';
import { audioPreviewManager, extractTrackInfo } from '../services/api.js';
import PlayButton from './PlayButton.jsx';

// Mini Player Component (appears at bottom when playing)
const MiniPlayer = ({ className = '' }) => {
  const [playbackState, setPlaybackState] = useState(null);
  const [currentTrack, setCurrentTrack] = useState(null);
  const [volume, setVolume] = useState(0.7);
  const [showVolumeControl, setShowVolumeControl] = useState(false);

  useEffect(() => {
    const unsubscribe = audioPreviewManager.subscribe((state) => {
      setPlaybackState(state);
    });

    // Get initial state
    const initialState = audioPreviewManager.getPlaybackState();
    setPlaybackState(initialState);
    setVolume(audioPreviewManager.getVolume());

    return unsubscribe;
  }, []);

  // Update current track info when playback state changes
  useEffect(() => {
    if (playbackState?.currentTrackId) {
      // You might need to store track info in the audio manager or pass it differently
      // For now, we'll show basic info
      setCurrentTrack({
        id: playbackState.currentTrackId,
        name: 'Playing...',
        artist: 'Loading...'
      });
    } else {
      setCurrentTrack(null);
    }
  }, [playbackState?.currentTrackId]);

  const handlePlayPause = () => {
    if (playbackState?.isPlaying) {
      audioPreviewManager.pause();
    } else {
      audioPreviewManager.resume();
    }
  };

  const handleVolumeChange = (e) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    audioPreviewManager.setVolume(newVolume);
  };

  const handleSeek = (e) => {
    const progressBar = e.currentTarget;
    const rect = progressBar.getBoundingClientRect();
    const percent = (e.clientX - rect.left) / rect.width;
    const seekTime = percent * (playbackState?.duration || 0);
    audioPreviewManager.seek(seekTime);
  };

  const formatTime = (seconds) => {
    if (!seconds || isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Don't show if nothing is playing
  if (!playbackState?.currentTrackId) {
    return null;
  }

  const progress = playbackState.duration > 0 
    ? (playbackState.currentTime / playbackState.duration) * 100 
    : 0;

  return (
    <div className={`
      fixed bottom-0 left-0 right-0 z-50
      bg-black/90 backdrop-blur-lg border-t border-white/10
      px-4 py-3 ${className}
    `}>
      <div className="max-w-6xl mx-auto flex items-center gap-4">
        {/* Track Info */}
        <div className="flex items-center gap-3 min-w-0 flex-1">
          <div className="w-12 h-12 rounded-lg bg-white/10 flex items-center justify-center flex-shrink-0">
            <Music className="w-6 h-6 text-white/60" />
          </div>
          <div className="min-w-0">
            <div className="text-white font-medium truncate">
              {currentTrack?.name || 'Unknown Track'}
            </div>
            <div className="text-white/60 text-sm truncate">
              {currentTrack?.artist || 'Unknown Artist'}
            </div>
          </div>
        </div>

        {/* Playback Controls */}
        <div className="flex items-center gap-4">
          {/* Play/Pause */}
          <button
            onClick={handlePlayPause}
            className="w-10 h-10 rounded-full bg-white/10 hover:bg-white/20 text-white flex items-center justify-center transition-all duration-300 hover:scale-110"
          >
            {playbackState?.isPlaying ? (
              <Pause className="w-5 h-5" />
            ) : (
              <Play className="w-5 h-5 ml-0.5" />
            )}
          </button>

          {/* Progress Bar */}
          <div className="flex items-center gap-2 flex-1 max-w-md">
            <span className="text-xs text-white/60 w-10 text-right">
              {formatTime(playbackState?.currentTime)}
            </span>
            <div 
              className="flex-1 h-1 bg-white/20 rounded-full cursor-pointer group"
              onClick={handleSeek}
            >
              <div 
                className="h-full bg-gradient-to-r from-purple-400 to-pink-400 rounded-full transition-all duration-150 group-hover:h-1.5"
                style={{ width: `${progress}%` }}
              />
            </div>
            <span className="text-xs text-white/60 w-10">
              {formatTime(playbackState?.duration)}
            </span>
          </div>

          {/* Volume Control */}
          <div className="relative">
            <button
              onClick={() => setShowVolumeControl(!showVolumeControl)}
              className="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 text-white/70 hover:text-white flex items-center justify-center transition-all duration-300"
            >
              {volume === 0 ? (
                <VolumeX className="w-4 h-4" />
              ) : (
                <Volume2 className="w-4 h-4" />
              )}
            </button>

            {/* Volume Slider */}
            {showVolumeControl && (
              <div className="absolute bottom-full right-0 mb-2 p-2 bg-black/90 backdrop-blur-lg rounded-lg border border-white/20">
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={volume}
                  onChange={handleVolumeChange}
                  className="w-20 h-1 bg-white/20 rounded-full appearance-none cursor-pointer"
                  style={{
                    background: `linear-gradient(to right, #8b5cf6 0%, #ec4899 ${volume * 100}%, rgba(255,255,255,0.2) ${volume * 100}%, rgba(255,255,255,0.2) 100%)`
                  }}
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Volume Control Component
const VolumeControl = ({ className = '' }) => {
  const [volume, setVolume] = useState(0.7);
  const [showSlider, setShowSlider] = useState(false);

  useEffect(() => {
    setVolume(audioPreviewManager.getVolume());
  }, []);

  const handleVolumeChange = (e) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    audioPreviewManager.setVolume(newVolume);
  };

  const toggleMute = () => {
    const newVolume = volume === 0 ? 0.7 : 0;
    setVolume(newVolume);
    audioPreviewManager.setVolume(newVolume);
  };

  return (
    <div className={`relative ${className}`}>
      <button
        onClick={toggleMute}
        onMouseEnter={() => setShowSlider(true)}
        onMouseLeave={() => setShowSlider(false)}
        className="w-10 h-10 rounded-full bg-white/10 hover:bg-white/20 text-white/70 hover:text-white flex items-center justify-center transition-all duration-300"
      >
        {volume === 0 ? (
          <VolumeX className="w-4 h-4" />
        ) : (
          <Volume2 className="w-4 h-4" />
        )}
      </button>

      {showSlider && (
        <div 
          className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 p-3 bg-black/90 backdrop-blur-lg rounded-lg border border-white/20"
          onMouseEnter={() => setShowSlider(true)}
          onMouseLeave={() => setShowSlider(false)}
        >
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={volume}
            onChange={handleVolumeChange}
            className="w-20 h-2 bg-white/20 rounded-full appearance-none cursor-pointer"
            style={{
              background: `linear-gradient(to right, #8b5cf6 0%, #ec4899 ${volume * 100}%, rgba(255,255,255,0.2) ${volume * 100}%, rgba(255,255,255,0.2) 100%)`
            }}
          />
          <div className="text-center text-xs text-white/60 mt-1">
            {Math.round(volume * 100)}%
          </div>
        </div>
      )}
    </div>
  );
};

// Compact Track Row Component (for playlist views)
const TrackRow = ({ 
  track, 
  index,
  onAddToPlaylist = null,
  onRemoveFromPlaylist = null,
  onGetSimilar = null,
  showRemove = false,
  showAdd = true,
  className = ''
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const trackInfo = extractTrackInfo(track);

  const handleAddToPlaylist = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (onAddToPlaylist) onAddToPlaylist(track);
  };

  const handleRemoveFromPlaylist = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (onRemoveFromPlaylist) onRemoveFromPlaylist(track.id);
  };

  return (
    <div 
      className={`
        group flex items-center gap-4 p-3 rounded-lg
        hover:bg-white/5 transition-all duration-300
        ${className}
      `}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Track Number / Play Button */}
      <div className="w-8 flex items-center justify-center">
        {isHovered ? (
          <PlayButton track={track} size="sm" variant="minimal" />
        ) : (
          <span className="text-white/40 text-sm font-medium">
            {(index + 1).toString().padStart(2, '0')}
          </span>
        )}
      </div>

      {/* Album Cover */}
      <div className="w-10 h-10 rounded bg-white/10 overflow-hidden flex-shrink-0">
        {trackInfo.imageUrl ? (
          <img 
            src={trackInfo.imageUrl} 
            alt="Album cover"
            className="w-full h-full object-cover"
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'flex';
            }}
          />
        ) : null}
        <div className={`w-full h-full flex items-center justify-center ${trackInfo.imageUrl ? 'hidden' : 'flex'}`}>
          <Music className="w-4 h-4 text-white/40" />
        </div>
      </div>

      {/* Track Info */}
      <div className="flex-1 min-w-0">
        <div className="text-white font-medium truncate group-hover:text-purple-300 transition-colors">
          {trackInfo.name}
        </div>
        <div className="text-white/60 text-sm truncate">
          {trackInfo.artist}
        </div>
      </div>

      {/* Album */}
      <div className="hidden md:block flex-1 min-w-0">
        <div className="text-white/60 text-sm truncate">
          {trackInfo.album}
        </div>
      </div>

      {/* Duration */}
      <div className="text-white/40 text-sm w-12 text-right">
        {trackInfo.duration}
      </div>

      {/* Actions */}
      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        {showAdd && onAddToPlaylist && (
          <button
            onClick={handleAddToPlaylist}
            className="w-8 h-8 rounded-full hover:bg-white/10 text-white/60 hover:text-green-400 flex items-center justify-center transition-colors"
            title="Add to playlist"
          >
            <Plus className="w-4 h-4" />
          </button>
        )}

        {showRemove && onRemoveFromPlaylist && (
          <button
            onClick={handleRemoveFromPlaylist}
            className="w-8 h-8 rounded-full hover:bg-white/10 text-white/60 hover:text-red-400 flex items-center justify-center transition-colors"
            title="Remove from playlist"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
};

export { MiniPlayer, VolumeControl, TrackRow };