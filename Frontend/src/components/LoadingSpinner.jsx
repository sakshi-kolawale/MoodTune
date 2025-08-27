import React from 'react';
import { Music } from 'lucide-react';

const LoadingSpinner = ({ message = "Loading..." }) => {
  return (
    <div className="flex flex-col items-center justify-center py-16">
      {/* Animated music note */}
      <div className="relative mb-6">
        {/* Outer ring */}
        <div className="w-20 h-20 rounded-full border-4 border-purple-200/30 border-t-purple-400 animate-spin" />
        
        {/* Inner ring */}
        <div className="absolute inset-2 w-16 h-16 rounded-full border-4 border-pink-200/30 border-t-pink-400 animate-spin animate-reverse" />
        
        {/* Music icon */}
        <div className="absolute inset-0 flex items-center justify-center">
          <Music className="w-8 h-8 text-purple-400 animate-pulse" />
        </div>
        
        {/* Floating dots */}
        <div className="absolute -top-2 -right-2 w-3 h-3 bg-purple-400 rounded-full animate-bounce" />
        <div className="absolute -bottom-2 -left-2 w-2 h-2 bg-pink-400 rounded-full animate-bounce" style={{ animationDelay: '0.5s' }} />
        <div className="absolute top-1/2 -left-4 w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '1s' }} />
      </div>
      
      {/* Loading text with typing animation */}
      <div className="text-center">
        <p className="text-white/80 font-medium text-lg mb-2">
          {message}
        </p>
        
        {/* Animated dots */}
        <div className="flex justify-center space-x-1">
          <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" />
          <div className="w-2 h-2 bg-pink-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
          <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
        </div>
      </div>
      
      {/* Background particles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(6)].map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-white/20 rounded-full animate-float"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 3}s`,
              animationDuration: `${3 + Math.random() * 2}s`
            }}
          />
        ))}
      </div>
    </div>
  );
};

export default LoadingSpinner;