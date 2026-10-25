import React, { useState, useEffect, useCallback } from 'react';
import { Sidebar } from './components/Sidebar';
import { ChatArea } from './components/ChatArea';
import { BucketHubView } from './components/BucketHubView';
import { BucketDetailsView } from './components/BucketDetailsView';
import { UploadModal } from './components/UploadModal';
import { BucketManagerModal } from './components/BucketManagerModal';
import { useChatStorage } from './hooks/useChatStorage';
import { api } from './services/api';

const ACTIVE_BUCKET_KEY = 'maria_active_bucket_v1';

export function App() {
  const [activeBucket, setActiveBucket] = useState(() => {
    try {
      return localStorage.getItem(ACTIVE_BUCKET_KEY) || 'general';
    } catch {
      return 'general';
    }
  });

  const {
    conversations,
    activeConversation,
    activeId,
    createConversation,
    selectConversation,
    deleteConversation,
    updateConversationId,
    addMessage,
    updateMessage,
  } = useChatStorage(activeBucket);

  const [isLoading, setIsLoading] = useState(false);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [isBucketManagerOpen, setIsBucketManagerOpen] = useState(false);

  // Vista actual: 'hub' (selector inicial de bucket) | 'chat' | 'manage'
  const [currentView, setCurrentView] = useState('hub');
  const [uploadTargetBucket, setUploadTargetBucket] = useState('general');
  const [managedBucket, setManagedBucket] = useState(null);

  // Estado de Buckets
  const [buckets, setBuckets] = useState([
    {
      name: 'general',
      content_type: 'general',
      description: 'Bucket general por defecto',
      total_chunks: 0,
    },
  ]);

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
    setUploadTargetBucket(bucketName);
    try {
      localStorage.setItem(ACTIVE_BUCKET_KEY, bucketName);
    } catch (e) {
      console.error(e);
    }
  };

  // Transición desde Hub al Chat
  const handleSelectBucketAndOpenChat = (bucketName) => {
    handleSelectBucket(bucketName);
    setCurrentView('chat');
  };

  // Volver desde Chat al Hub
  const handleBackToHub = () => {
    setCurrentView('hub');
  };

  // Abrir vista particular de administración del bucket
  const handleManageBucket = (bucketName) => {
    setManagedBucket(bucketName);
    setUploadTargetBucket(bucketName);
    setCurrentView('manage');
  };

  // Abrir modal de upload para un bucket específico desde el Hub
  const handleOpenUploadForBucket = (bucketName) => {
    setUploadTargetBucket(bucketName);
    setIsUploadModalOpen(true);
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
      // 2. Invocar backend FastAPI con streaming en vivo persistiendo en PostgreSQL
      let accumulatedText = '';
      const result = await api.sendMessage(
        queryText,
        bucketToUse,
        (token, currentFull) => {
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
        },
        currentConvId
      );

      // Si el backend retornó un UUID de PostgreSQL, sincronizarlo en el estado local
      if (result?.conversacion_id && result.conversacion_id !== currentConvId) {
        updateConversationId(currentConvId, result.conversacion_id);
      }

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
      {currentView === 'hub' ? (
        /* Vista 1: Selector / Hub de Buckets */
        <BucketHubView
          buckets={buckets}
          activeBucket={activeBucket}
          onSelectBucketAndChat={handleSelectBucketAndOpenChat}
          onOpenUploadForBucket={handleOpenUploadForBucket}
          onOpenBucketManager={() => setIsBucketManagerOpen(true)}
          onManageBucket={handleManageBucket}
        />
      ) : currentView === 'manage' ? (
        /* Vista 2: Vista particular de administración de bucket y documentos */
        <BucketDetailsView
          bucketName={managedBucket || activeBucket}
          bucketInfo={buckets.find((b) => b.name === (managedBucket || activeBucket))}
          onBackToHub={handleBackToHub}
          onOpenChat={(bName) => handleSelectBucketAndOpenChat(bName)}
          onOpenUpload={(bName) => handleOpenUploadForBucket(bName)}
          onBucketDeleted={() => loadBuckets()}
        />
      ) : (
        /* Vista 3: Chat con Sidebar y ChatArea */
        <>
          <Sidebar
            conversations={conversations}
            activeId={activeId}
            onSelectConversation={selectConversation}
            onCreateConversation={createConversation}
            onDeleteConversation={deleteConversation}
            activeBucket={activeBucket}
            onBackToHub={handleBackToHub}
          />

          <ChatArea
            conversation={activeConversation}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
            onOpenUploadModal={() => {
              setUploadTargetBucket(activeBucket);
              setIsUploadModalOpen(true);
            }}
            activeBucket={activeBucket}
            buckets={buckets}
            onOpenBucketManager={() => setIsBucketManagerOpen(true)}
            onBackToHub={handleBackToHub}
          />
        </>
      )}

      {/* Modales Compartidos */}
      <UploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onUploadSuccess={handleUploadSuccess}
        buckets={buckets}
        activeBucket={uploadTargetBucket || activeBucket}
        onOpenBucketManager={() => setIsBucketManagerOpen(true)}
      />

      <BucketManagerModal
        isOpen={isBucketManagerOpen}
        onClose={() => setIsBucketManagerOpen(false)}
        buckets={buckets}
        activeBucket={activeBucket}
        onSelectActiveBucket={(b) => {
          handleSelectBucket(b);
          setUploadTargetBucket(b);
        }}
        onBucketsChanged={loadBuckets}
      />
    </div>
  );
}

export default App;
