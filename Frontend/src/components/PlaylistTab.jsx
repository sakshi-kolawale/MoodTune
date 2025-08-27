import React, { useState } from 'react';
import { Music, Share, Download, Clock, Play, ExternalLink } from 'lucide-react';
import TrackCard from './TrackCard.jsx';
import { formatDuration, calculatePlaylistDuration, generatePlaylistName } from '../utils/helper.js';
import { authenticateSpotify, createSpotifyPlaylist } from '../services/api.js';

const PlaylistTab = ({ 
  playlist, 
  onRemoveFromPlaylist, 
  selectedMood, 
  selectedGenre, 
  accessToken 
}) => {
  const [isCreatingPlaylist, setIsCreatingPlaylist] = useState(false);

  const totalDuration = calculatePlaylistDuration(playlist);
  const playlistName = generatePlaylistName(selectedMood, selectedGenre);

  const handleAuthenticateSpotify = async () => {
    try {
      await authenticateSpotify();
    } catch (error) {
      console.error('Authentication failed:', error);
    }
  };

  const handleCreatePlaylistOnSpotify = async () => {
    if (!accessToken || playlist.length === 0) {
      alert('Please authenticate and add tracks to your playlist first!');
      return;
    }

    setIsCreatingPlaylist(true);
    try {
      const trackUris = playlist.map(track => track.uri);
      const result = await createSpotifyPlaylist(
        accessToken,
        playlistName,
        `Generated playlist with ${selectedMood} mood`,
        trackUris
      );
      
      if (result.playlist_url) {
        alert('Playlist created successfully on Spotify!');
        window.open(result.playlist_url, '_blank');
      }
    } catch (error) {
      console.error('Failed to create playlist:', error);
      alert('Failed to create playlist. Please try again.');
    } finally {
      setIsCreatingPlaylist(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-white mb-2">
          Your Playlist
        </h2>
        <p className="text-white/70">
          Manage and export your curated music collection
        </p>
      </div>

      {/* Playlist Stats & Actions */}
      <div className="relative group">
        <div className="absolute inset-0 bg-gradient-to-r from-purple-400/20 to-pink-400/20 rounded-2xl blur-xl transition-all duration-300" />
        
        <div className="relative backdrop-blur-lg bg-white/10 border border-white/20 rounded-2xl p-8 shadow-xl">
          <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6">
            {/* Playlist Info */}
            <div className="flex-1">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-16 h-16 rounded-xl bg-gradient-to-r from-purple-400 to-pink-400 flex items-center justify-center shadow-lg">
                  <Music className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-white">
                    {playlistName}
                  </h3>
                  <p className="text-white/70">
                    {playlist.length} tracks • {formatDuration(totalDuration)}
                  </p>
                </div>
              </div>

              {/* Stats */}
              <div className="flex flex-wrap items-center gap-6 text-sm">
                <div className="flex items-center gap-2 text-white/70">
                  <Music className="w-4 h-4" />
                  <span>{playlist.length} songs</span>
                </div>
                <div className="flex items-center gap-2 text-white/70">
                  <Clock className="w-4 h-4" />
                  <span>{formatDuration(totalDuration)}</span>
                </div>
                {playlist.length > 0 && (
                  <div className="flex items-center gap-2 text-white/70">
                    <Play className="w-4 h-4" />
                    <span>
                      {playlist.filter(track => track.preview_url).length} previews available
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-3 w-full lg:w-auto">
              <button
                onClick={handleAuthenticateSpotify}
                className={`
                  px-6 py-3 rounded-xl font-medium text-white
                  bg-gradient-to-r from-green-500 to-emerald-500
                  hover:from-green-600 hover:to-emerald-600
                  transition-all duration-300 transform hover:scale-105
                  shadow-lg hover:shadow-xl hover:shadow-green-500/25
                  flex items-center justify-center gap-2 group/btn
                `}
              >
                <ExternalLink className="w-4 h-4 group-hover/btn:rotate-12 transition-transform duration-300" />
                Connect Spotify
              </button>
              
              <button
                onClick={handleCreatePlaylistOnSpotify}
                disabled={playlist.length === 0 || isCreatingPlaylist}
                className={`
                  px-6 py-3 rounded-xl font-medium text-white
                  bg-gradient-to-r from-purple-500 to-pink-500
                  hover:from-purple-600 hover:to-pink-600
                  disabled:opacity-50 disabled:cursor-not-allowed
                  transition-all duration-300 transform hover:scale-105
                  shadow-lg hover:shadow-xl hover:shadow-purple-500/25
                  flex items-center justify-center gap-2 group/btn
                `}
              >
                {isCreatingPlaylist ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4 group-hover/btn:animate-bounce transition-transform duration-300" />
                    Export to Spotify
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Playlist Content */}
      {playlist.length === 0 ? (
        /* Empty State */
        <div className="text-center py-16">
          <div className="w-32 h-32 mx-auto mb-8 rounded-full bg-gradient-to-r from-purple-400/20 to-pink-400/20 flex items-center justify-center">
            <Music className="w-16 h-16 text-white/30" />
          </div>
          <h3 className="text-2xl font-semibold text-white mb-4">
            Your playlist is empty
          </h3>
          <p className="text-white/70 max-w-md mx-auto mb-8">
            Start building your perfect playlist by searching for music or getting personalized recommendations.
          </p>
          
          {/* Quick action suggestions */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <div className="backdrop-blur-lg bg-white/5 border border-white/10 rounded-xl p-4 text-center">
              <div className="w-10 h-10 mx-auto mb-2 rounded-full bg-purple-400/20 flex items-center justify-center">
                <span className="text-lg">🔍</span>
              </div>
              <p className="text-white/80 text-sm">Search for specific tracks</p>
            </div>
            <div className="backdrop-blur-lg bg-white/5 border border-white/10 rounded-xl p-4 text-center">
              <div className="w-10 h-10 mx-auto mb-2 rounded-full bg-pink-400/20 flex items-center justify-center">
                <span className="text-lg">✨</span>
              </div>
              <p className="text-white/80 text-sm">Get smart recommendations</p>
            </div>
          </div>
        </div>
      ) : (
        /* Playlist Tracks */
        <div className="space-y-6">
          <div className="text-center">
            <h3 className="text-lg font-semibold text-white mb-2">
              Playlist Tracks
            </h3>
            <p className="text-white/70">
              Swipe or click to manage your tracks
            </p>
          </div>

          <div className="grid gap-4 animate-fadeIn">
            {playlist.map((track, index) => (
              <div
                key={track.id}
                className="animate-slideInUp"
                style={{ animationDelay: `${index * 0.05}s` }}
              >
                <div className="relative group">
                  {/* Track number indicator */}
                  <div className="absolute -left-12 top-1/2 transform -translate-y-1/2 w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-white/60 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    {index + 1}
                  </div>
                  
                  <TrackCard
                    track={track}
                    inPlaylist={true}
                    onRemoveFromPlaylist={onRemoveFromPlaylist}
                  />
                </div>
              </div>
            ))}
          </div>

          {/* Playlist Summary */}
          <div className="backdrop-blur-lg bg-white/5 border border-white/10 rounded-xl p-6 text-center">
            <h4 className="text-white font-medium mb-2">Playlist Summary</h4>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
              <div>
                <div className="text-2xl font-bold text-purple-400">{playlist.length}</div>
                <div className="text-white/70">Total Tracks</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-pink-400">
                  {Math.floor(totalDuration / 60000)}m
                </div>
                <div className="text-white/70">Duration</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-blue-400">
                  {new Set(playlist.flatMap(track => track.artists?.map(artist => artist.name) || [])).size}
                </div>
                <div className="text-white/70">Unique Artists</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PlaylistTab;