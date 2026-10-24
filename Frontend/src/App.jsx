import React, { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { ChatArea } from './components/ChatArea';
import { UploadModal } from './components/UploadModal';
import { useChatStorage } from './hooks/useChatStorage';
import { api } from './services/api';

export function App() {
  const {
    conversations,
    activeConversation,
    activeId,
    createConversation,
    selectConversation,
    deleteConversation,
    addMessage,
  } = useChatStorage();

  const [isLoading, setIsLoading] = useState(false);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);

  const handleSendMessage = async (queryText) => {
    if (!queryText || isLoading) return;

    const currentConvId = activeId;

    // 1. Agregar mensaje del usuario
    addMessage(currentConvId, {
      role: 'user',
      text: queryText,
    });

    setIsLoading(true);

    try {
      // 2. Invocar backend FastAPI
      const result = await api.sendMessage(queryText);

      // 3. Agregar respuesta de MARIA
      addMessage(currentConvId, {
        role: 'assistant',
        text: result.response || 'No se obtuvo respuesta del modelo.',
        iteration: result.iteration,
      });
    } catch (err) {
      console.error('Error al generar respuesta:', err);
      addMessage(currentConvId, {
        role: 'assistant',
        text: `⚠️ **Error al consultar el asistente**: ${err.message || 'Error de conexión con el backend'}. Verifica que los servicios de FastAPI, Milvus y Ollama estén corriendo.`,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleUploadSuccess = (fileName, chunksCount) => {
    addMessage(activeId, {
      role: 'assistant',
      text: `📄 **Documento procesado:** Se ha indexado el archivo \`${fileName}\` en la base de datos vectorial (${chunksCount} fragmentos procesados). Ya puedes realizar consultas específicas sobre su contenido.`,
    });
  };

  return (
    <div className="app-layout">
      <Sidebar
        conversations={conversations}
        activeId={activeId}
        onSelectConversation={selectConversation}
        onCreateConversation={createConversation}
        onDeleteConversation={deleteConversation}
        onOpenUploadModal={() => setIsUploadModalOpen(true)}
      />

      <ChatArea
        conversation={activeConversation}
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
        onOpenUploadModal={() => setIsUploadModalOpen(true)}
      />

      <UploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onUploadSuccess={handleUploadSuccess}
      />
    </div>
  );
}

export default App;
