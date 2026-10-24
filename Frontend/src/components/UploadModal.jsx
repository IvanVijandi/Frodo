import React, { useState, useRef } from 'react';
import { X, UploadCloud, FileText, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { api } from '../services/api';
import { GeminiSparkle } from './GeminiSparkle';

export function UploadModal({ isOpen, onClose, onUploadSuccess }) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [status, setStatus] = useState('idle'); // 'idle' | 'uploading' | 'success' | 'error'
  const [statusMessage, setStatusMessage] = useState('');
  const [chunksCount, setChunksCount] = useState(null);
  const fileInputRef = useRef(null);

  if (!isOpen) return null;

  const resetState = () => {
    setSelectedFile(null);
    setStatus('idle');
    setStatusMessage('');
    setChunksCount(null);
  };

  const handleClose = () => {
    resetState();
    onClose();
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const validateAndSetFile = (file) => {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith('.pdf') && file.type !== 'application/pdf') {
      setStatus('error');
      setStatusMessage('Solo se admiten documentos en formato PDF (.pdf).');
      return;
    }
    setSelectedFile(file);
    setStatus('idle');
    setStatusMessage('');
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    try {
      setStatus('uploading');
      setStatusMessage('Indexando documento en Milvus...');

      const result = await api.uploadPdf(selectedFile);

      setStatus('success');
      setStatusMessage(result.message || 'Documento indexado con éxito.');
      setChunksCount(result.chunks_procesados);

      if (onUploadSuccess) {
        onUploadSuccess(selectedFile.name, result.chunks_procesados);
      }
    } catch (err) {
      setStatus('error');
      setStatusMessage(err.message || 'Error al procesar el archivo.');
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="gemini-modal-overlay" onClick={handleClose}>
      <div className="gemini-modal-card" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="gemini-modal-header">
          <div className="gemini-modal-title-group">
            <GeminiSparkle size={22} />
            <div>
              <h3>Cargar Documento PDF</h3>
              <p className="gemini-modal-sub">Alimenta la base de conocimiento vectorial de MARIA</p>
            </div>
          </div>
          <button className="gemini-icon-btn" onClick={handleClose} type="button">
            <X size={18} />
          </button>
        </div>

        {/* Body */}
        <div className="gemini-modal-body">
          <div
            className={`gemini-dropzone ${dragActive ? 'drag-active' : ''} ${selectedFile ? 'has-file' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => status !== 'uploading' && fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,application/pdf"
              style={{ display: 'none' }}
              onChange={handleFileChange}
              disabled={status === 'uploading'}
            />

            {!selectedFile ? (
              <div className="gemini-dropzone-inner">
                <div className="gemini-dropzone-icon">
                  <UploadCloud size={30} />
                </div>
                <h4>Arrastra un PDF aquí</h4>
                <p>o haz clic para examinar tus archivos</p>
                <span className="gemini-pdf-badge">Formato PDF hasta 100 MB</span>
              </div>
            ) : (
              <div className="gemini-selected-file">
                <FileText size={32} className="text-accent" />
                <div className="gemini-file-meta">
                  <span className="file-name">{selectedFile.name}</span>
                  <span className="file-size">{formatFileSize(selectedFile.size)}</span>
                </div>
                {status !== 'uploading' && (
                  <button
                    type="button"
                    className="gemini-change-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      resetState();
                    }}
                  >
                    Cambiar
                  </button>
                )}
              </div>
            )}
          </div>

          {/* Feedback */}
          {status === 'uploading' && (
            <div className="gemini-feedback-box feedback-loading">
              <Loader2 size={18} className="spinner" />
              <div>
                <p className="feedback-title">Procesando y generando embeddings...</p>
                <p className="feedback-desc">Dividiendo el texto y almacenando vectores en Milvus.</p>
              </div>
            </div>
          )}

          {status === 'success' && (
            <div className="gemini-feedback-box feedback-success">
              <CheckCircle2 size={20} className="text-success" />
              <div>
                <p className="feedback-title">Documento indexado con éxito</p>
                <p className="feedback-desc">
                  Se generaron e insertaron <strong>{chunksCount} fragmentos</strong>. Ya puedes hacerle preguntas en el chat.
                </p>
              </div>
            </div>
          )}

          {status === 'error' && (
            <div className="gemini-feedback-box feedback-error">
              <AlertCircle size={20} className="text-error" />
              <div>
                <p className="feedback-title">No se pudo procesar</p>
                <p className="feedback-desc">{statusMessage}</p>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="gemini-modal-footer">
          <button
            type="button"
            className="gemini-btn-text"
            onClick={handleClose}
            disabled={status === 'uploading'}
          >
            {status === 'success' ? 'Cerrar' : 'Cancelar'}
          </button>

          {status !== 'success' && (
            <button
              type="button"
              className="gemini-btn-pill"
              onClick={handleUpload}
              disabled={!selectedFile || status === 'uploading'}
            >
              {status === 'uploading' ? (
                <>
                  <Loader2 size={16} className="spinner" /> Subiendo...
                </>
              ) : (
                'Subir e Indexar'
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
