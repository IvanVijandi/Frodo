import { useState, useEffect } from 'react';

const STORAGE_KEY = 'maria_rag_conversations_v1';
const ACTIVE_CONV_PREFIX = 'maria_rag_active_conv_';

function createNewConversationObject(bucket = 'general') {
  const now = new Date();
  const bucketLabel = bucket === 'general' ? 'general' : bucket;
  return {
    id: `conv_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`,
    bucket: bucket,
    title: 'Nueva conversación',
    createdAt: now.toISOString(),
    messages: [
      {
        id: `msg_welcome_${Date.now()}`,
        role: 'assistant',
        text: `¡Hola! Soy **MARIA**, tu asistente RAG. Estás en el espacio **${bucketLabel}**. Puedo responder preguntas consultando los documentos indexados en este bucket.`,
        timestamp: now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ],
  };
}

export function useChatStorage(activeBucket = 'general') {
  // 1. Todas las conversaciones persistidas
  const [allConversations, setAllConversations] = useState(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed) && parsed.length > 0) {
          // Migración automática: asegurar que toda conversación previa tenga asignado su bucket
          return parsed.map((c) => ({
            ...c,
            bucket: c.bucket || 'general',
          }));
        }
      }
    } catch (e) {
      console.warn('Error reading conversations from localStorage:', e);
    }
    const initial = createNewConversationObject(activeBucket || 'general');
    return [initial];
  });

  // 2. ID activo para el bucket actual
  const [activeId, setActiveId] = useState(() => {
    try {
      const currentB = activeBucket || 'general';
      const savedActive = localStorage.getItem(`${ACTIVE_CONV_PREFIX}${currentB}`);
      if (savedActive) {
        return savedActive;
      }
    } catch (e) {
      console.warn('Error reading activeId from localStorage:', e);
    }
    return '';
  });

  // Sincronizar todas las conversaciones con localStorage
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(allConversations));
    } catch (e) {
      console.error('Error saving conversations:', e);
    }
  }, [allConversations]);

  // Conversaciones filtradas estrictamente para el bucket activo
  const currentBucketName = activeBucket || 'general';
  const conversations = allConversations.filter(
    (c) => (c.bucket || 'general') === currentBucketName
  );

  // Efecto: Cuando cambia el activeBucket, asegurar que activeId corresponda a este bucket
  useEffect(() => {
    const currentB = activeBucket || 'general';
    const bucketConvs = allConversations.filter(
      (c) => (c.bucket || 'general') === currentB
    );

    if (bucketConvs.length === 0) {
      // Si este bucket aún no tiene conversaciones, crear una fresca y activarla
      const fresh = createNewConversationObject(currentB);
      setAllConversations((prev) => [fresh, ...prev]);
      setActiveId(fresh.id);
      try {
        localStorage.setItem(`${ACTIVE_CONV_PREFIX}${currentB}`, fresh.id);
      } catch (e) {}
    } else {
      // Si el activeId actual no pertenece a este bucket, seleccionar el último activo o el primero disponible
      const currentMatches = bucketConvs.some((c) => c.id === activeId);
      if (!currentMatches) {
        let candidateId = '';
        try {
          const savedForBucket = localStorage.getItem(`${ACTIVE_CONV_PREFIX}${currentB}`);
          if (savedForBucket && bucketConvs.some((c) => c.id === savedForBucket)) {
            candidateId = savedForBucket;
          }
        } catch (e) {}

        const finalId = candidateId || bucketConvs[0].id;
        setActiveId(finalId);
      }
    }
  }, [activeBucket]);

  // Sincronizar activeId del bucket actual en localStorage
  useEffect(() => {
    if (activeId) {
      try {
        const currentB = activeBucket || 'general';
        localStorage.setItem(`${ACTIVE_CONV_PREFIX}${currentB}`, activeId);
      } catch (e) {
        console.error('Error saving activeId:', e);
      }
    }
  }, [activeId, activeBucket]);

  const activeConversation =
    conversations.find((c) => c.id === activeId) ||
    conversations[0] ||
    createNewConversationObject(currentBucketName);

  const createConversation = () => {
    const newConv = createNewConversationObject(currentBucketName);
    setAllConversations((prev) => [newConv, ...prev]);
    setActiveId(newConv.id);
    return newConv;
  };

  const selectConversation = (id) => {
    setActiveId(id);
  };

  const deleteConversation = (id) => {
    setAllConversations((prev) => {
      const filtered = prev.filter((c) => c.id !== id);
      const remainingInBucket = filtered.filter(
        (c) => (c.bucket || 'general') === currentBucketName
      );

      if (remainingInBucket.length === 0) {
        const fresh = createNewConversationObject(currentBucketName);
        setActiveId(fresh.id);
        return [fresh, ...filtered];
      }

      if (activeId === id) {
        setActiveId(remainingInBucket[0].id);
      }
      return filtered;
    });
  };

  const addMessage = (convId, message) => {
    const msgId = `msg_${Date.now()}_${Math.random().toString(36).substr(2, 4)}`;
    const fullMessage = {
      id: msgId,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      ...message,
    };

    setAllConversations((prev) =>
      prev.map((conv) => {
        if (conv.id !== convId) return conv;

        const updatedMessages = [...conv.messages, fullMessage];
        let updatedTitle = conv.title;

        // Si es el primer mensaje del usuario y la conversación aún tiene el título por defecto, actualizar título
        if (conv.title === 'Nueva conversación' && message.role === 'user') {
          updatedTitle = message.text.slice(0, 32).trim() + (message.text.length > 32 ? '...' : '');
        }

        return {
          ...conv,
          title: updatedTitle,
          messages: updatedMessages,
        };
      })
    );

    return fullMessage;
  };

  const updateMessage = (convId, msgId, updates) => {
    setAllConversations((prev) =>
      prev.map((conv) => {
        if (conv.id !== convId) return conv;
        return {
          ...conv,
          messages: conv.messages.map((msg) =>
            msg.id === msgId ? { ...msg, ...(typeof updates === 'function' ? updates(msg) : updates) } : msg
          ),
        };
      })
    );
  };

  return {
    conversations,
    allConversations,
    activeConversation,
    activeId,
    createConversation,
    selectConversation,
    deleteConversation,
    addMessage,
    updateMessage,
  };
}
