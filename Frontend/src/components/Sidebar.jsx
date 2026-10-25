import React from 'react';
import {
  Plus,
  MessageSquare,
  Trash2,
  Database,
  ArrowLeft
} from 'lucide-react';
import { MariaVectorLogo } from './MariaVectorLogo';

export function Sidebar({
  conversations = [],
  activeId,
  onSelectConversation,
  onCreateConversation,
  onDeleteConversation,
  activeBucket = 'general',
  onBackToHub,
}) {
  return (
    <aside className="maria-sidebar">
      {/* Header: Logo Frodo + botón para volver a los buckets */}
      <div className="maria-sidebar-header">
        <div
          className="maria-brand"
          onClick={onBackToHub}
          style={{ cursor: onBackToHub ? 'pointer' : 'default' }}
          title={onBackToHub ? "Volver a la selección de buckets" : undefined}
        >
          <MariaVectorLogo size={42} />
          <span className="maria-brand-title">Frodo</span>
        </div>

        {onBackToHub && (
          <button
            type="button"
            className="maria-sidebar-back-hub-pill"
            onClick={onBackToHub}
            title="Ver todos los espacios"
          >
            <ArrowLeft size={12} />
            <span>Espacios</span>
          </button>
        )}
      </div>

      {/* Indicador sutil del bucket activo actual */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '6px 10px',
          margin: '0 4px 10px 4px',
          background: 'rgba(255, 255, 255, 0.03)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '8px',
          fontSize: '0.82rem',
          color: 'var(--text-sub)',
        }}
        title={`Espacio actual: ${activeBucket}`}
      >
        <Database size={13} className="text-emerald" />
        <span style={{ color: 'var(--text-muted)' }}>Espacio:</span>
        <strong style={{ color: 'var(--text-main)', fontWeight: 600 }}>{activeBucket}</strong>
      </div>

      {/* Botón "+ Nuevo chat" */}
      <div className="maria-sidebar-action">
        <button
          className="maria-new-chat-btn"
          onClick={onCreateConversation}
          type="button"
        >
          <Plus size={16} className="text-emerald" />
          <span>Nuevo chat</span>
        </button>
      </div>

      {/* Historial de Chats Recientes en este bucket */}
      <div className="maria-history-section" style={{ flex: 1 }}>
        <span className="maria-history-heading">Recientes</span>
        <div className="maria-history-list">
          {conversations.length === 0 ? (
            <p className="maria-empty-text">Sin conversaciones recientes en este espacio</p>
          ) : (
            conversations.map((conv) => {
              const isActive = conv.id === activeId;
              return (
                <div
                  key={conv.id}
                  className={`maria-history-item ${isActive ? 'active' : ''}`}
                  onClick={() => onSelectConversation(conv.id)}
                >
                  <MessageSquare size={14} className="maria-history-icon" />
                  <span className="maria-history-title" title={conv.title}>
                    {conv.title}
                  </span>
                  <button
                    type="button"
                    className="maria-history-del"
                    title="Eliminar chat"
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteConversation(conv.id);
                    }}
                  >
                    <Trash2 size={13} />
                  </button>
                </div>
              );
            })
          )}
        </div>
      </div>
    </aside>
  );
}
