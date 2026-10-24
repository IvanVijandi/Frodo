import React, { useState } from 'react';
import { X, FolderKanban, Plus, Trash2, Check, AlertCircle, Loader2, Database, Info, Layers } from 'lucide-react';
import { api } from '../services/api';

const CONTENT_TYPE_PRESETS = [
  { value: 'general', label: '📁 General', desc: 'Todo tipo de documentos' },
  { value: 'legal', label: '⚖️ Legal', desc: 'Contratos, leyes y normativas' },
  { value: 'financiero', label: '📊 Financiero', desc: 'Reportes, balances e impuestos' },
  { value: 'tecnico', label: '⚙️ Técnico', desc: 'Manuales, código y arquitectura' },
  { value: 'medico', label: '🩺 Médico', desc: 'Historias clínicas y estudios' },
  { value: 'academico', label: '🎓 Académico', desc: 'Papers, tesis e investigaciones' },
  { value: 'otro', label: '✏️ Otro...', desc: 'Definir categoría personalizada' },
];

export function BucketManagerModal({
  isOpen,
  onClose,
  buckets = [],
  activeBucket = 'general',
  onSelectActiveBucket,
  onBucketsChanged,
}) {
  const [activeTab, setActiveTab] = useState('list'); // 'list' | 'create'
  
  // Form State
  const [newBucketName, setNewBucketName] = useState('');
  const [selectedPreset, setSelectedPreset] = useState('general');
  const [customContentType, setCustomContentType] = useState('');
  const [newDescription, setNewDescription] = useState('');
  
  const [isLoading, setIsLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState(null); // { type: 'success' | 'error', text: '' }

  if (!isOpen) return null;

  const resetForm = () => {
    setNewBucketName('');
    setSelectedPreset('general');
    setCustomContentType('');
    setNewDescription('');
    setStatusMessage(null);
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  const handleCreateBucket = async (e) => {
    e?.preventDefault();
    if (!newBucketName.trim()) {
      setStatusMessage({ type: 'error', text: 'El nombre del bucket es requerido.' });
      return;
    }

    const effectiveContentType = selectedPreset === 'otro'
      ? (customContentType.trim() || 'general')
      : selectedPreset;

    setIsLoading(true);
    setStatusMessage(null);

    try {
      const result = await api.createBucket(
        newBucketName.trim(),
        effectiveContentType,
        newDescription.trim()
      );

      setStatusMessage({
        type: 'success',
        text: `Bucket '${result.bucket?.name || newBucketName}' creado exitosamente en Milvus.`
      });

      if (onBucketsChanged) {
        await onBucketsChanged();
      }

      // Cambiar automáticamente al nuevo bucket creado
      if (onSelectActiveBucket && result.bucket?.name) {
        onSelectActiveBucket(result.bucket.name);
      }

      setTimeout(() => {
        resetForm();
        setActiveTab('list');
      }, 1200);
    } catch (err) {
      setStatusMessage({
        type: 'error',
        text: err.message || 'Error al crear el bucket.'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteBucket = async (bucketName) => {
    if (bucketName === 'general') return;

    const confirm = window.confirm(
      `¿Estás seguro de que deseas eliminar el bucket '${bucketName}'?\nSe eliminarán todos los fragmentos vectoriales almacenados en Milvus.`
    );
    if (!confirm) return;

    try {
      setIsLoading(true);
      await api.deleteBucket(bucketName);
      
      if (activeBucket === bucketName && onSelectActiveBucket) {
        onSelectActiveBucket('general');
      }

      if (onBucketsChanged) {
        await onBucketsChanged();
      }
    } catch (err) {
      alert(`Error al eliminar bucket: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="gemini-modal-overlay" onClick={handleClose}>
      <div className="gemini-modal-card bucket-manager-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="gemini-modal-header">
          <div className="gemini-modal-title-group">
            <div className="bucket-icon-badge">
              <FolderKanban size={22} />
            </div>
            <div>
              <h3>Administrar Buckets de Información</h3>
              <p className="gemini-modal-sub">Colecciones vectoriales temáticas en Milvus</p>
            </div>
          </div>
          <button className="gemini-icon-btn" onClick={handleClose} type="button">
            <X size={18} />
          </button>
        </div>

        {/* Tab Switcher */}
        <div className="bucket-tabs-nav">
          <button
            className={`bucket-tab-btn ${activeTab === 'list' ? 'active' : ''}`}
            onClick={() => setActiveTab('list')}
            type="button"
          >
            <Layers size={16} />
            <span>Tus Buckets ({buckets.length})</span>
          </button>
          <button
            className={`bucket-tab-btn ${activeTab === 'create' ? 'active' : ''}`}
            onClick={() => setActiveTab('create')}
            type="button"
          >
            <Plus size={16} />
            <span>Crear Nuevo Bucket</span>
          </button>
        </div>

        {/* Modal Body */}
        <div className="gemini-modal-body bucket-modal-body">
          {activeTab === 'list' ? (
            /* Lista de Buckets */
            <div className="buckets-list-container">
              {buckets.map((b) => {
                const isActive = b.name === activeBucket;
                const isGeneral = b.name === 'general';

                return (
                  <div
                    key={b.name}
                    className={`bucket-card ${isActive ? 'bucket-card-active' : ''}`}
                    onClick={() => onSelectActiveBucket && onSelectActiveBucket(b.name)}
                  >
                    <div className="bucket-card-header">
                      <div className="bucket-name-row">
                        <span className="bucket-name">{b.name}</span>
                        {isActive && (
                          <span className="bucket-active-chip">
                            <Check size={12} /> Activo en chat
                          </span>
                        )}
                      </div>
                      <span className="bucket-content-type-badge">
                        {b.content_type || 'general'}
                      </span>
                    </div>

                    <p className="bucket-desc">
                      {b.description || 'Sin descripción asignada.'}
                    </p>

                    <div className="bucket-card-footer">
                      <div className="bucket-stats">
                        <span className="stats-chunks">
                          <strong>{b.total_chunks || 0}</strong> fragmentos
                        </span>
                        {b.created_at && (
                          <span className="stats-date">
                            {new Date(b.created_at).toLocaleDateString([], { month: 'short', day: 'numeric' })}
                          </span>
                        )}
                      </div>

                      <div className="bucket-actions">
                        {!isActive && (
                          <button
                            type="button"
                            className="btn-select-bucket"
                            onClick={(e) => {
                              e.stopPropagation();
                              onSelectActiveBucket(b.name);
                            }}
                          >
                            Seleccionar
                          </button>
                        )}

                        {!isGeneral && (
                          <button
                            type="button"
                            className="btn-delete-bucket"
                            title="Eliminar este bucket"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteBucket(b.name);
                            }}
                          >
                            <Trash2 size={14} />
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            /* Formulario de Creación de Bucket */
            <form className="bucket-create-form" onSubmit={handleCreateBucket}>
              {statusMessage && (
                <div className={`gemini-feedback-box feedback-${statusMessage.type}`}>
                  {statusMessage.type === 'error' ? (
                    <AlertCircle size={18} className="text-error" />
                  ) : (
                    <Check size={18} className="text-success" />
                  )}
                  <div>
                    <p className="feedback-title">
                      {statusMessage.type === 'error' ? 'Atención' : 'Éxito'}
                    </p>
                    <p className="feedback-desc">{statusMessage.text}</p>
                  </div>
                </div>
              )}

              <div className="form-field">
                <label className="field-label">Nombre del Bucket</label>
                <input
                  type="text"
                  className="field-input"
                  placeholder="ej: finanzas_2026, manuales_tecnicos, legal"
                  value={newBucketName}
                  onChange={(e) => setNewBucketName(e.target.value)}
                  disabled={isLoading}
                  required
                />
                <span className="field-hint">
                  Se normalizará en minúsculas y guiones bajos para Milvus.
                </span>
              </div>

              <div className="form-field">
                <label className="field-label">Tipo de Contenido</label>
                <div className="preset-chips-grid">
                  {CONTENT_TYPE_PRESETS.map((preset) => (
                    <button
                      key={preset.value}
                      type="button"
                      className={`preset-chip ${selectedPreset === preset.value ? 'preset-active' : ''}`}
                      onClick={() => setSelectedPreset(preset.value)}
                    >
                      <span className="preset-label">{preset.label}</span>
                      <span className="preset-desc">{preset.desc}</span>
                    </button>
                  ))}
                </div>

                {selectedPreset === 'otro' && (
                  <div className="custom-type-input-box">
                    <input
                      type="text"
                      className="field-input"
                      placeholder="Escribe el tipo de contenido personalizado..."
                      value={customContentType}
                      onChange={(e) => setCustomContentType(e.target.value)}
                    />
                  </div>
                )}
              </div>

              <div className="form-field">
                <label className="field-label">Descripción (Opcional)</label>
                <textarea
                  className="field-textarea"
                  placeholder="Explica qué clase de información o documentos contendrá este bucket..."
                  value={newDescription}
                  onChange={(e) => setNewDescription(e.target.value)}
                  rows={2}
                  disabled={isLoading}
                />
              </div>

              <div className="create-form-footer">
                <button
                  type="button"
                  className="gemini-btn-text"
                  onClick={() => setActiveTab('list')}
                  disabled={isLoading}
                >
                  Volver a la lista
                </button>
                <button
                  type="submit"
                  className="gemini-btn-pill"
                  disabled={!newBucketName.trim() || isLoading}
                >
                  {isLoading ? (
                    <>
                      <Loader2 size={16} className="spinner" /> Creando colección...
                    </>
                  ) : (
                    'Crear Bucket en Milvus'
                  )}
                </button>
              </div>
            </form>
          )}
        </div>

        {/* Footer */}
        {activeTab === 'list' && (
          <div className="gemini-modal-footer">
            <div className="modal-footer-info">
              <Info size={14} className="text-muted" />
              <span>El bucket seleccionado determina sobre qué colección busca el asistente RAG.</span>
            </div>
            <button
              type="button"
              className="gemini-btn-pill"
              onClick={handleClose}
            >
              Listo
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

