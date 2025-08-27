``// Format duration from milliseconds to MM:SS
export const formatDuration = (ms) => {
  const minutes = Math.floor(ms / 60000);
  const seconds = ((ms % 60000) / 1000).toFixed(0);
  return `${minutes}:${seconds.padStart(2, '0')}`;
};

// Calculate total playlist duration
export const calculatePlaylistDuration = (playlist) => {
  return playlist.reduce((acc, track) => acc + track.duration_ms, 0);
};

// Check if track is in playlist
export const isTrackInPlaylist = (track, playlist) => {
  return playlist.find(t => t.id === track.id);
};

// Generate playlist name based on mood and genre
export const generatePlaylistName = (mood, genre) => {
  const moodCapitalized = mood.charAt(0).toUpperCase() + mood.slice(1);
  const genreCapitalized = genre ? ` ${genre.charAt(0).toUpperCase() + genre.slice(1)}` : '';
  return `My ${moodCapitalized}${genreCapitalized} Playlist`;
};

// Debounce function for search input
export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

// Get mood configuration by value
export const getMoodConfig = (moodValue, moods) => {
  return moods.find(mood => mood.value === moodValue);
};