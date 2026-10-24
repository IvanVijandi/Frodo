import React from 'react';

/**
 * Logotipo Vectorial de MARIA inspirado en el diseño de Voyage AI
 * Representa espacios vectoriales multidimensionales y búsqueda semántica de alta precisión.
 */
export function MariaVectorLogo({ size = 24, className = '' }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <defs>
        <linearGradient id="maria_vector_grad" x1="2" y1="2" x2="22" y2="22" gradientUnits="userSpaceOnUse">
          <stop stopColor="#059669" />
          <stop offset="0.6" stopColor="#10B981" />
          <stop offset="1" stopColor="#14B8A6" />
        </linearGradient>
        <linearGradient id="maria_inner_grad" x1="7" y1="7" x2="17" y2="17" gradientUnits="userSpaceOnUse">
          <stop stopColor="#10B981" stopOpacity="0.9" />
          <stop offset="1" stopColor="#047857" stopOpacity="0.95" />
        </linearGradient>
      </defs>

      {/* Poliedro vectorial exterior */}
      <path
        d="M12 2L20.66 7V17L12 22L3.34 17V7L12 2Z"
        stroke="url(#maria_vector_grad)"
        strokeWidth="1.75"
        strokeLinejoin="round"
      />

      {/* Conexiones de hipercubo/vector semántico interior */}
      <path
        d="M12 2V12M20.66 17L12 12M3.34 17L12 12"
        stroke="url(#maria_vector_grad)"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeOpacity="0.75"
      />

      {/* Núcleo central de embeddings */}
      <circle cx="12" cy="12" r="2.5" fill="url(#maria_inner_grad)" />
    </svg>
  );
}

