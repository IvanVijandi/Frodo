import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Paperclip,
  Database,
  Search,
  BookOpen,
  FileText,
  ChevronDown,
  ArrowLeft
} from 'lucide-react';
import { MessageItem } from './MessageItem';
import { MariaVectorLogo } from './MariaVectorLogo';

export function ChatArea({
  conversation,
  onSendMessage,
  isLoading,
  onOpenUploadModal,
  activeBucket = 'general',
  buckets = [],
  onOpenBucketManager,
  onBackToHub,
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
    <main className="maria-main">
      {/* Header Limpio con botón para volver a los buckets */}
      <header className="maria-header">
        <div className="maria-header-left">
          {onBackToHub && (
            <button
              className="maria-header-back-btn"
              onClick={onBackToHub}
              title="Volver a la selección de buckets"
              type="button"
            >
              <ArrowLeft size={15} />
              <span>Mis buckets</span>
            </button>
          )}

          <div
            className="maria-header-brand"
            onClick={onBackToHub}
            style={{ cursor: onBackToHub ? 'pointer' : 'default' }}
            title={onBackToHub ? "Ir a la vista de buckets" : undefined}
          >
            <MariaVectorLogo size={20} />
            <span className="maria-header-title">MARIA</span>
          </div>

          {/* Selector de Bucket Activo Simple */}
          <button
            className="maria-header-bucket-badge"
            onClick={onOpenBucketManager}
            title="Administrar o cambiar bucket"
            type="button"
          >
            <Database size={13} className="text-emerald" />
            <span>Bucket: <strong>{activeBucket}</strong></span>
            <ChevronDown size={12} className="text-muted" />
          </button>
        </div>

        <div className="maria-header-right">
          <button
            className="maria-header-upload-btn"
            onClick={onOpenUploadModal}
            type="button"
          >
            <Paperclip size={14} className="text-emerald" />
            <span>Cargar PDF</span>
          </button>
        </div>
      </header>

      {/* Área de Mensajes / Contenido */}
      <div className="maria-scroll-container">
        <div className="maria-chat-container">
          {isFreshConversation ? (
            /* Pantalla de Bienvenida Minimalista en Blanco y Verde */
            <div className="maria-hero">
              <div className="maria-hero-icon-wrap">
                <MariaVectorLogo size={48} />
              </div>

              <h1 className="maria-hero-name">MARIA</h1>
              <p className="maria-hero-subtitle">¿En qué puedo ayudarte hoy?</p>

              <div
                className="maria-hero-bucket-chip"
                onClick={onOpenBucketManager}
                title="Haga clic para gestionar este bucket"
              >
                <span className="maria-hero-dot-emerald"></span>
                <span>Bucket activo: <strong>{activeBucket}</strong></span>
              </div>

              {/* Sugerencias de consulta limpias */}
              <div className="maria-hero-suggestions">
                <button
                  type="button"
                  className="maria-suggestion-card"
                  onClick={() => handleSuggestionClick(`Haz un resumen estructurado del contenido en el bucket ${activeBucket}`)}
                >
                  <BookOpen size={16} className="text-emerald maria-sugg-icon" />
                  <span>Resumir los puntos clave de este bucket</span>
                </button>

                <button
                  type="button"
                  className="maria-suggestion-card"
                  onClick={() => handleSuggestionClick(`¿Qué temas principales contiene el bucket ${activeBucket}?`)}
                >
                  <Search size={16} className="text-emerald maria-sugg-icon" />
                  <span>Consultar temas y documentos indexados</span>
                </button>

                <button
                  type="button"
                  className="maria-suggestion-card"
                  onClick={() => handleSuggestionClick('Explica de manera concisa y clara el tema principal')}
                >
                  <FileText size={16} className="text-emerald maria-sugg-icon" />
                  <span>Explicar el concepto principal con claridad</span>
                </button>
              </div>
            </div>
          ) : (
            /* Lista de Mensajes */
            <div className="maria-messages-flow">
              {messages.map((msg) => (
                <MessageItem key={msg.id} message={msg} />
              ))}
            </div>
          )}

          {/* Indicador de Generación / Streaming */}
          {isLoading && (
            <div className="maria-message-row assistant-row maria-loading-row">
              <div className="maria-avatar-bubble pulse-animation">
                <MariaVectorLogo size={18} />
              </div>
              <div className="maria-loading-indicator">
                <span className="maria-loading-dot"></span>
                <span className="maria-loading-dot"></span>
                <span className="maria-loading-dot"></span>
                <span className="maria-loading-text">
                  Buscando en <strong>{activeBucket}</strong> y generando...
                </span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Flotante Minimalista */}
      <div className="maria-input-wrapper">
        <div className="maria-input-inner">
          <form className="maria-input-box" onSubmit={handleSubmit}>
            <button
              type="button"
              className="maria-attach-icon-btn"
              onClick={onOpenUploadModal}
              title={`Adjuntar PDF al bucket '${activeBucket}'`}
            >
              <Paperclip size={17} />
            </button>

            <textarea
              ref={textareaRef}
              rows={1}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={`Pregunta a MARIA sobre el bucket '${activeBucket}'...`}
              className="maria-textarea"
              disabled={isLoading}
            />

            <button
              type="submit"
              className={`maria-submit-btn ${inputValue.trim() && !isLoading ? 'is-ready' : ''}`}
              disabled={!inputValue.trim() || isLoading}
              title="Enviar consulta (Enter)"
            >
              <Send size={15} />
            </button>
          </form>

          <div className="maria-disclaimer">
            <span>MARIA busca contexto en Milvus y responde localmente con Ollama</span>
          </div>
        </div>
      </div>
    </main>
  );
}
