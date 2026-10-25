import React, { useState } from 'react';
import {
  Plus,
  MessageSquare,
  Trash2,
  FileUp,
  FolderKanban,
  Settings2,
  Check,
  ChevronDown,
  ChevronUp,
  Database,
  ArrowLeft
} from 'lucide-react';
import { MariaVectorLogo } from './MariaVectorLogo';

export function Sidebar({
  conversations,
  activeId,
  onSelectConversation,
  onCreateConversation,
  onDeleteConversation,
  onOpenUploadModal,
  buckets = [],
  activeBucket = 'general',
  onSelectBucket,
  onOpenBucketManager,
  onBackToHub,
}) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <aside className="maria-sidebar">
      {/* Header: Solo MARIA sin leyendas + botón para volver a los buckets */}
      <div className="maria-sidebar-header">
        <div
          className="maria-brand"
          onClick={onBackToHub}
          style={{ cursor: onBackToHub ? 'pointer' : 'default' }}
          title={onBackToHub ? "Volver a la selección de buckets" : undefined}
        >
          <MariaVectorLogo size={22} />
          <span className="maria-brand-title">MARIA</span>
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

      {/* Sección Limpia de Buckets con Botón de Despliegue */}
      <div className="maria-buckets-panel">
        <div className="maria-buckets-header">
          <div className="maria-buckets-title">
            <Database size={15} className="text-emerald" />
            <span>Buckets</span>
          </div>

          <div className="maria-buckets-controls">
            <button
              type="button"
              className="maria-btn-toggle"
              onClick={() => setIsExpanded(!isExpanded)}
              title={isExpanded ? "Plegar sección" : "Desplegar buckets"}
            >
              <span>{isExpanded ? "Plegar" : "Ver info"}</span>
              {isExpanded ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
            </button>

            <button
              type="button"
              className="maria-icon-btn-ghost"
              onClick={onOpenBucketManager}
              title="Administrar buckets"
            >
              <Settings2 size={14} />
            </button>
          </div>
        </div>

        {/* Bucket Activo (siempre visible, limpio) */}
        <div
          className="maria-active-bucket-row"
          onClick={() => setIsExpanded(!isExpanded)}
          title="Bucket activo actualmente"
        >
          <span className="maria-status-dot-emerald"></span>
          <span className="maria-active-bucket-name">{activeBucket}</span>
          <span className="maria-active-tag">Activo</span>
        </div>

        {/* Lista Desplegable Simple y Limpia */}
        {isExpanded && (
          <div className="maria-buckets-dropdown">
            <div className="maria-buckets-list">
              {buckets.map((b) => {
                const isActive = b.name === activeBucket;
                return (
                  <div
                    key={b.name}
                    className={`maria-bucket-item ${isActive ? 'is-active' : ''}`}
                    onClick={() => onSelectBucket && onSelectBucket(b.name)}
                    title={`Seleccionar bucket ${b.name}`}
                  >
                    <FolderKanban size={14} className={isActive ? 'text-emerald' : 'text-muted'} />
                    <span className="maria-bucket-name">{b.name}</span>
                    {isActive && <Check size={13} className="text-emerald maria-bucket-check" />}
                  </div>
                );
              })}
            </div>

            <button
              type="button"
              className="maria-manage-buckets-link"
              onClick={onOpenBucketManager}
            >
              <Settings2 size={13} />
              <span>Administrar buckets</span>
            </button>
          </div>
        )}
      </div>

      {/* Historial de Chats Recientes */}
      <div className="maria-history-section">
        <span className="maria-history-heading">Recientes</span>
        <div className="maria-history-list">
          {conversations.length === 0 ? (
            <p className="maria-empty-text">Sin conversaciones recientes</p>
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

      {/* Footer Limpio */}
      <div className="maria-sidebar-footer">
        <button
          className="maria-upload-btn"
          onClick={onOpenUploadModal}
          type="button"
        >
          <FileUp size={15} className="text-emerald" />
          <span>Cargar PDF</span>
        </button>
      </div>
    </aside>
  );
}
