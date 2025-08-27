import React, { useState, useEffect } from 'react';
import { Shuffle, Heart, Zap, Coffee, PartyPopper, Sun } from 'lucide-react';
import TrackCard from './TrackCard.jsx';
import LoadingSpinner from './LoadingSpinner.jsx';
import { getRecommendations, fetchGenres } from '../services/api.js';
import { MOODS } from '../constants/index.js';
import { getMoodConfig } from '../utils/helper.js';

const RecommendationsTab = ({ onAddToPlaylist }) => {
  const [recommendations, setRecommendations] = useState([]);
  const [availableGenres, setAvailableGenres] = useState([]);
  const [selectedMood, setSelectedMood] = useState('happy');
  const [selectedGenre, setSelectedGenre] = useState('');
  const [loading, setLoading] = useState(false);
  const [hasGenerated, setHasGenerated] = useState(false);

  // Mood icons mapping
  const moodIcons = {
    happy: Sun,
    sad: Coffee,
    energetic: Zap,
    chill: Coffee,
    party: PartyPopper
  };

  useEffect(() => {
    loadGenres();
  }, []);

  const loadGenres = async () => {
    try {
      const genres = await fetchGenres();
      setAvailableGenres(genres);
    } catch (error) {
      console.error('Failed to load genres:', error);
    }
  };

  const handleGetRecommendations = async () => {
    setLoading(true);
    try {
      const results = await getRecommendations(selectedMood, selectedGenre);
      setRecommendations(results);
      setHasGenerated(true);
    } catch (error) {
      console.error('Failed to get recommendations:', error);
      setRecommendations([]);
    } finally {
      setLoading(false);
    }
  };

  const currentMoodConfig = getMoodConfig(selectedMood, MOODS);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-white mb-2">
          Smart Recommendations
        </h2>
        <p className="text-white/70">
          Get personalized music recommendations based on your mood and preferences
        </p>
      </div>

      {/* Configuration Panel */}
      <div className="relative group">
        <div className="absolute inset-0 bg-gradient-to-r from-purple-400/20 to-pink-400/20 rounded-2xl blur-xl transition-all duration-300" />
        
        <div className="relative backdrop-blur-lg bg-white/10 border border-white/20 rounded-2xl p-8 shadow-xl">
          <h3 className="text-xl font-semibold text-white mb-6 text-center">
            Customize Your Experience
          </h3>
          
          <div className="grid lg:grid-cols-2 gap-8">
            {/* Mood Selection */}
            <div>
              <label className="block text-white font-medium mb-4">
                Choose your mood:
              </label>
              <div className="grid grid-cols-2 gap-3">
                {MOODS.map((mood) => {
                  const IconComponent = moodIcons[mood.value];
                  return (
                    <button
                      key={mood.value}
                      onClick={() => setSelectedMood(mood.value)}
                      className={`
                        p-4 rounded-xl border-2 transition-all duration-300 
                        flex items-center gap-3 text-sm font-medium group/mood
                        transform hover:scale-105
                        ${selectedMood === mood.value
                          ? `bg-gradient-to-r ${mood.color} text-white border-white/30 shadow-lg`
                          : 'bg-white/5 text-white/80 border-white/20 hover:border-white/40 hover:bg-white/10'
                        }
                      `}
                    >
                      <IconComponent className="w-5 h-5 group-hover/mood:animate-bounce" />
                      <span>{mood.label}</span>
                      
                      {/* Selection indicator */}
                      {selectedMood === mood.value && (
                        <div className="ml-auto w-2 h-2 bg-white rounded-full animate-pulse" />
                      )}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Genre Selection */}
            <div>
              <label className="block text-white font-medium mb-4">
                Genre (optional):
              </label>
              <div className="relative">
                <select
                  value={selectedGenre}
                  onChange={(e) => setSelectedGenre(e.target.value)}
                  className={`
                    w-full px-4 py-4 bg-white/5 border border-white/20 rounded-xl
                    text-white backdrop-blur-sm appearance-none cursor-pointer
                    focus:ring-2 focus:ring-purple-400/50 focus:border-purple-400/50 
                    focus:bg-white/10 transition-all duration-300
                  `}
                >
                  <option value="" className="bg-gray-800">Any Genre</option>
                  {availableGenres.slice(0, 20).map((genre) => (
                    <option key={genre} value={genre} className="bg-gray-800">
                      {genre.charAt(0).toUpperCase() + genre.slice(1)}
                    </option>
                  ))}
                </select>
                
                {/* Custom dropdown arrow */}
                <div className="absolute inset-y-0 right-0 flex items-center pr-4 pointer-events-none">
                  <svg className="w-5 h-5 text-white/40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </div>
              
              {/* Selected genre indicator */}
              {selectedGenre && (
                <div className="mt-3 inline-flex items-center px-3 py-1 rounded-full bg-white/10 text-white/80 text-sm">
                  <span>Selected: {selectedGenre.charAt(0).toUpperCase() + selectedGenre.slice(1)}</span>
                  <button
                    onClick={() => setSelectedGenre('')}
                    className="ml-2 text-white/60 hover:text-white transition-colors"
                  >
                    ×
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Generate Button */}
          <div className="mt-8 text-center">
            <button
              onClick={handleGetRecommendations}
              disabled={loading}
              className={`
                px-8 py-4 rounded-xl font-medium text-white
                bg-gradient-to-r from-purple-500 to-pink-500
                hover:from-purple-600 hover:to-pink-600
                disabled:opacity-50 disabled:cursor-not-allowed
                transition-all duration-300 transform hover:scale-105
                shadow-lg hover:shadow-xl hover:shadow-purple-500/25
                flex items-center gap-3 mx-auto group/btn
              `}
            >
              <Shuffle className="w-5 h-5 group-hover/btn:rotate-180 transition-transform duration-500" />
              Generate Recommendations
              
              {/* Loading dots */}
              {loading && (
                <div className="flex space-x-1 ml-2">
                  <div className="w-1.5 h-1.5 bg-white rounded-full animate-bounce" />
                  <div className="w-1.5 h-1.5 bg-white rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                  <div className="w-1.5 h-1.5 bg-white rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
                </div>
              )}
            </button>
          </div>

          {/* Current selection summary */}
          <div className="mt-6 text-center">
            <p className="text-white/60 text-sm">
              Generating {currentMoodConfig?.label.toLowerCase()} music
              {selectedGenre && ` in ${selectedGenre} genre`}
            </p>
          </div>
        </div>
      </div>

      {/* Results Section */}
      {loading ? (
        <LoadingSpinner message="Finding perfect tracks for you..." />
      ) : (
        <div className="space-y-6">
          {/* Results Header */}
          {hasGenerated && recommendations.length > 0 && (
            <div className="text-center">
              <h3 className="text-xl font-semibold text-white mb-2">
                Your {currentMoodConfig?.label} Recommendations
              </h3>
              <p className="text-white/70">
                {recommendations.length} tracks curated just for you
              </p>
            </div>
          )}

          {/* Recommendations Grid */}
          {recommendations.length > 0 && (
            <div className="grid gap-4 animate-fadeIn">
              {recommendations.map((track, index) => (
                <div
                  key={track.id}
                  className="animate-slideInUp"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <TrackCard
                    track={track}
                    onAddToPlaylist={onAddToPlaylist}
                  />
                </div>
              ))}
            </div>
          )}

          {/* Empty State */}
          {hasGenerated && recommendations.length === 0 && !loading && (
            <div className="text-center py-16">
              <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-white/5 flex items-center justify-center">
                <Shuffle className="w-12 h-12 text-white/30" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">
                No recommendations found
              </h3>
              <p className="text-white/70 max-w-md mx-auto">
                Try selecting a different mood or genre combination to get personalized recommendations.
              </p>
            </div>
          )}

          {/* Initial State */}
          {!hasGenerated && !loading && (
            <div className="text-center py-16">
              <div className={`w-24 h-24 mx-auto mb-6 rounded-full bg-gradient-to-r ${currentMoodConfig?.color}/20 flex items-center justify-center`}>
                <Heart className="w-12 h-12 text-white/50 animate-pulse" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">
                Ready to Discover?
              </h3>
              <p className="text-white/70 max-w-md mx-auto">
                Select your mood and preferred genre, then click "Generate Recommendations" to get started.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default RecommendationsTab;