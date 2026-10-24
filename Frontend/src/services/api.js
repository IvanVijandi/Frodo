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
   * Sube un archivo PDF al backend para ser procesado e indexado en Milvus
   * @param {File} file Archivo PDF
   * @returns {Promise<{message: string, chunks_procesados: number}>}
   */
  async uploadPdf(file) {
    if (!file || !file.name.toLowerCase().endsWith('.pdf')) {
      throw new Error('Solo se admiten archivos con extensión .pdf');
    }

    const formData = new FormData();
    formData.append('file', file);

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
   * Envía una consulta al grafo RAG
   * @param {string} query Pregunta del usuario
   * @returns {Promise<{message: string, response: string, iteration: number}>}
   */
  async sendMessage(query) {
    if (!query || !query.trim()) {
      throw new Error('La consulta no puede estar vacía');
    }

    const response = await fetch(`${API_PREFIX}/generarRespuesta`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query: query.trim() }),
    });

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      const errorMsg = data?.detail || `Error al procesar la pregunta (HTTP ${response.status})`;
      throw new Error(errorMsg);
    }

    return data;
  },
};

