import React, { useState } from 'react';
import { marked } from 'marked';
import { User, Copy, Check, Sparkles } from 'lucide-react';
import { GeminiSparkle } from './GeminiSparkle';

marked.setOptions({
  breaks: true,
  gfm: true,
});

export function MessageItem({ message }) {
  const isAssistant = message.role === 'assistant';
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const renderContent = () => {
    if (isAssistant) {
      const htmlContent = marked.parse(message.text || '');
      return (
        <div
          className="gemini-markdown-body"
          dangerouslySetInnerHTML={{ __html: htmlContent }}
        />
      );
    }
    return <div className="gemini-user-text">{message.text}</div>;
  };

  if (!isAssistant) {
    return (
      <div className="gemini-message-row user-row">
        <div className="gemini-user-bubble">
          {renderContent()}
        </div>
      </div>
    );
  }

  return (
    <div className="gemini-message-row assistant-row">
      <div className="gemini-avatar-wrapper">
        <GeminiSparkle size={26} />
      </div>

      <div className="gemini-response-container">
        <div className="gemini-response-content">
          {renderContent()}
        </div>

        <div className="gemini-response-actions">
          <button
            onClick={handleCopy}
            className="gemini-action-btn"
            title="Copiar respuesta"
            type="button"
          >
            {copied ? (
              <>
                <Check size={14} className="text-success" />
                <span>Copiado</span>
              </>
            ) : (
              <>
                <Copy size={14} />
                <span>Copiar</span>
              </>
            )}
          </button>

          <span className="gemini-rag-badge">
            <Sparkles size={11} />
            <span>Fundamentado con RAG</span>
          </span>

          {message.iteration !== undefined && message.iteration > 0 && (
            <span className="gemini-iteration-badge">
              {message.iteration} {message.iteration === 1 ? 'iteración' : 'iteraciones'}
            </span>
          )}

          <span className="gemini-time-badge">{message.timestamp}</span>
        </div>
      </div>
    </div>
  );
}
