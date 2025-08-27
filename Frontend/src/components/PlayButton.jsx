import React, { useState, useEffect } from 'react';
import { Play, Pause, Volume2, VolumeX } from 'lucide-react';
import { audioPreviewManager } from '../services/api.js';

const PlayButton = ({ 
  track, 
  size = 'md', 
  variant = 'default',
  showLabel = false,
  className = '',
  onPlayStateChange = null 
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [hasError, setHasError] = useState(false);

  // Check if this track is currently playing
  useEffect(() => {
    const checkPlayingState = () => {
      const currentlyPlaying = audioPreviewManager.isCurrentlyPlaying(track.id);
      setIsPlaying(currentlyPlaying);
    };

    checkPlayingState();
    
    // Set up interval to check playing state
    const interval = setInterval(checkPlayingState, 100);
    
    return () => clearInterval(interval);
  }, [track.id]);

  // Size configurations
  const sizeConfig = {
    sm: {
      button: 'w-8 h-8',
      icon: 'w-3 h-3',
      text: 'text-xs'
    },
    md: {
      button: 'w-10 h-10',
      icon: 'w-4 h-4',
      text: 'text-sm'
    },
    lg: {
      button: 'w-12 h-12',
      icon: 'w-5 h-5',
      text: 'text-base'
    }
  };

  // Variant configurations
  const variantConfig = {
    default: {
      base: 'bg-white/10 hover:bg-white/20 text-white border border-white/20',
      active: 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg',
      loading: 'bg-white/5 text-white/50'
    },
    primary: {
      base: 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white shadow-lg',
      active: 'bg-gradient-to-r from-green-500 to-emerald-500 text-white shadow-lg',
      loading: 'bg-gray-400 text-white/70'
    },
    minimal: {
      base: 'bg-transparent hover:bg-white/10 text-white/80 hover:text-white',
      active: 'bg-white/20 text-white',
      loading: 'bg-transparent text-white/40'
    }
  };

  const handlePlayClick = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (isLoading) return;
    
    setIsLoading(true);
    setHasError(false);

    try {
      const result = await audioPreviewManager.playPreview(track);
      
      if (result.success) {
        const newPlayingState = result.action === 'playing_preview';
        setIsPlaying(newPlayingState);
        
        // Notify parent component of play state change
        if (onPlayStateChange) {
          onPlayStateChange(newPlayingState, result.action);
        }

        // Show feedback based on action
        if (result.action === 'opened_spotify') {
          showNotification('No preview available - opened in Spotify', 'info');
        } else if (result.action === 'playing_preview') {
          showNotification('Playing preview', 'success');
        } else if (result.action === 'paused') {
          showNotification('Paused', 'info');
        }
      }
    } catch (error) {
      console.error('Playback failed:', error);
      setHasError(true);
      showNotification('Playback failed', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const showNotification = (message, type = 'info') => {
    const notification = document.createElement('div');
    const colors = {
      success: 'bg-green-500',
      error: 'bg-red-500',
      info: 'bg-blue-500'
    };
    
    notification.className = `fixed top-4 right-4 ${colors[type]} text-white px-4 py-2 rounded-lg shadow-lg z-50 animate-slideInRight`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
      if (notification.parentNode) {
        notification.remove();
      }
    }, 2000);
  };

  const config = sizeConfig[size];
  const variantStyles = variantConfig[variant];  // ✅ FIXED name

  let buttonClass, iconToShow;
  
  if (isLoading) {
    buttonClass = variantStyles.loading;
    iconToShow = <div className={`${config.icon} border-2 border-current border-t-transparent rounded-full animate-spin`} />;
  } else if (hasError) {
    buttonClass = 'bg-red-500/20 text-red-400 border border-red-400/30';
    iconToShow = <VolumeX className={config.icon} />;
  } else if (isPlaying) {
    buttonClass = variantStyles.active;
    iconToShow = <Pause className={config.icon} />;
  } else {
    buttonClass = variantStyles.base;
    iconToShow = <Play className={`${config.icon} ml-0.5`} />;
  }

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <button
        onClick={handlePlayClick}
        disabled={isLoading}
        className={`
          ${config.button} ${buttonClass}
          rounded-full backdrop-blur-sm
          transition-all duration-300 transform
          hover:scale-110 active:scale-95
          disabled:cursor-not-allowed disabled:transform-none
          group relative overflow-hidden
        `}
        title={isPlaying ? 'Pause' : hasError ? 'Playback failed' : 'Play preview'}
      >
        {/* Ripple effect */}
        <div className="absolute inset-0 bg-white/20 rounded-full scale-0 group-hover:scale-100 transition-transform duration-300 opacity-0 group-hover:opacity-100" />
        
        {/* Icon */}
        <div className="relative flex items-center justify-center">
          {iconToShow}
        </div>
        
        {/* Playing indicator */}
        {isPlaying && (
          <div className="absolute inset-0 rounded-full border-2 border-white/50 animate-pulse" />
        )}
      </button>

      {/* Optional label */}
      {showLabel && (
        <span className={`${config.text} text-white/80 font-medium`}>
          {isLoading ? 'Loading...' : isPlaying ? 'Playing' : hasError ? 'Error' : 'Play'}
        </span>
      )}
    </div>
  );
};

export default PlayButton;
