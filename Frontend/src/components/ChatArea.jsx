import React, { useState, useRef, useEffect } from 'react';
import { Send, Paperclip, Sparkles, Loader2, FileText, Search, BookOpen, UploadCloud, FolderKanban } from 'lucide-react';
import { MessageItem } from './MessageItem';
import { GeminiSparkle } from './GeminiSparkle';

export function ChatArea({
  conversation,
  onSendMessage,
  isLoading,
  onOpenUploadModal,
  activeBucket = 'general',
  buckets = [],
  onOpenBucketManager,
}) {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const currentBucketInfo = buckets.find((b) => b.name === activeBucket);

  // Auto-scroll al final
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversation?.messages, isLoading]);

  // Auto-grow textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  }, [inputValue]);

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    onSendMessage(inputValue.trim());
    setInputValue('');

    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSuggestionClick = (promptText) => {
    if (isLoading) return;
    onSendMessage(promptText);
  };

  const messages = conversation?.messages || [];
  const isFreshConversation = messages.length <= 1;

  return (
    <main className="gemini-chat-main">
      {/* Top Header */}
      <header className="gemini-header">
        <div className="gemini-header-left">
          <div className="gemini-brand-title">
            <span className="gemini-brand-name">{conversation?.title || 'Conversación'}</span>
          </div>

          {/* Selector de Bucket Activo */}
          <button
            className="gemini-active-bucket-pill"
            onClick={onOpenBucketManager}
            title="Haga clic para cambiar o administrar buckets"
            type="button"
          >
            <FolderKanban size={13} />
            <span>Bucket: <strong>{activeBucket}</strong></span>
            {currentBucketInfo?.content_type && (
              <span className="pill-type">{currentBucketInfo.content_type}</span>
            )}
          </button>
        </div>

        <div className="gemini-header-right">
          <button
            className="gemini-upload-chip-btn"
            onClick={onOpenUploadModal}
            type="button"
          >
            <Paperclip size={15} />
            <span>Cargar PDF</span>
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <div className="gemini-scroll-view">
        <div className="gemini-content-container">
          {isFreshConversation ? (
            /* Gemini Welcome Screen */
            <div className="gemini-welcome-hero">
              <div className="gemini-greeting">
                <h1 className="gemini-gradient-text">Hola,</h1>
                <h2 className="gemini-greeting-sub">¿En qué puedo ayudarte hoy con tus documentos?</h2>
                <div className="gemini-welcome-bucket-info">
                  <FolderKanban size={15} />
                  <span>
                    Consultando bucket <strong>{activeBucket}</strong> (tipo:{' '}
                    <em>{currentBucketInfo?.content_type || 'general'}</em>)
                  </span>
                </div>
              </div>

              <div className="gemini-cards-grid">
                <div
                  className="gemini-prompt-card"
                  onClick={() => handleSuggestionClick(`Haz un resumen estructurado con los puntos clave del bucket ${activeBucket}`)}
                >
                  <p className="card-text">Resumir la información disponible en el bucket <strong>{activeBucket}</strong></p>
                  <div className="card-icon-circle">
                    <BookOpen size={18} />
                  </div>
                </div>

                <div
                  className="gemini-prompt-card"
                  onClick={() => handleSuggestionClick(`¿Qué temas o documentos específicos se encuentran en el bucket ${activeBucket}?`)}
                >
                  <p className="card-text">Explorar documentos y temas indexados en este bucket</p>
                  <div className="card-icon-circle">
                    <Search size={18} />
                  </div>
                </div>

                <div
                  className="gemini-prompt-card"
                  onClick={() => handleSuggestionClick('Explica de manera concisa y clara el tema principal del archivo')}
                >
                  <p className="card-text">Explicar la idea central de forma concisa y amigable</p>
                  <div className="card-icon-circle">
                    <FileText size={18} />
                  </div>
                </div>

                <div
                  className="gemini-prompt-card action-card"
                  onClick={onOpenUploadModal}
                >
                  <p className="card-text">Cargar un nuevo PDF en el bucket <strong>{activeBucket}</strong></p>
                  <div className="card-icon-circle accent">
                    <UploadCloud size={18} />
                  </div>
                </div>
              </div>
            </div>
          ) : (
            /* Messages List */
            <div className="gemini-messages-list">
              {messages.map((msg) => (
                <MessageItem key={msg.id} message={msg} />
              ))}
            </div>
          )}

          {/* Thinking / Streaming Indicator */}
          {isLoading && (
            <div className="gemini-message-row assistant-row gemini-thinking-row">
              <div className="gemini-avatar-wrapper spin-pulse">
                <GeminiSparkle size={26} />
              </div>
              <div className="gemini-thinking-container">
                <div className="gemini-shimmer-line line-1"></div>
                <div className="gemini-shimmer-line line-2"></div>
                <div className="gemini-shimmer-line line-3"></div>
                <span className="gemini-thinking-label">
                  Buscando en bucket <strong>{activeBucket}</strong> y generando respuesta...
                </span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Floating Bottom Input Capsule */}
      <div className="gemini-input-anchor">
        <div className="gemini-input-container">
          <form className="gemini-input-capsule" onSubmit={handleSubmit}>
            <button
              type="button"
              className="gemini-attach-btn"
              onClick={onOpenUploadModal}
              title={`Adjuntar PDF al bucket ${activeBucket}`}
            >
              <Paperclip size={19} />
            </button>

            <textarea
              ref={textareaRef}
              className="gemini-textarea"
              placeholder={`Pregunta algo sobre el bucket '${activeBucket}'...`}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
              disabled={isLoading}
            />

            <button
              type="submit"
              className={`gemini-send-btn ${inputValue.trim() && !isLoading ? 'active' : ''}`}
              disabled={!inputValue.trim() || isLoading}
              title="Enviar consulta"
            >
              {isLoading ? (
                <Loader2 size={18} className="spinner" />
              ) : (
                <Send size={18} />
              )}
            </button>
          </form>

          <p className="gemini-disclaimer">
            MARIA RAG consulta el bucket <strong>{activeBucket}</strong>. Verifica la información importante con los documentos originales.
          </p>
        </div>
      </div>
    </main>
  );
}
