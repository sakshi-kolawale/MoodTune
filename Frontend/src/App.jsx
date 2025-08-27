import React, { useState, useEffect } from 'react';
import { Music, Search, Heart, Shuffle } from 'lucide-react';
import SearchTab from './components/SearchTab.jsx';
import RecommendationsTab from './components/RecommendationsTab.jsx';
import PlaylistTab from './components/PlaylistTab.jsx';
import { getSimilarTracks } from './services/api.js';
import { isTrackInPlaylist } from './utils/helper.js';
import { MiniPlayer } from './components/MiniPlayer.jsx';

const MusicRecommendationApp = () => {
  const [playlist, setPlaylist] = useState([]);
  const [accessToken, setAccessToken] = useState(null);
  const [selectedMood, setSelectedMood] = useState('happy');
  const [selectedGenre, setSelectedGenre] = useState('');
  const [activeTab, setActiveTab] = useState('search');

  // Tab configuration with icons
  const tabs = [
    { id: 'search', label: 'Search', icon: Search },
    { id: 'recommendations', label: 'Recommendations', icon: Shuffle },
    { id: 'playlist', label: 'My Playlist', icon: Heart }
  ];

  const addToPlaylist = (track) => {
    if (!isTrackInPlaylist(track, playlist)) {
      setPlaylist(prev => [...prev, track]);
      
      // Show success feedback
      const notification = document.createElement('div');
      notification.className = 'fixed top-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-50 animate-slideInRight';
      notification.textContent = `Added "${track.name}" to playlist`;
      document.body.appendChild(notification);
      
      setTimeout(() => {
        notification.remove();
      }, 3000);
    }
  };

  const removeFromPlaylist = (trackId) => {
    setPlaylist(prev => prev.filter(track => track.id !== trackId));
  };

  const handleGetSimilar = async (trackId) => {
    try {
      const similarTracks = await getSimilarTracks(trackId);
      if (similarTracks.length > 0) {
        setActiveTab('recommendations');
      }
    } catch (error) {
      console.error('Failed to get similar tracks:', error);
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Animated Background */}
      <div className="fixed inset-0 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        {/* Animated background elements */}
        <div className="absolute inset-0">
          {/* Floating particles */}
          {[...Array(20)].map((_, i) => (
            <div
              key={i}
              className="absolute w-2 h-2 bg-white/10 rounded-full animate-float"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 10}s`,
                animationDuration: `${10 + Math.random() * 20}s`
              }}
            />
          ))}
          
          {/* Gradient orbs */}
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse" />
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-pink-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }} />
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '4s' }} />
        </div>
        
        {/* Grid overlay */}
        {/* <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%23ffffff" fill-opacity="0.03"%3E%3Ccircle cx="30" cy="30" r="1"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-50" /> */}

        <div 
  className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg%20width%3D%2260%22%20height%3D%2260%22%20viewBox%3D%220%200%2060%2060%22%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%3E%3Cg%20fill%3D%22none%22%20fill-rule%3D%22evenodd%22%3E%3Cg%20fill%3D%22%23ffffff%22%20fill-opacity%3D%220.03%22%3E%3Ccircle%20cx%3D%2230%22%20cy%3D%2230%22%20r%3D%221%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-50"
/>

      </div>

      {/* Main Content */}
      <div className="relative z-10">
        <div className="container mx-auto px-4 py-8 max-w-6xl">
          {/* Header */}
          <header className="text-center mb-12">
            <div className="relative inline-block">
              {/* Glow effect behind title */}
              <div className="absolute inset-0 bg-gradient-to-r from-purple-400/30 to-pink-400/30 blur-2xl rounded-full" />
              
              <h1 className="relative text-5xl md:text-6xl font-bold text-white mb-4 flex items-center justify-center gap-4">
                <div className="relative">
                  <Music className="w-12 h-12 md:w-16 md:h-16 text-purple-400 animate-pulse" />
                  {/* Musical note particles */}
                  <div className="absolute -top-2 -right-2 w-3 h-3 bg-pink-400 rounded-full animate-bounce" />
                  <div className="absolute -bottom-1 -left-1 w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.5s' }} />
                </div>
                <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 bg-clip-text text-transparent">
                  Music Discovery
                </span>
              </h1>
            </div>
            
            <p className="text-white/80 text-lg md:text-xl max-w-2xl mx-auto leading-relaxed">
              Discover new music, get personalized recommendations, and create the perfect playlist
            </p>
            
            {/* Stats */}
            <div className="flex justify-center items-center gap-8 mt-8">
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-400">{playlist.length}</div>
                <div className="text-white/60 text-sm">Tracks Added</div>
              </div>
              <div className="w-px h-8 bg-white/20" />
              <div className="text-center">
                <div className="text-2xl font-bold text-pink-400">∞</div>
                <div className="text-white/60 text-sm">Possibilities</div>
              </div>
            </div>
          </header>

          {/* Tab Navigation */}
          <div className="flex justify-center mb-12">
            <div className="relative">
              {/* Background glow */}
              <div className="absolute inset-0 bg-white/10 rounded-2xl backdrop-blur-lg border border-white/20 shadow-2xl" />
              
              <div className="relative flex p-2">
                {tabs.map((tab, index) => {
                  const IconComponent = tab.icon;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`
                        relative px-6 py-3 rounded-xl font-medium transition-all duration-300
                        flex items-center gap-3 group
                        ${activeTab === tab.id
                          ? 'text-white shadow-lg'
                          : 'text-white/70 hover:text-white hover:bg-white/5'
                        }
                      `}
                    >
                      {/* Active tab background */}
                      {activeTab === tab.id && (
                        <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl shadow-lg animate-fadeIn" />
                      )}
                      
                      {/* Content */}
                      <div className="relative flex items-center gap-2">
                        <IconComponent className={`w-5 h-5 transition-transform duration-300 ${
                          activeTab === tab.id ? 'scale-110' : 'group-hover:scale-105'
                        }`} />
                        <span className="hidden sm:block">{tab.label}</span>
                        
                        {/* Playlist count badge */}
                        {tab.id === 'playlist' && playlist.length > 0 && (
                          <div className="absolute -top-2 -right-2 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center text-xs font-bold text-white animate-pulse">
                            {playlist.length > 9 ? '9+' : playlist.length}
                          </div>
                        )}
                      </div>
                      
                      {/* Hover effect */}
                      <div className={`
                        absolute inset-0 bg-white/5 rounded-xl opacity-0 
                        group-hover:opacity-100 transition-opacity duration-300
                        ${activeTab === tab.id ? 'hidden' : ''}
                      `} />
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Tab Content */}
          <div className="relative">
            {/* Tab content wrapper with fade animation */}
            <div key={activeTab} className="animate-fadeIn">
              {activeTab === 'search' && (
                <SearchTab 
                  onAddToPlaylist={addToPlaylist}
                  onGetSimilar={handleGetSimilar}
                />
              )}
              
              {activeTab === 'recommendations' && (
                <RecommendationsTab 
                  onAddToPlaylist={addToPlaylist}
                  selectedMood={selectedMood}
                  selectedGenre={selectedGenre}
                  onMoodChange={setSelectedMood}
                  onGenreChange={setSelectedGenre}
                />
              )}
              
              {activeTab === 'playlist' && (
                <PlaylistTab 
                  playlist={playlist}
                  onRemoveFromPlaylist={removeFromPlaylist}
                  selectedMood={selectedMood}
                  selectedGenre={selectedGenre}
                  accessToken={accessToken}
                />
              )}
              <MiniPlayer />
            </div>
          </div>
        </div>
      </div>

      {/* Global Styles for Animations */}
      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-20px) rotate(180deg); }
        }
        
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes slideInUp {
          from { opacity: 0; transform: translateY(30px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes slideInRight {
          from { opacity: 0; transform: translateX(100px); }
          to { opacity: 1; transform: translateX(0); }
        }
        
        @keyframes gradient-x {
          0%, 100% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
        }
        
        .animate-float {
          animation: float 15s ease-in-out infinite;
        }
        
        .animate-fadeIn {
          animation: fadeIn 0.6s ease-out;
        }
        
        .animate-slideInUp {
          animation: slideInUp 0.6s ease-out both;
        }
        
        .animate-slideInRight {
          animation: slideInRight 0.5s ease-out;
        }
        
        .animate-gradient-x {
          background-size: 200% 200%;
          animation: gradient-x 3s ease infinite;
        }
        
        .animate-reverse {
          animation-direction: reverse;
        }
        
        /* Glassmorphism backdrop filter support */
        .backdrop-blur-lg {
          backdrop-filter: blur(16px);
          -webkit-backdrop-filter: blur(16px);
        }
        
        .backdrop-blur-sm {
          backdrop-filter: blur(4px);
          -webkit-backdrop-filter: blur(4px);
        }
        
        /* Smooth scroll behavior */
        html {
          scroll-behavior: smooth;
        }
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
          width: 8px;
        }
        
        ::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb {
          background: linear-gradient(to bottom, #8b5cf6, #ec4899);
          border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
          background: linear-gradient(to bottom, #7c3aed, #db2777);
        }
      `}</style>
    </div>
  );
};

export default MusicRecommendationApp;