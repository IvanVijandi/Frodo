import React, { useState, useRef, useEffect } from 'react';
import { Send, Paperclip, Sparkles, Loader2, FileText, Search, BookOpen, UploadCloud } from 'lucide-react';
import { MessageItem } from './MessageItem';
import { GeminiSparkle } from './GeminiSparkle';

export function ChatArea({
  conversation,
  onSendMessage,
  isLoading,
  onOpenUploadModal,
}) {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

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
            <span className="gemini-version-pill">RAG Activo</span>
          </div>
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
                <h2 className="gemini-greeting-sub">¿En qué puedo ayudarte hoy con tus PDFs?</h2>
              </div>

              <div className="gemini-cards-grid">
                <div
                  className="gemini-prompt-card"
                  onClick={() => handleSuggestionClick('Haz un resumen estructurado con los puntos clave del documento cargado')}
                >
                  <p className="card-text">Resumir el documento principal con sus puntos más relevantes</p>
                  <div className="card-icon-circle">
                    <BookOpen size={18} />
                  </div>
                </div>

                <div
                  className="gemini-prompt-card"
                  onClick={() => handleSuggestionClick('¿Qué documentos o prestaciones se encuentran indexados en la base de datos?')}
                >
                  <p className="card-text">Explorar qué información o documentos están indexados</p>
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
                  <p className="card-text">Cargar un nuevo archivo PDF para consultar</p>
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
                  Consultando base vectorial y generando respuesta...
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
              title="Adjuntar documento PDF"
            >
              <Paperclip size={19} />
            </button>

            <textarea
              ref={textareaRef}
              className="gemini-textarea"
              placeholder="Haz una pregunta sobre tus documentos PDF..."
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
            MARIA puede cometer errores. Verifica la información importante con los documentos originales.
          </p>
        </div>
      </div>
    </main>
  );
}
