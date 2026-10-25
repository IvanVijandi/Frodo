import React, { useState, useEffect, useCallback } from 'react';
import {
  ArrowLeft,
  FileText,
  Upload,
  Trash2,
  MessageSquare,
  ArrowUpRight,
  Database,
  Loader2,
  RefreshCw,
  AlertCircle,
  FileCheck,
  CheckCircle2
} from 'lucide-react';
import { api } from '../services/api';
import { MariaVectorLogo } from './MariaVectorLogo';

export function BucketDetailsView({
  bucketName,
  bucketInfo,
  onBackToHub,
  onOpenChat,
  onOpenUpload,
  onBucketDeleted,
}) {
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDeletingDoc, setIsDeletingDoc] = useState(null); // filename being deleted
  const [isDeletingBucket, setIsDeletingBucket] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  const loadDocuments = useCallback(async () => {
    if (!bucketName) return;
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const docs = await api.listBucketDocuments(bucketName);
      setDocuments(docs || []);
    } catch (err) {
      console.warn('Error al cargar documentos del bucket:', err);
      setErrorMsg(err.message || 'No se pudieron cargar los documentos.');
    } finally {
      setIsLoading(false);
    }
  }, [bucketName]);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  const handleDeleteDocument = async (filename) => {
    if (!confirm(`¿Eliminar el documento "${filename}" del bucket "${bucketName}"? Se borrarán todos sus fragmentos vectoriales.`)) {
      return;
    }

    setIsDeletingDoc(filename);
    setErrorMsg(null);
    try {
      await api.deleteBucketDocument(bucketName, filename);
      setSuccessMsg(`Documento "${filename}" eliminado.`);
      setTimeout(() => setSuccessMsg(null), 3000);
      await loadDocuments();
    } catch (err) {
      setErrorMsg(err.message || 'Error al eliminar el documento.');
    } finally {
      setIsDeletingDoc(null);
    }
  };

  const handleDeleteBucket = async () => {
    if (bucketName === 'general') return;
    if (!confirm(`¿Estás seguro de eliminar el bucket "${bucketName}"? Se borrarán sus documentos y colecciones vectoriales.`)) {
      return;
    }

    setIsDeletingBucket(true);
    try {
      await api.deleteBucket(bucketName);
      if (onBucketDeleted) {
        await onBucketDeleted(bucketName);
      }
      onBackToHub();
    } catch (err) {
      setErrorMsg(err.message || 'Error al eliminar el bucket.');
      setIsDeletingBucket(false);
    }
  };

  const totalChunks = documents.reduce((acc, d) => acc + (d.chunks_count || 0), 0);

  return (
    <div className="hub-page-wrapper">
      {/* Barra Superior */}
      <header className="hub-header">
        <div className="hub-header-inner">
          <div className="hub-brand" onClick={onBackToHub} style={{ cursor: 'pointer' }}>
            <MariaVectorLogo size={46} />
            <span className="hub-brand-name">Frodo</span>
          </div>

          <button
            type="button"
            className="hub-btn-new-space"
            onClick={onBackToHub}
            style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}
          >
            <ArrowLeft size={14} />
            <span>Volver a buckets</span>
          </button>
        </div>
      </header>

      {/* Contenedor Principal */}
      <main className="hub-main-content">
        {/* Banner del Bucket */}
        <div className="hub-hero-section" style={{ paddingBottom: '1.5rem' }}>
          <div className="hub-hero-left" style={{ maxWidth: '100%' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '0.5rem' }}>
              <span className="hub-count-badge" style={{ textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                {bucketInfo?.content_type || 'general'}
              </span>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                {totalChunks} fragmentos indexados
              </span>
            </div>

            <h1 className="hub-hero-title" style={{ fontSize: '2.2rem', marginBottom: '0.5rem' }}>
              Administrar <span className="hub-title-highlight">{bucketName}</span>
            </h1>

            <p className="hub-hero-sub" style={{ maxWidth: '650px' }}>
              {bucketInfo?.description || 'Gestiona los documentos PDF, fragmentación vectorial y configuración de este espacio de conocimiento.'}
            </p>

            {/* Botones de acción principales */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', marginTop: '1.25rem' }}>
              <button
                type="button"
                className="hub-btn-open-chat"
                onClick={() => onOpenChat && onOpenChat(bucketName)}
                style={{ padding: '0.65rem 1.25rem', fontSize: '0.95rem', borderRadius: '10px' }}
              >
                <MessageSquare size={16} />
                <span>Abrir chat de este bucket</span>
                <ArrowUpRight size={16} />
              </button>

              <button
                type="button"
                className="hub-btn-new-space"
                onClick={() => onOpenUpload && onOpenUpload(bucketName)}
                style={{ padding: '0.65rem 1.25rem', fontSize: '0.95rem', borderRadius: '10px', background: 'var(--bg-card)' }}
              >
                <Upload size={16} />
                <span>Subir documento PDF</span>
              </button>

              <button
                type="button"
                className="maria-icon-btn-ghost"
                onClick={loadDocuments}
                title="Actualizar lista"
                style={{ padding: '0.65rem', borderRadius: '10px' }}
              >
                <RefreshCw size={16} className={isLoading ? 'spin-animation' : ''} />
              </button>

              {bucketName !== 'general' && (
                <button
                  type="button"
                  onClick={handleDeleteBucket}
                  disabled={isDeletingBucket}
                  className="maria-history-del"
                  style={{ opacity: 1, padding: '0.65rem 1rem', borderRadius: '10px', marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '6px', color: '#ef4444' }}
                  title="Eliminar este bucket"
                >
                  <Trash2 size={15} />
                  <span>Eliminar bucket</span>
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Notificaciones */}
        {errorMsg && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '0.75rem 1rem', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '8px', color: '#f87171', marginBottom: '1.5rem' }}>
            <AlertCircle size={16} />
            <span>{errorMsg}</span>
          </div>
        )}

        {successMsg && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '0.75rem 1rem', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '8px', color: '#34d399', marginBottom: '1.5rem' }}>
            <CheckCircle2 size={16} />
            <span>{successMsg}</span>
          </div>
        )}

        {/* Sección de Documentos */}
        <div className="hub-section-header" style={{ marginTop: '1rem' }}>
          <div className="hub-section-title-wrap">
            <h2 className="hub-section-title">Documentos cargados</h2>
            <p className="hub-section-sub">Archivos indexados disponibles para consulta semántica en el chat</p>
          </div>
          <span className="hub-count-badge">
            {documents.length} {documents.length === 1 ? 'archivo' : 'archivos'}
          </span>
        </div>

        {isLoading ? (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
            <Loader2 size={24} className="spin-animation" style={{ marginRight: '8px' }} />
            <span>Consultando documentos en la base de datos...</span>
          </div>
        ) : documents.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem 1.5rem', background: 'var(--bg-card)', border: '1px dashed var(--border-color)', borderRadius: '16px', margin: '1rem 0' }}>
            <FileText size={38} className="text-muted" style={{ margin: '0 auto 1rem' }} />
            <h3 style={{ fontSize: '1.1rem', marginBottom: '0.5rem', fontWeight: 600 }}>Aún no hay documentos en este bucket</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', maxWidth: '420px', margin: '0 auto 1.5rem' }}>
              Sube tus primeros archivos PDF para fragmentarlos, vectorizarlos e interactuar con su contenido desde el chat.
            </p>
            <button
              type="button"
              className="hub-btn-open-chat"
              onClick={() => onOpenUpload && onOpenUpload(bucketName)}
              style={{ display: 'inline-flex', padding: '0.65rem 1.25rem', borderRadius: '10px' }}
            >
              <Upload size={16} />
              <span>Subir documento PDF</span>
            </button>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '16px', marginTop: '1rem' }}>
            {documents.map((doc) => (
              <div
                key={doc.filename}
                style={{
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '12px',
                  padding: '1.25rem',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  transition: 'all 0.2s ease',
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                    <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: 'rgba(16, 185, 129, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <FileCheck size={18} className="text-emerald" />
                    </div>
                    <span style={{ fontSize: '0.75rem', padding: '2px 8px', borderRadius: '12px', background: 'var(--bg-hover)', color: 'var(--text-muted)' }}>
                      PDF
                    </span>
                  </div>

                  <h4
                    style={{
                      fontSize: '0.95rem',
                      fontWeight: 600,
                      marginBottom: '0.4rem',
                      wordBreak: 'break-all',
                      lineHeight: '1.3'
                    }}
                    title={doc.filename}
                  >
                    {doc.filename}
                  </h4>

                  <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
                    {doc.chunks_count} {doc.chunks_count === 1 ? 'fragmento vectorial' : 'fragmentos vectoriales'}
                  </p>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', paddingTop: '0.75rem', borderTop: '1px solid var(--border-color)' }}>
                  <button
                    type="button"
                    onClick={() => handleDeleteDocument(doc.filename)}
                    disabled={isDeletingDoc === doc.filename}
                    style={{
                      background: 'transparent',
                      border: 'none',
                      color: 'var(--text-muted)',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                      fontSize: '0.82rem',
                      padding: '4px 8px',
                      borderRadius: '6px',
                      transition: 'all 0.15s ease'
                    }}
                    onMouseEnter={(e) => { e.currentTarget.style.color = '#ef4444'; e.currentTarget.style.background = 'rgba(239, 68, 68, 0.1)'; }}
                    onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--text-muted)'; e.currentTarget.style.background = 'transparent'; }}
                    title={`Quitar ${doc.filename} de este bucket`}
                  >
                    {isDeletingDoc === doc.filename ? (
                      <Loader2 size={14} className="spin-animation" />
                    ) : (
                      <Trash2 size={14} />
                    )}
                    <span>Quitar</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

