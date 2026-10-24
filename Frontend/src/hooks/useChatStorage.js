import { useState, useEffect } from 'react';

const STORAGE_KEY = 'maria_rag_conversations_v1';
const ACTIVE_CONV_KEY = 'maria_rag_active_conv_v1';

function createNewConversationObject() {
  const now = new Date();
  return {
    id: `conv_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`,
    title: 'Nueva conversación',
    createdAt: now.toISOString(),
    messages: [
      {
        id: `msg_welcome_${Date.now()}`,
        role: 'assistant',
        text: '¡Hola! Soy **MARIA**, tu asistente RAG. Puedo responder preguntas consultando los documentos PDF que subas a la base de conocimiento vectorial.',
        timestamp: now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ],
  };
}

export function useChatStorage() {
  const [conversations, setConversations] = useState(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed) && parsed.length > 0) {
          return parsed;
        }
      }
    } catch (e) {
      console.warn('Error reading conversations from localStorage:', e);
    }
    const initial = createNewConversationObject();
    return [initial];
  });

  const [activeId, setActiveId] = useState(() => {
    try {
      const savedActive = localStorage.getItem(ACTIVE_CONV_KEY);
      if (savedActive && conversations.some((c) => c.id === savedActive)) {
        return savedActive;
      }
    } catch (e) {
      console.warn('Error reading activeId from localStorage:', e);
    }
    return conversations[0]?.id || '';
  });

  // Sincronizar con localStorage
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations));
    } catch (e) {
      console.error('Error saving conversations:', e);
    }
  }, [conversations]);

  useEffect(() => {
    try {
      localStorage.setItem(ACTIVE_CONV_KEY, activeId);
    } catch (e) {
      console.error('Error saving activeId:', e);
    }
  }, [activeId]);

  const activeConversation = conversations.find((c) => c.id === activeId) || conversations[0];

  const createConversation = () => {
    const newConv = createNewConversationObject();
    setConversations((prev) => [newConv, ...prev]);
    setActiveId(newConv.id);
    return newConv;
  };

  const selectConversation = (id) => {
    setActiveId(id);
  };

  const deleteConversation = (id) => {
    setConversations((prev) => {
      const filtered = prev.filter((c) => c.id !== id);
      if (filtered.length === 0) {
        const fresh = createNewConversationObject();
        setActiveId(fresh.id);
        return [fresh];
      }
      if (activeId === id) {
        setActiveId(filtered[0].id);
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

    setConversations((prev) =>
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

  return {
    conversations,
    activeConversation,
    activeId,
    createConversation,
    selectConversation,
    deleteConversation,
    addMessage,
  };
}

