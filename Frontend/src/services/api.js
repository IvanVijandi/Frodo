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
   * Envía una consulta al grafo RAG indicando el bucket de búsqueda
   * @param {string} query Pregunta del usuario
   * @param {string} [bucketName='general'] Bucket donde buscar
   * @returns {Promise<{message: string, bucket: string, response: string, iteration: number}>}
   */
  async sendMessage(query, bucketName = 'general') {
    if (!query || !query.trim()) {
      throw new Error('La consulta no puede estar vacía');
    }

    const response = await fetch(`${API_PREFIX}/generarRespuesta`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: query.trim(),
        bucket_name: bucketName || 'general',
      }),
    });

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      const errorMsg = data?.detail || `Error al procesar la pregunta (HTTP ${response.status})`;
      throw new Error(errorMsg);
    }

    return data;
  },
};
