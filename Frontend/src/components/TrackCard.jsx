import React, { useState } from 'react';
import { Heart, Plus, Trash2, ExternalLink, Music, Clock } from 'lucide-react';
import PlayButton from './PlayButton.jsx';
import { extractTrackInfo } from '../services/api.js';

const TrackCard = ({ 
  track, 
  onAddToPlaylist = null,
  onRemoveFromPlaylist = null,
  onGetSimilar = null,
  showRemove = false,
  showAdd = true,
  showSimilar = false,
  className = ''
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const trackInfo = extractTrackInfo(track);

  const handleAddToPlaylist = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (onAddToPlaylist) {
      onAddToPlaylist(track);
    }
  };

  const handleRemoveFromPlaylist = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (onRemoveFromPlaylist) {
      onRemoveFromPlaylist(track.id);
    }
  };

  const handleGetSimilar = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (onGetSimilar) {
      onGetSimilar(track.id);
    }
  };

  const handleOpenSpotify = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (trackInfo.playUrls.spotify_web) {
      window.open(trackInfo.playUrls.spotify_web, '_blank');
    }
  };

  return (
    <div 
      className={`
        group relative bg-white/5 backdrop-blur-sm rounded-xl border border-white/10
        hover:bg-white/10 hover:border-white/20 transition-all duration-300
        transform hover:scale-[1.02] hover:shadow-2xl
        ${className}
      `}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Background gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-pink-500/5 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      
      <div className="relative p-4">
        <div className="flex items-start gap-4">
          {/* Album Cover */}
          <div className="relative flex-shrink-0">
            <div className="w-16 h-16 rounded-lg overflow-hidden bg-white/10 border border-white/20">
              {trackInfo.imageUrl ? (
                <img 
                  src={trackInfo.imageUrl} 
                  alt={`${trackInfo.album} cover`}
                  className="w-full h-full object-cover transform group-hover:scale-110 transition-transform duration-300"
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'flex';
                  }}
                />
              ) : null}
              {/* Fallback icon */}
              <div className={`w-full h-full flex items-center justify-center ${trackInfo.imageUrl ? 'hidden' : 'flex'}`}>
                <Music className="w-6 h-6 text-white/40" />
              </div>
            </div>
            
            {/* Play button overlay */}
            <div className="absolute inset-0 flex items-center justify-center bg-black/50 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300">
              <PlayButton 
                track={track} 
                size="sm" 
                variant="primary"
              />
            </div>
          </div>

          {/* Track Information */}
          <div className="flex-1 min-w-0">
            {/* Track Name */}
            <h3 className="font-semibold text-white text-lg leading-tight mb-1 truncate group-hover:text-purple-300 transition-colors duration-300">
              {trackInfo.name}
            </h3>
            
            {/* Artist */}
            <p className="text-white/70 text-sm mb-2 truncate group-hover:text-white/80 transition-colors duration-300">
              {trackInfo.artist}
            </p>
            
            {/* Album and Duration */}
            <div className="flex items-center gap-3 text-xs text-white/50">
              <span className="truncate flex-1">{trackInfo.album}</span>
              {trackInfo.duration && (
                <div className="flex items-center gap-1 flex-shrink-0">
                  <Clock className="w-3 h-3" />
                  <span>{trackInfo.duration}</span>
                </div>
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2">
            {/* Play Button (always visible on mobile, hover on desktop) */}
            <div className="md:opacity-0 md:group-hover:opacity-100 transition-opacity duration-300">
              <PlayButton 
                track={track} 
                size="md" 
                variant="default"
              />
            </div>

            {/* Add to Playlist */}
            {showAdd && onAddToPlaylist && (
              <button
                onClick={handleAddToPlaylist}
                className="w-10 h-10 rounded-full bg-white/10 hover:bg-green-500/20 border border-white/20 hover:border-green-500/50 text-white/70 hover:text-green-400 transition-all duration-300 flex items-center justify-center group/btn"
                title="Add to playlist"
              >
                <Plus className="w-4 h-4 transition-transform duration-300 group-hover/btn:scale-110" />
              </button>
            )}

            {/* Remove from Playlist */}
            {showRemove && onRemoveFromPlaylist && (
              <button
                onClick={handleRemoveFromPlaylist}
                className="w-10 h-10 rounded-full bg-white/10 hover:bg-red-500/20 border border-white/20 hover:border-red-500/50 text-white/70 hover:text-red-400 transition-all duration-300 flex items-center justify-center group/btn"
                title="Remove from playlist"
              >
                <Trash2 className="w-4 h-4 transition-transform duration-300 group-hover/btn:scale-110" />
              </button>
            )}

            {/* Get Similar Tracks */}
            {showSimilar && onGetSimilar && (
              <button
                onClick={handleGetSimilar}
                className="w-10 h-10 rounded-full bg-white/10 hover:bg-purple-500/20 border border-white/20 hover:border-purple-500/50 text-white/70 hover:text-purple-400 transition-all duration-300 flex items-center justify-center group/btn"
                title="Find similar tracks"
              >
                <Heart className="w-4 h-4 transition-transform duration-300 group-hover/btn:scale-110" />
              </button>
            )}

            {/* Open in Spotify */}
            {trackInfo.playUrls.spotify_web && (
              <button
                onClick={handleOpenSpotify}
                className="w-10 h-10 rounded-full bg-white/10 hover:bg-spotify-green/20 border border-white/20 hover:border-green-500/50 text-white/70 hover:text-green-400 transition-all duration-300 flex items-center justify-center group/btn opacity-0 group-hover:opacity-100"
                title="Open in Spotify"
              >
                <ExternalLink className="w-4 h-4 transition-transform duration-300 group-hover/btn:scale-110" />
              </button>
            )}
          </div>
        </div>

        {/* Preview URL indicator */}
        {trackInfo.playUrls.preview_url && (
          <div className="absolute top-2 right-2 w-2 h-2 bg-green-400 rounded-full animate-pulse" title="Preview available" />
        )}

        {/* Hover effect border */}
        <div className="absolute inset-0 rounded-xl border border-transparent bg-gradient-to-r from-purple-500/20 to-pink-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
      </div>
    </div>
  );
};

export default TrackCard;