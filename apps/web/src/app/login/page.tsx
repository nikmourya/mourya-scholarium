'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import useStore, { wakeUpServer } from '@/store/useStore';

export default function LoginPage() {
  const router = useRouter();
  const login = useStore(s => s.login);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [waking, setWaking] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setWaking(false);
    try {
      // Wake up Render free-tier before making the real login call
      await wakeUpServer(() => {
        setWaking(true);
      });
      setWaking(false);

      await login(email, password);
      router.push('/dashboard');
    } catch (err: any) {
      setWaking(false);
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const isDisabled = loading || waking;

  return (
    <div className="page-center" style={{ background: 'linear-gradient(135deg, #0A1628 0%, #1A2A42 100%)' }}>
      <div className="card" style={{ width: '100%', maxWidth: 420 }}>
        <div style={{ textAlign: 'center', marginBottom: 28 }}>
          <div style={{ width: 56, height: 56, margin: '0 auto 12px', background: 'rgba(201,168,76,0.15)', border: '2px solid #C9A84C', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <span style={{ fontFamily: 'var(--font-display)', fontSize: 20, fontWeight: 700, color: '#C9A84C' }}>MS</span>
          </div>
          <h2>Welcome Back</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: 14, marginTop: 4 }}>Sign in to Mourya Scholarium</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 16 }}>
            <label className="label">Email</label>
            <input className="input" type="email" value={email} onChange={e => setEmail(e.target.value)} required placeholder="you@institution.edu" />
          </div>
          <div style={{ marginBottom: 20 }}>
            <label className="label">Password</label>
            <input className="input" type="password" value={password} onChange={e => setPassword(e.target.value)} required placeholder="••••••••" />
          </div>

          {/* Waking-up banner */}
          {waking && (
            <div style={{
              background: 'rgba(212, 175, 55, 0.1)',
              border: '1px solid rgba(212, 175, 55, 0.4)',
              borderRadius: 6,
              padding: '10px 14px',
              marginBottom: 12,
              fontSize: 13,
              color: 'var(--gold)',
              display: 'flex',
              alignItems: 'center',
              gap: 8,
            }}>
              <span className="spinner" style={{ width: 14, height: 14, flexShrink: 0 }} />
              Server is waking up, please wait… (Render free tier may take ~30 seconds)
            </div>
          )}

          {/* Error message */}
          {error && (
            <p style={{ color: 'var(--danger)', fontSize: 13, marginBottom: 12 }}>{error}</p>
          )}

          <button
            className="btn btn-primary"
            type="submit"
            disabled={isDisabled}
            style={{ width: '100%', justifyContent: 'center' }}
          >
            {isDisabled ? <span className="spinner" /> : 'Sign In'}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: 20, fontSize: 13, color: 'var(--text-muted)' }}>
          Don’t have an account? <a href="/register" style={{ color: 'var(--gold)', fontWeight: 500 }}>Create one</a>
        </p>
      </div>
    </div>
  );
}
