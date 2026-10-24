import React from 'react';
import { Plus, MessageSquare, Trash2, FileUp, FolderKanban, Settings2, Check } from 'lucide-react';

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
}) {
  return (
    <aside className="gemini-sidebar">
      {/* Header con título MARIA */}
      <div className="gemini-sidebar-top">
        <div className="gemini-logo-row">
          <span className="gemini-logo-text">MARIA</span>
        </div>
      </div>

      {/* Botón "+ Nuevo chat" estilo píldora */}
      <div className="gemini-sidebar-actions">
        <button
          className="gemini-new-chat-pill"
          onClick={onCreateConversation}
          type="button"
        >
          <Plus size={18} />
          <span>Nuevo chat</span>
        </button>
      </div>

      {/* Sección de Buckets de Conocimiento */}
      <div className="gemini-sidebar-section buckets-section">
        <div className="gemini-section-header-row">
          <span className="gemini-section-header">Buckets</span>
          <button
            className="gemini-section-action-btn"
            onClick={onOpenBucketManager}
            title="Administrar buckets"
            type="button"
          >
            <Settings2 size={14} />
          </button>
        </div>

        <div className="gemini-buckets-mini-list">
          {buckets.map((b) => {
            const isActive = b.name === activeBucket;
            return (
              <div
                key={b.name}
                className={`gemini-bucket-mini-item ${isActive ? 'active' : ''}`}
                onClick={() => onSelectBucket && onSelectBucket(b.name)}
                title={`Bucket: ${b.name} (${b.content_type || 'general'})`}
              >
                <FolderKanban size={15} className="bucket-mini-icon" />
                <span className="bucket-mini-name">{b.name}</span>
                <span className="bucket-mini-type">{b.content_type || 'gen'}</span>
                {isActive && <Check size={13} className="bucket-mini-check" />}
              </div>
            );
          })}
        </div>

        <button
          type="button"
          className="btn-manage-buckets-sidebar"
          onClick={onOpenBucketManager}
        >
          <Plus size={13} />
          <span>Administrar o crear buckets</span>
        </button>
      </div>

      {/* Sección de Recientes */}
      <div className="gemini-sidebar-section history-section">
        <span className="gemini-section-header">Recientes</span>
        <div className="gemini-history-list">
          {conversations.length === 0 ? (
            <p className="gemini-empty-history">Sin conversaciones recientes</p>
          ) : (
            conversations.map((conv) => {
              const isActive = conv.id === activeId;
              return (
                <div
                  key={conv.id}
                  className={`gemini-history-item ${isActive ? 'active' : ''}`}
                  onClick={() => onSelectConversation(conv.id)}
                >
                  <MessageSquare size={16} className="history-icon" />
                  <span className="history-title" title={conv.title}>
                    {conv.title}
                  </span>
                  <button
                    type="button"
                    className="history-delete-btn"
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

      {/* Footer con subida de PDF y estado de Milvus */}
      <div className="gemini-sidebar-footer">
        <button
          className="gemini-footer-btn"
          onClick={onOpenUploadModal}
          type="button"
        >
          <FileUp size={16} />
          <span>Cargar documento PDF</span>
        </button>

        <div className="gemini-status-tag">
          <span className="gemini-status-dot"></span>
          <span>Milvus & Ollama RAG</span>
        </div>
      </div>
    </aside>
  );
}
