import React, { useState, useCallback } from 'react';
import { Search } from 'lucide-react';
import TrackCard from './TrackCard.jsx';
import LoadingSpinner from './LoadingSpinner.jsx';
import { searchTracks } from '../services/api.js';
import { debounce } from '../utils/helper.js';

const SearchTab = ({ onAddToPlaylist, onGetSimilar }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const performSearch = useCallback(
    debounce(async (query) => {
      if (!query.trim()) {
        setSearchResults([]);
        setHasSearched(false);
        return;
      }

      setLoading(true);
      try {
        const results = await searchTracks(query);
        setSearchResults(results);
        setHasSearched(true);
      } catch (error) {
        console.error('Search failed:', error);
        setSearchResults([]);
      } finally {
        setLoading(false);
      }
    }, 300),
    []
  );

  const handleSearchChange = (e) => {
    const query = e.target.value;
    setSearchQuery(query);
    performSearch(query);
  };

  const handleSearchSubmit = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setLoading(true);
    try {
      const results = await searchTracks(searchQuery);
      setSearchResults(results);
      setHasSearched(true);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Search Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-white mb-2">
          Discover Music
        </h2>
        <p className="text-white/70">
          Search for your favorite songs, artists, or albums
        </p>
      </div>

      {/* Search Bar */}
      <div className="relative group">
        <div className="absolute inset-0 bg-gradient-to-r from-purple-400/20 to-pink-400/20 rounded-2xl blur-xl group-hover:blur-2xl transition-all duration-300" />
        
        <form 
          onSubmit={handleSearchSubmit}
          className="relative backdrop-blur-lg bg-white/10 border border-white/20 rounded-2xl p-6 shadow-xl"
        >
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <input
                type="text"
                placeholder="Search for songs, artists, or albums..."
                value={searchQuery}
                onChange={handleSearchChange}
                className={`
                  w-full px-6 py-4 bg-white/5 border border-white/10 rounded-xl
                  text-white placeholder-white/50 backdrop-blur-sm
                  focus:ring-2 focus:ring-purple-400/50 focus:border-purple-400/50 
                  focus:bg-white/10 transition-all duration-300
                  text-lg
                `}
              />
              
              {/* Search icon overlay */}
              <div className="absolute inset-y-0 right-0 flex items-center pr-4 pointer-events-none">
                <Search className="w-5 h-5 text-white/40" />
              </div>
            </div>
            
            <button
              type="submit"
              disabled={loading || !searchQuery.trim()}
              className={`
                px-8 py-4 rounded-xl font-medium text-white
                bg-gradient-to-r from-purple-500 to-pink-500
                hover:from-purple-600 hover:to-pink-600
                disabled:opacity-50 disabled:cursor-not-allowed
                transition-all duration-300 transform hover:scale-105
                shadow-lg hover:shadow-xl hover:shadow-purple-500/25
                flex items-center gap-2 group/btn
              `}
            >
              <Search className="w-5 h-5 group-hover/btn:rotate-12 transition-transform duration-300" />
              Search
            </button>
          </div>
          
          {/* Real-time search indicator */}
          {loading && (
            <div className="absolute top-full left-0 right-0 mt-2">
              <div className="bg-white/10 backdrop-blur-sm rounded-lg px-4 py-2 text-center">
                <span className="text-white/70 text-sm">Searching...</span>
              </div>
            </div>
          )}
        </form>
      </div>

      {/* Search Results */}
      {loading ? (
        <LoadingSpinner message="Searching for tracks..." />
      ) : (
        <div className="space-y-6">
          {/* Results Header */}
          {hasSearched && (
            <div className="text-center">
              <p className="text-white/70">
                {searchResults.length > 0 
                  ? `Found ${searchResults.length} results for "${searchQuery}"`
                  : `No results found for "${searchQuery}"`
                }
              </p>
            </div>
          )}

          {/* Results Grid */}
          {searchResults.length > 0 && (
            <div className="grid gap-4 animate-fadeIn">
              {searchResults.map((track, index) => (
                <div
                  key={track.id}
                  className="animate-slideInUp"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <TrackCard
                    track={track}
                    showSimilar={true}
                    onAddToPlaylist={onAddToPlaylist}
                    onGetSimilar={onGetSimilar}
                  />
                </div>
              ))}
            </div>
          )}

          {/* Empty State */}
          {hasSearched && searchResults.length === 0 && !loading && (
            <div className="text-center py-16">
              <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-white/5 flex items-center justify-center">
                <Search className="w-12 h-12 text-white/30" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">
                No tracks found
              </h3>
              <p className="text-white/70 max-w-md mx-auto">
                Try adjusting your search terms or check your spelling. 
                You can search for song titles, artist names, or album names.
              </p>
            </div>
          )}

          {/* Initial State */}
          {!hasSearched && !loading && (
            <div className="text-center py-16">
              <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-gradient-to-r from-purple-400/20 to-pink-400/20 flex items-center justify-center">
                <Search className="w-12 h-12 text-white/50" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">
                Start Your Music Discovery
              </h3>
              <p className="text-white/70 max-w-md mx-auto">
                Enter a song name, artist, or album in the search bar above to discover amazing music.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SearchTab;