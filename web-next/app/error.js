'use client';
import Link from 'next/link';

export default function Error({ error, reset }) {
  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#0a0a0f',
      color: '#fff',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px',
      textAlign: 'center',
      fontFamily: 'system-ui, sans-serif'
    }}>
      <h1 style={{ fontSize: '32px', fontWeight: '900', color: '#e50914', marginBottom: '12px' }}>
        DramaPe
      </h1>
      <p style={{ color: '#aaa', fontSize: '16px', maxWidth: '400px', marginBottom: '24px' }}>
        Ha ocurrido una pequeña interrupción momentánea al conectar con el servidor.
      </p>
      <div style={{ display: 'flex', gap: '12px' }}>
        <button
          onClick={() => reset()}
          style={{
            padding: '10px 20px',
            background: '#e50914',
            color: '#fff',
            border: 'none',
            borderRadius: '8px',
            fontWeight: '700',
            cursor: 'pointer'
          }}
        >
          Reintentar
        </button>
        <Link
          href="/"
          style={{
            padding: '10px 20px',
            background: 'rgba(255,255,255,0.1)',
            color: '#fff',
            borderRadius: '8px',
            textDecoration: 'none',
            fontWeight: '600'
          }}
        >
          Ir al Inicio
        </Link>
      </div>
    </div>
  );
}
