import React, { useState, useEffect, useCallback } from 'react';
import { Sidebar } from './components/Sidebar';
import { ChatArea } from './components/ChatArea';
import { UploadModal } from './components/UploadModal';
import { BucketManagerModal } from './components/BucketManagerModal';
import { useChatStorage } from './hooks/useChatStorage';
import { api } from './services/api';

const ACTIVE_BUCKET_KEY = 'maria_active_bucket_v1';

export function App() {
  const {
    conversations,
    activeConversation,
    activeId,
    createConversation,
    selectConversation,
    deleteConversation,
    addMessage,
    updateMessage,
  } = useChatStorage();

  const [isLoading, setIsLoading] = useState(false);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [isBucketManagerOpen, setIsBucketManagerOpen] = useState(false);

  // Estado de Buckets
  const [buckets, setBuckets] = useState([
    {
      name: 'general',
      content_type: 'general',
      description: 'Bucket general por defecto',
      total_chunks: 0,
    },
  ]);

  const [activeBucket, setActiveBucket] = useState(() => {
    try {
      return localStorage.getItem(ACTIVE_BUCKET_KEY) || 'general';
    } catch {
      return 'general';
    }
  });

  // Cargar lista de buckets desde el backend
  const loadBuckets = useCallback(async () => {
    try {
      const data = await api.listBuckets();
      if (data && Array.isArray(data.buckets) && data.buckets.length > 0) {
        setBuckets(data.buckets);
      }
    } catch (err) {
      console.warn('No se pudo cargar la lista de buckets:', err);
    }
  }, []);

  useEffect(() => {
    loadBuckets();
  }, [loadBuckets]);

  // Persistir activeBucket
  const handleSelectBucket = (bucketName) => {
    setActiveBucket(bucketName);
    try {
      localStorage.setItem(ACTIVE_BUCKET_KEY, bucketName);
    } catch (e) {
      console.error(e);
    }
  };

  const handleSendMessage = async (queryText) => {
    if (!queryText || isLoading) return;

    const currentConvId = activeId;
    const bucketToUse = activeBucket || 'general';

    // 1. Agregar mensaje del usuario
    addMessage(currentConvId, {
      role: 'user',
      text: queryText,
    });

    setIsLoading(true);

    let assistantMsgId = null;

    try {
      // 2. Invocar backend FastAPI con streaming en vivo
      let accumulatedText = '';
      const result = await api.sendMessage(queryText, bucketToUse, (token, currentFull) => {
        accumulatedText = currentFull;
        if (!assistantMsgId) {
          setIsLoading(false); // Ocultar shimmer cuando empieza a escribir
          const newMsg = addMessage(currentConvId, {
            role: 'assistant',
            text: currentFull,
            isStreaming: true,
          });
          assistantMsgId = newMsg.id;
        } else {
          updateMessage(currentConvId, assistantMsgId, {
            text: currentFull,
            isStreaming: true,
          });
        }
      });

      // 3. Finalizar respuesta del asistente
      if (assistantMsgId) {
        updateMessage(currentConvId, assistantMsgId, {
          text: accumulatedText || result?.response || 'No se obtuvo respuesta del modelo.',
          isStreaming: false,
        });
      } else {
        addMessage(currentConvId, {
          role: 'assistant',
          text: result?.response || 'No se obtuvo respuesta del modelo.',
          iteration: result?.iteration,
        });
      }
    } catch (err) {
      console.error('Error al generar respuesta:', err);
      if (assistantMsgId) {
        updateMessage(currentConvId, assistantMsgId, {
          text: `⚠️ **Error al consultar el asistente**: ${err.message || 'Error de conexión con el backend'}. Verifica que los servicios de FastAPI, Milvus y Ollama estén corriendo.`,
          isStreaming: false,
        });
      } else {
        addMessage(currentConvId, {
          role: 'assistant',
          text: `⚠️ **Error al consultar el asistente**: ${err.message || 'Error de conexión con el backend'}. Verifica que los servicios de FastAPI, Milvus y Ollama estén corriendo.`,
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleUploadSuccess = (fileName, chunksCount, bucketName, contentType) => {
    addMessage(activeId, {
      role: 'assistant',
      text: `📄 **Documento indexado:** Se ha procesado el archivo \`${fileName}\` en el bucket **${bucketName}** (${contentType || 'general'}), registrando ${chunksCount} fragmentos. Ya puedes consultarlo.`,
    });
    // Actualizar estadísticas de chunks
    loadBuckets();
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
        buckets={buckets}
        activeBucket={activeBucket}
        onSelectBucket={handleSelectBucket}
        onOpenBucketManager={() => setIsBucketManagerOpen(true)}
      />

      <ChatArea
        conversation={activeConversation}
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
        onOpenUploadModal={() => setIsUploadModalOpen(true)}
        activeBucket={activeBucket}
        buckets={buckets}
        onOpenBucketManager={() => setIsBucketManagerOpen(true)}
      />

      <UploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onUploadSuccess={handleUploadSuccess}
        buckets={buckets}
        activeBucket={activeBucket}
        onOpenBucketManager={() => setIsBucketManagerOpen(true)}
      />

      <BucketManagerModal
        isOpen={isBucketManagerOpen}
        onClose={() => setIsBucketManagerOpen(false)}
        buckets={buckets}
        activeBucket={activeBucket}
        onSelectActiveBucket={handleSelectBucket}
        onBucketsChanged={loadBuckets}
      />
    </div>
  );
}

export default App;
