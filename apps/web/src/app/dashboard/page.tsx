'use client';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import useStore from '@/store/useStore';

export default function DashboardPage() {
  const router = useRouter();
  const user = useStore(s => s.user);
  const projects = useStore(s => s.projects);
  const loadProjects = useStore(s => s.loadProjects);
  const createProject = useStore(s => s.createProject);
  const logout = useStore(s => s.logout);

  useEffect(() => {
    if (!user) { router.push('/login'); return; }
    loadProjects();
  }, [user]);

  if (!user) return null;

  return (
    <div style={{ minHeight: '100vh', background: 'var(--ivory)' }}>
      {/* Top Bar */}
      <header style={{ background: 'var(--navy)', color: 'var(--ivory)', padding: '12px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <span style={{ fontFamily: 'var(--font-display)', fontSize: 18, color: 'var(--gold)', fontWeight: 700 }}>MS</span>
          <span style={{ fontFamily: 'var(--font-display)', fontSize: 16 }}>Mourya Scholarium</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <span style={{ fontSize: 13 }}>{user.name}</span>
          <button className="btn btn-ghost btn-sm" style={{ color: 'var(--ivory)', borderColor: 'rgba(245,240,232,0.2)' }} onClick={logout}>Sign Out</button>
        </div>
      </header>

      <div className="container" style={{ paddingTop: 40, paddingBottom: 60 }}>
        {/* Welcome */}
        <div style={{ marginBottom: 36 }}>
          <h1 style={{ marginBottom: 4 }}>Welcome, {user.name.split(' ')[0]}</h1>
          <p style={{ color: 'var(--text-muted)' }}>Your academic writing workspace is ready.</p>
        </div>

        {/* Quick Actions */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16, marginBottom: 40 }}>
          <button className="card" style={{ cursor: 'pointer', textAlign: 'center', border: '2px solid transparent' }}
            onClick={() => router.push('/studio')}
            onMouseEnter={e => (e.currentTarget.style.borderColor = 'var(--gold)')}
            onMouseLeave={e => (e.currentTarget.style.borderColor = 'transparent')}>
            <div style={{ fontSize: 32, marginBottom: 8 }}>✍️</div>
            <h3 style={{ fontSize: 16 }}>New Writing Session</h3>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 4 }}>Start writing with AI assistance</p>
          </button>

          <button className="card" style={{ cursor: 'pointer', textAlign: 'center', border: '2px solid transparent' }}
            onClick={async () => { const t = prompt('Project title:'); if (t) await createProject(t); }}>
            <div style={{ fontSize: 32, marginBottom: 8 }}>📁</div>
            <h3 style={{ fontSize: 16 }}>New Project</h3>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 4 }}>Organize your academic work</p>
          </button>

          <button className="card" style={{ cursor: 'pointer', textAlign: 'center', border: '2px solid transparent' }}
            onClick={() => router.push('/onboarding')}>
            <div style={{ fontSize: 32, marginBottom: 8 }}>⚙️</div>
            <h3 style={{ fontSize: 16 }}>Update Profile</h3>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 4 }}>Adjust writing preferences</p>
          </button>
        </div>

        {/* Projects List */}
        <h2 style={{ marginBottom: 16 }}>Your Projects</h2>
        {projects.length === 0 ? (
          <div className="card" style={{ textAlign: 'center', color: 'var(--text-muted)', padding: 40 }}>
            <p>No projects yet. Create one to organize your writing sessions.</p>
          </div>
        ) : (
          <div style={{ display: 'grid', gap: 12 }}>
            {projects.map((p: any) => (
              <div key={p.id} className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }}
                onClick={() => router.push('/studio')}>
                <div>
                  <h3 style={{ fontSize: 15, marginBottom: 2 }}>{p.title}</h3>
                  <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>{p.project_type || 'General'} · {p.status}</p>
                </div>
                <span style={{ fontSize: 12, color: 'var(--text-light)' }}>{p.created_at ? new Date(p.created_at).toLocaleDateString() : ''}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
