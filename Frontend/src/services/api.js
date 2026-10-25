// Cliente de comunicación con la API de FastAPI
const API_PREFIX = '/api';

export const api = {
  /**
   * Verifica la disponibilidad del backend
   */
  async checkHealth() {
    try {
      const res = await fetch(`${API_PREFIX}/`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (err) {
      console.warn('Backend no disponible:', err);
      return null;
    }
  },

  /**
   * Obtiene la lista de buckets registrados en Milvus con sus metadatos
   * @returns {Promise<{buckets: Array}>}
   */
  async listBuckets() {
    const response = await fetch(`${API_PREFIX}/buckets`);
    const data = await response.json().catch(() => null);
    if (!response.ok) {
      throw new Error(data?.detail || 'Error al listar buckets');
    }
    return data;
  },

  /**
   * Crea un nuevo bucket en Milvus con su tipo de contenido y descripción
   */
  async createBucket(name, contentType = 'general', description = '', metadata = {}) {
    const response = await fetch(`${API_PREFIX}/buckets`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name,
        content_type: contentType,
        description,
        metadata,
      }),
    });
    const data = await response.json().catch(() => null);
    if (!response.ok) {
      throw new Error(data?.detail || 'Error al crear bucket');
    }
    return data;
  },

  /**
   * Elimina un bucket y su colección asociada
   */
  async deleteBucket(bucketName) {
    const response = await fetch(`${API_PREFIX}/buckets/${encodeURIComponent(bucketName)}`, {
      method: 'DELETE',
    });
    const data = await response.json().catch(() => null);
    if (!response.ok) {
      throw new Error(data?.detail || 'Error al eliminar bucket');
    }
    return data;
  },

  /**
   * Sube un archivo PDF al backend asignándolo a un bucket específico
   * @param {File} file Archivo PDF
   * @param {string} bucketName Nombre del bucket (por defecto 'general')
   * @param {string} [contentType] Tipo de contenido opcional
   * @returns {Promise<{message: string, bucket: string, content_type: string, chunks_procesados: number}>}
   */
  async uploadPdf(file, bucketName = 'general', contentType = null) {
    if (!file || !file.name.toLowerCase().endsWith('.pdf')) {
      throw new Error('Solo se admiten archivos con extensión .pdf');
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('bucket_name', bucketName || 'general');
    if (contentType) {
      formData.append('content_type', contentType);
    }

    const response = await fetch(`${API_PREFIX}/upload-file`, {
      method: 'POST',
      body: formData,
    });

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      const errorMsg = data?.detail || `Error al subir el archivo (HTTP ${response.status})`;
      throw new Error(errorMsg);
    }

    return data;
  },

  /**
   * Crea una nueva conversación en PostgreSQL para un bucket
   */
  async createConversation(bucketName, title = 'Nueva conversación', extraMetadata = {}) {
    const response = await fetch(`${API_PREFIX}/conversaciones`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        bucket_name: bucketName || 'general',
        title: title || 'Nueva conversación',
        extra_metadata: extraMetadata,
      }),
    });
    const data = await response.json().catch(() => null);
    if (!response.ok) {
      throw new Error(data?.detail || 'Error al crear conversación');
    }
    return data;
  },

  /**
   * Obtiene la lista de conversaciones de un bucket desde PostgreSQL
   */
  async listConversations(bucketName) {
    const response = await fetch(`${API_PREFIX}/buckets/${encodeURIComponent(bucketName || 'general')}/conversaciones`);
    const data = await response.json().catch(() => null);
    if (!response.ok) {
      throw new Error(data?.detail || 'Error al listar conversaciones');
    }
    return Array.isArray(data) ? data : [];
  },

  /**
   * Obtiene una conversación completa con sus mensajes desde PostgreSQL
   */
  async getConversation(conversationId) {
    const response = await fetch(`${API_PREFIX}/conversaciones/${encodeURIComponent(conversationId)}`);
    const data = await response.json().catch(() => null);
    if (!response.ok) {
      throw new Error(data?.detail || 'Error al obtener conversación');
    }
    return data;
  },

  /**
   * Elimina una conversación de PostgreSQL (cascada a sus mensajes)
   */
  async deleteConversation(conversationId) {
    const response = await fetch(`${API_PREFIX}/conversaciones/${encodeURIComponent(conversationId)}`, {
      method: 'DELETE',
    });
    const data = await response.json().catch(() => null);
    if (!response.ok) {
      throw new Error(data?.detail || 'Error al eliminar conversación');
    }
    return data;
  },

  /**
   * Envía una consulta al grafo RAG indicando el bucket y persistiendo en la conversación de PostgreSQL
   * @param {string} query Pregunta del usuario
   * @param {string} [bucketName='general'] Bucket donde buscar
   * @param {function(string, string): void} [onChunk] Callback llamado por cada token recibido (token, fullTextAcumulado)
   * @param {string} [conversationId] UUID de la conversación en PostgreSQL
   * @returns {Promise<{message?: string, bucket: string, response: string, iteration?: number, conversacion_id?: string}>}
   */
  async sendMessage(query, bucketName = 'general', onChunk = null, conversationId = null) {
    if (!query || !query.trim()) {
      throw new Error('La consulta no puede estar vacía');
    }

    const payload = {
      query: query.trim(),
      bucket_name: bucketName || 'general',
      stream: true,
    };
    if (conversationId) {
      payload.conversacion_id = conversationId;
    }

    const response = await fetch(`${API_PREFIX}/generarRespuesta`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      const errorMsg = errorData?.detail || `Error al procesar la pregunta (HTTP ${response.status})`;
      throw new Error(errorMsg);
    }

    const contentType = response.headers.get('content-type') || '';
    if (contentType.includes('text/event-stream') && response.body) {
      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';
      let fullText = '';
      let returnedConvId = conversationId;

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith('data:')) {
            const dataStr = trimmed.slice(5).trim();
            if (dataStr) {
              try {
                const parsed = JSON.parse(dataStr);
                if (parsed.error) {
                  throw new Error(parsed.error);
                }
                if (parsed.conversacion_id) {
                  returnedConvId = parsed.conversacion_id;
                }
                if (parsed.token) {
                  fullText += parsed.token;
                  if (onChunk) {
                    onChunk(parsed.token, fullText);
                  }
                }
              } catch (parseErr) {
                console.error('Error parseando SSE chunk:', parseErr);
              }
            }
          }
        }
      }

      return {
        response: fullText,
        bucket: bucketName || 'general',
        conversacion_id: returnedConvId,
      };
    } else {
      const data = await response.json().catch(() => null);
      return data || { response: '', bucket: bucketName, conversacion_id: conversationId };
    }
  },
};
