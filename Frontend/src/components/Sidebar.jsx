import React from 'react';
import { Plus, MessageSquare, Trash2, FileUp } from 'lucide-react';

export function Sidebar({
  conversations,
  activeId,
  onSelectConversation,
  onCreateConversation,
  onDeleteConversation,
  onOpenUploadModal,
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

      {/* Sección de Recientes */}
      <div className="gemini-sidebar-section">
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
