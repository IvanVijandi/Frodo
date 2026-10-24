import React, { useState } from 'react';
import { marked } from 'marked';
import { Copy, Check } from 'lucide-react';
import { MariaVectorLogo } from './MariaVectorLogo';

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
        <div className="maria-markdown-body">
          <div dangerouslySetInnerHTML={{ __html: htmlContent }} />
          {message.isStreaming && <span className="maria-cursor">▍</span>}
        </div>
      );
    }
    return <div className="maria-user-text">{message.text}</div>;
  };

  if (!isAssistant) {
    return (
      <div className="maria-message-row user-row">
        <div className="maria-user-bubble">
          {renderContent()}
        </div>
      </div>
    );
  }

  return (
    <div className="maria-message-row assistant-row">
      <div className="maria-avatar-bubble">
        <MariaVectorLogo size={20} />
      </div>

      <div className="maria-assistant-container">
        <div className="maria-assistant-content">
          {renderContent()}
        </div>

        <div className="maria-message-footer">
          <button
            onClick={handleCopy}
            className="maria-copy-btn"
            title="Copiar respuesta"
            type="button"
          >
            {copied ? (
              <>
                <Check size={13} className="text-emerald" />
                <span>Copiado</span>
              </>
            ) : (
              <>
                <Copy size={13} />
                <span>Copiar</span>
              </>
            )}
          </button>
          {message.timestamp && (
            <span className="maria-timestamp">{message.timestamp}</span>
          )}
        </div>
      </div>
    </div>
  );
}
