'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import useStore, { wakeUpServer } from '@/store/useStore';

export default function RegisterPage() {
  const router = useRouter();
  const register = useStore(s => s.register);
  const [form, setForm] = useState({ name: '', email: '', password: '', institution: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [waking, setWaking] = useState(false);

  const update = (k: string, v: string) => setForm({ ...form, [k]: v });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setWaking(false);

    try {
      // Ping the server first so Render free-tier has a chance to wake up
      // before the actual register request is made.
      await wakeUpServer(() => {
        // Called on first failed ping — update UI to inform the user
        setWaking(true);
      });
      setWaking(false);

      await register(form.email, form.name, form.password, form.institution || undefined);
      router.push('/onboarding');
    } catch (err: any) {
      setWaking(false);
      // Surface the friendly message from wakeUpServer / apiFetch
      setError(err.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const isDisabled = loading || waking;

  return (
    <div className="page-center" style={{ background: 'linear-gradient(135deg, #0A1628 0%, #1A2A42 100%)' }}>
      <div className="card" style={{ width: '100%', maxWidth: 460 }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <h2>Create Your Account</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: 14, marginTop: 4 }}>Join Mourya Scholarium</p>
        </div>
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 14 }}>
            <label className="label">Full Name</label>
            <input className="input" value={form.name} onChange={e => update('name', e.target.value)} required placeholder="Dr. Priya Sharma" />
          </div>
          <div style={{ marginBottom: 14 }}>
            <label className="label">Email</label>
            <input className="input" type="email" value={form.email} onChange={e => update('email', e.target.value)} required placeholder="priya@university.edu" />
          </div>
          <div style={{ marginBottom: 14 }}>
            <label className="label">Password</label>
            <input className="input" type="password" value={form.password} onChange={e => update('password', e.target.value)} required minLength={8} placeholder="Min. 8 characters" />
          </div>
          <div style={{ marginBottom: 20 }}>
            <label className="label">Institution (optional)</label>
            <input className="input" value={form.institution} onChange={e => update('institution', e.target.value)} placeholder="University of Delhi" />
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
            {isDisabled ? <span className="spinner" /> : 'Create Account'}
          </button>
        </form>
        <p style={{ textAlign: 'center', marginTop: 20, fontSize: 13, color: 'var(--text-muted)' }}>
          Already have an account? <a href="/login" style={{ color: 'var(--gold)', fontWeight: 500 }}>Sign In</a>
        </p>
      </div>
    </div>
  );
}
