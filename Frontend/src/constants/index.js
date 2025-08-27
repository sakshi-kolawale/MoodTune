// API Configuration
export const BACKEND_URL = 'http://localhost:5000';

// Mood options with icons and colors
export const MOODS = [
  { 
    value: 'happy', 
    label: 'Happy', 
    color: 'from-yellow-400 to-orange-500',
    textColor: 'text-yellow-600',
    bgColor: 'bg-gradient-to-r from-yellow-400/20 to-orange-500/20'
  },
  { 
    value: 'sad', 
    label: 'Sad', 
    color: 'from-blue-400 to-indigo-500',
    textColor: 'text-blue-600',
    bgColor: 'bg-gradient-to-r from-blue-400/20 to-indigo-500/20'
  },
  { 
    value: 'energetic', 
    label: 'Energetic', 
    color: 'from-red-400 to-pink-500',
    textColor: 'text-red-600',
    bgColor: 'bg-gradient-to-r from-red-400/20 to-pink-500/20'
  },
  { 
    value: 'chill', 
    label: 'Chill', 
    color: 'from-green-400 to-emerald-500',
    textColor: 'text-green-600',
    bgColor: 'bg-gradient-to-r from-green-400/20 to-emerald-500/20'
  },
  { 
    value: 'party', 
    label: 'Party', 
    color: 'from-purple-400 to-pink-500',
    textColor: 'text-purple-600',
    bgColor: 'bg-gradient-to-r from-purple-400/20 to-pink-500/20'
  }
];

// Animation variants
export const ANIMATION_VARIANTS = {
  fadeIn: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 }
  },
  slideIn: {
    initial: { opacity: 0, x: -20 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: 20 }
  },
  scaleIn: {
    initial: { opacity: 0, scale: 0.9 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.9 }
  }
};