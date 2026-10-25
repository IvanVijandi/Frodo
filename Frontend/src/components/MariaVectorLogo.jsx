import React from 'react';
import frodoImg from '../assets/frodo.jpeg';

/**
 * Logotipo oficial de Frodo (imagen del usuario)
 * Sin bordes verdes, ni sombras de color, con dimensiones visibles y nítidas.
 */
export function FrodoLogo({ size = 46, className = '', style = {} }) {
  return (
    <img
      src={frodoImg}
      alt="Frodo Logo"
      width={size}
      height={size}
      className={`frodo-avatar-logo ${className}`}
      style={{
        width: `${size}px`,
        height: `${size}px`,
        borderRadius: '50%',
        objectFit: 'cover',
        display: 'inline-block',
        verticalAlign: 'middle',
        border: 'none',
        outline: 'none',
        boxShadow: 'none',
        flexShrink: 0,
        ...style,
      }}
    />
  );
}

// Exportación para mantener compatibilidad en todas las vistas
export const MariaVectorLogo = FrodoLogo;
export default FrodoLogo;
