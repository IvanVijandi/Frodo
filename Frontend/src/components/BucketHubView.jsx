import React from 'react';
import {
  ArrowUpRight,
  Database,
  BookOpen,
  FolderKanban,
  FileText,
  Upload,
  ShieldCheck,
  Plus,
  Coins,
  Settings2,
  MessageSquare,
} from 'lucide-react';
import { MariaVectorLogo } from './MariaVectorLogo';

export function BucketHubView({
  buckets = [],
  activeBucket = 'general',
  onSelectBucketAndChat,
  onOpenUploadForBucket,
  onOpenBucketManager,
  onManageBucket,
}) {
  // Función para elegir icono adecuado según nombre o tipo
  const getBucketIcon = (bucket) => {
    const name = (bucket.name || '').toLowerCase();
    const type = (bucket.content_type || '').toLowerCase();

    if (name.includes('cripto') || name.includes('crypto') || name.includes('btc') || type.includes('finan')) {
      return <Coins size={20} className="hub-icon-emerald" />;
    }
    if (name.includes('market') || type.includes('academ') || type.includes('legal')) {
      return <BookOpen size={20} className="hub-icon-emerald" />;
    }
    if (name.includes('proyect') || name.includes('doc') || type.includes('tecnic')) {
      return <FolderKanban size={20} className="hub-icon-emerald" />;
    }
    return <Database size={20} className="hub-icon-emerald" />;
  };

  // Capitalización amigable del nombre
  const formatBucketName = (name) => {
    if (!name) return 'General';
    return name.charAt(0).toUpperCase() + name.slice(1);
  };

  // Descripción con fallback elegante
  const getBucketDescription = (bucket) => {
    if (bucket.description && bucket.description.trim()) {
      return bucket.description;
    }
    const name = (bucket.name || '').toLowerCase();
    const type = (bucket.content_type || '').toLowerCase();

    if (name.includes('cripto') || name.includes('crypto')) {
      return 'Bitcoin, blockchain y activos digitales.';
    }
    if (name.includes('market')) {
      return 'Campañas, investigación y guía de marca.';
    }
    if (name.includes('proyect')) {
      return 'Briefs, notas y documentación de producto.';
    }
    if (type.includes('legal')) {
      return 'Contratos, leyes y acuerdos legales.';
    }
    if (type.includes('tecnic')) {
      return 'Manuales, arquitectura y código.';
    }
    return 'Documentación y fragmentos de conocimiento indexados.';
  };

  // Fecha o tiempo relativo
  const formatRelativeTime = (createdAt) => {
    if (!createdAt) return 'Actualizado recientemente';
    try {
      const date = new Date(createdAt);
      if (isNaN(date.getTime())) return 'Actualizado recientemente';
      const diffMs = Date.now() - date.getTime();
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
      if (diffHours < 1) return 'Actualizado hace poco';
      if (diffHours < 24) return `Actualizado hace ${diffHours} h`;
      const diffDays = Math.floor(diffHours / 24);
      if (diffDays === 1) return 'Actualizado ayer';
      if (diffDays < 7) return `Actualizado hace ${diffDays} días`;
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    } catch {
      return 'Actualizado recientemente';
    }
  };

  return (
    <div className="hub-page-wrapper">
      {/* Navbar Superior */}
      <header className="hub-header">
        <div className="hub-header-inner">
          <div className="hub-brand">
            <MariaVectorLogo size={24} />
            <span className="hub-brand-name">MARIA</span>
          </div>
        </div>
      </header>

      {/* Contenido Central */}
      <main className="hub-main-content">
        {/* Hero Section */}
        <div className="hub-hero-section">
          <div className="hub-hero-left">
            <h1 className="hub-hero-title">
              ¿Qué quieres <span className="hub-title-highlight">consultar</span> hoy?
            </h1>
            <p className="hub-hero-sub">
              Elige un bucket para conversar con la información que guardaste allí.
            </p>
          </div>

          <div className="hub-hero-right">
            <div className="hub-quote-card">
              <div className="hub-quote-line"></div>
              <p className="hub-quote-text">
                Cada espacio reúne sus documentos y conversaciones en un solo lugar.
              </p>
            </div>
          </div>
        </div>

        {/* Encabezado de Sección "Mis buckets" */}
        <div className="hub-section-header">
          <div className="hub-section-title-wrap">
            <h2 className="hub-section-title">Mis buckets</h2>
            <p className="hub-section-sub">Selecciona un espacio para continuar</p>
          </div>

          <div className="hub-section-actions">
            <span className="hub-count-badge">
              {buckets.length} {buckets.length === 1 ? 'espacio' : 'espacios'}
            </span>
            {onOpenBucketManager && (
              <button
                type="button"
                className="hub-btn-new-space"
                onClick={onOpenBucketManager}
                title="Crear o administrar buckets"
              >
                <Plus size={14} />
                <span>Nuevo bucket</span>
              </button>
            )}
          </div>
        </div>

        {/* Grid de Tarjetas de Buckets */}
        <div className="hub-cards-grid">
          {buckets.map((b) => {
            const isCurrentActive = b.name === activeBucket;
            const chunksCount = b.total_chunks ?? 0;

            return (
              <div
                key={b.name}
                className={`hub-bucket-card ${isCurrentActive ? 'is-active-card' : ''}`}
                onClick={() => onSelectBucketAndChat(b.name)}
              >
                <div className="hub-card-top">
                  <div className="hub-card-icon-box">
                    {getBucketIcon(b)}
                  </div>
                  <button
                    type="button"
                    className="hub-card-arrow-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectBucketAndChat(b.name);
                    }}
                    title={`Abrir chat en ${b.name}`}
                  >
                    <ArrowUpRight size={17} />
                  </button>
                </div>

                <h3 className="hub-card-title">{formatBucketName(b.name)}</h3>
                <p className="hub-card-desc">{getBucketDescription(b)}</p>

                <div className="hub-card-meta">
                  <div className="hub-card-stat">
                    <FileText size={14} className="text-muted" />
                    <span>{chunksCount} {chunksCount === 1 ? 'documento' : 'documentos'}</span>
                  </div>
                  <span className="hub-card-time">{formatRelativeTime(b.created_at)}</span>
                </div>

                <div className="hub-card-actions" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                  <button
                    type="button"
                    className="hub-btn-new-space"
                    onClick={(e) => {
                      e.stopPropagation();
                      onManageBucket && onManageBucket(b.name);
                    }}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '6px',
                      padding: '0.6rem 0.5rem',
                      fontSize: '0.85rem',
                      background: 'var(--bg-card)',
                      border: '1px solid var(--border-color)',
                      borderRadius: '8px',
                      color: 'var(--text-main)',
                      cursor: 'pointer',
                      whiteSpace: 'nowrap'
                    }}
                    title={`Administrar documentos y configuración de ${b.name}`}
                  >
                    <Settings2 size={15} />
                    <span>Administrar</span>
                  </button>

                  <button
                    type="button"
                    className="hub-btn-open-chat"
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectBucketAndChat(b.name);
                    }}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '6px',
                      padding: '0.6rem 0.5rem',
                      fontSize: '0.85rem',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      whiteSpace: 'nowrap'
                    }}
                    title={`Abrir chat en el bucket ${b.name}`}
                  >
                    <MessageSquare size={15} />
                    <span>Abrir chat</span>
                    <ArrowUpRight size={14} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        {/* Footer Informativo de Seguridad y Contexto */}
        <div className="hub-security-footer">
          <ShieldCheck size={16} className="text-emerald" />
          <span>MARIA mantiene cada conversación dentro del contexto de su bucket.</span>
        </div>
      </main>
    </div>
  );
}

