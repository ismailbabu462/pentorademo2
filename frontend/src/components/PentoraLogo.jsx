import React from 'react';

const PentoraLogo = ({ className = "w-5 h-5" }) => {
  return (
    <svg 
      className={className} 
      viewBox="0 0 100 120" 
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Outer Shield - Blue gradient */}
      <path 
        d="M50 10L15 25v35c0 25 18 45 35 50 17-5 35-25 35-50V25L50 10z" 
        fill="url(#blueGradient)" 
      />
      
      {/* Inner Shield - Darker blue */}
      <path 
        d="M50 20L25 32v28c0 18 12 32 25 37 13-5 25-19 25-37V32L50 20z" 
        fill="url(#darkBlueGradient)" 
      />
      
      {/* Center Diamond */}
      <path 
        d="M50 45L40 55h20L50 45z" 
        fill="url(#centerGradient)" 
      />
      
      {/* Upper Chevron */}
      <path 
        d="M50 35L35 50h30L50 35z" 
        fill="url(#lightBlueGradient)" 
      />
      
      {/* Lower Chevron */}
      <path 
        d="M50 55L40 65h20L50 55z" 
        fill="url(#darkBlueGradient)" 
      />

      {/* Gradients */}
      <defs>
        <linearGradient id="blueGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#00BFFF" />
          <stop offset="100%" stopColor="#1E90FF" />
        </linearGradient>
        
        <linearGradient id="darkBlueGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#0066CC" />
          <stop offset="100%" stopColor="#003399" />
        </linearGradient>
        
        <linearGradient id="lightBlueGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#87CEEB" />
          <stop offset="100%" stopColor="#00BFFF" />
        </linearGradient>
        
        <linearGradient id="centerGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#FFFFFF" />
          <stop offset="100%" stopColor="#E6F3FF" />
        </linearGradient>
      </defs>
    </svg>
  );
};

export default PentoraLogo;
