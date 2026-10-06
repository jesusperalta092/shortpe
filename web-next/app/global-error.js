'use client';

export default function GlobalError({ error, reset }) {
  return (
    <html>
      <body style={{ backgroundColor: '#0a0a0f', color: '#fff', textAlign: 'center', padding: '50px 20px', fontFamily: 'sans-serif' }}>
        <h2 style={{ color: '#e50914' }}>DramaPe — Algo salió mal</h2>
        <button
          onClick={() => reset()}
          style={{ padding: '10px 20px', background: '#e50914', color: '#fff', border: 'none', borderRadius: '8px', cursor: 'pointer', marginTop: '20px' }}
        >
          Reintentar
        </button>
      </body>
    </html>
  );
}
