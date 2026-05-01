'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import useStore from '@/store/useStore';
import styles from './studio.module.css';

const MODES = [
  { value: 'write_from_prompt', label: '✍️ Write from Prompt', enabled: true },
  { value: 'rewrite', label: '✨ Rewrite / Polish', enabled: true },
  { value: 'literature_review', label: '📚 Literature Review', enabled: true },
  { value: 'introduction', label: '📝 Introduction', enabled: true },
  { value: 'methodology', label: '🔬 Methodology', enabled: false },
  { value: 'results_to_prose', label: '📊 Results to Prose', enabled: false },
  { value: 'abstract', label: '📄 Abstract', enabled: false },
  { value: 'research_proposal', label: '🎯 Research Proposal', enabled: false },
];

export default function StudioPage() {
  const router = useRouter();
  const user = useStore(s => s.user);
  const currentResult = useStore(s => s.currentResult);
  const isGenerating = useStore(s => s.isGenerating);
  const submitWriteRequest = useStore(s => s.submitWriteRequest);
  const submitFeedback = useStore(s => s.submitFeedback);
  const logout = useStore(s => s.logout);

  const [mode, setMode] = useState('write_from_prompt');
  const [prompt, setPrompt] = useState('');
  const [inputText, setInputText] = useState('');
  const [rightPanel, setRightPanel] = useState<'sources' | 'evidence' | 'bibliography' | 'integrity'>('sources');
  const [mobilePanel, setMobilePanel] = useState<string | null>(null);

  useEffect(() => { if (!user) router.push('/login'); }, [user]);
  if (!user) return null;

  const handleGenerate = async () => {
    if (!prompt.trim()) return;
    await submitWriteRequest({
      writing_mode: mode,
      prompt: prompt.trim(),
      input_text: mode === 'rewrite' ? inputText : undefined,
      review_type: mode === 'literature_review' ? 'narrative' : undefined,
    });
  };

  const r = currentResult;

  return (
    <div className={styles.studio}>
      {/* Top Bar */}
      <header className={styles.topbar}>
        <div className={styles.topbarLeft}>
          <span className={styles.brandMark}>MS</span>
          <span className={styles.brandName}>Writing Studio</span>
        </div>
        <div className={styles.topbarRight}>
          <button className="btn btn-ghost btn-sm" onClick={() => router.push('/dashboard')}>Dashboard</button>
          <span style={{ fontSize: 13 }}>{user.name}</span>
          <button className="btn btn-ghost btn-sm" onClick={logout}>Sign Out</button>
        </div>
      </header>

      <div className={styles.workspace}>
        {/* Left Panel — Mode Selector */}
        <aside className={styles.leftPanel}>
          <h3 className={styles.panelTitle}>Writing Mode</h3>
          {MODES.map(m => (
            <button key={m.value} disabled={!m.enabled}
              className={`${styles.modeBtn} ${mode === m.value ? styles.modeBtnActive : ''}`}
              onClick={() => { setMode(m.value); setPrompt(''); setInputText(''); }}>
              {m.label}
              {!m.enabled && <span className={styles.comingSoon}>Soon</span>}
            </button>
          ))}
          <div className={styles.panelDivider} />
          <div className={styles.statsBox}>
            {r && <>
              <div className={styles.stat}><span>Words</span><strong>{r.word_count}</strong></div>
              <div className={styles.stat}><span>Sources</span><strong>{r.sources.length}</strong></div>
              <div className={styles.stat}><span>Citations</span><strong>{r.bibliography.length}</strong></div>
              <div className={styles.stat}>
                <span>Integrity</span>
                <span className={`badge ${r.integrity_status === 'pass' ? 'badge-pass' : r.integrity_status === 'warning' ? 'badge-warning' : 'badge-fail'}`}>
                  {r.integrity_status}
                </span>
              </div>
            </>}
          </div>
        </aside>

        {/* Center — Editor */}
        <main className={styles.center}>
          <div className={styles.promptArea}>
            <label className="label" style={{ fontSize: 14 }}>
              {mode === 'rewrite' ? 'Instructions for rewriting:' : mode === 'literature_review' ? 'Literature review topic:' : 'Your writing prompt:'}
            </label>
            <textarea className="textarea" value={prompt} onChange={e => setPrompt(e.target.value)}
              placeholder={mode === 'literature_review' ? 'e.g., Write a narrative literature review on remote sensing applications in wetland monitoring...' : mode === 'rewrite' ? 'e.g., Improve the coherence and academic tone of this text...' : mode === 'introduction' ? 'Write an introduction for a study on wetland loss due to urbanization using remote sensing.' : 'e.g., Write an introduction section about the role of GIS in urban green space monitoring...'}
              rows={3} />

            {mode === 'rewrite' && (
              <>
                <label className="label" style={{ marginTop: 12 }}>Text to rewrite:</label>
                <textarea className="textarea body-serif" value={inputText} onChange={e => setInputText(e.target.value)}
                  placeholder="Paste your text here..." rows={6} />
              </>
            )}

            <div className={styles.generateBar}>
              <button className="btn btn-primary btn-lg" onClick={handleGenerate}
                disabled={isGenerating || !prompt.trim()}>
                {isGenerating ? <><span className="spinner" /> Generating...</> : '⚡ Generate'}
              </button>
            </div>
          </div>

          {/* Output */}
          {r && (
            <div className={styles.outputArea}>
              <div className={styles.outputHeader}>
                <h3>Generated Output</h3>
                <div className={styles.outputActions}>
                  <button className="btn btn-sm btn-primary" onClick={() => submitFeedback(r.session_id, 'accept')}>✅ Accept</button>
                  <button className="btn btn-sm btn-ghost" onClick={() => submitFeedback(r.session_id, 'edit')}>✏️ Edit</button>
                  <button className="btn btn-sm btn-ghost" onClick={() => { submitFeedback(r.session_id, 'reject'); }}>❌ Reject</button>
                </div>
              </div>
              <div className={styles.outputText + ' body-serif'}>
                {r.text.split('\n').map((line, i) => (
                  <p key={i} style={{ marginBottom: line.trim() ? 12 : 0 }}>{line}</p>
                ))}
              </div>
            </div>
          )}

          {isGenerating && (
            <div className={styles.generatingOverlay}>
              <span className="spinner" style={{ width: 40, height: 40 }} />
              <p style={{ marginTop: 16, color: 'var(--text-muted)' }}>Retrieving sources and generating academic text...</p>
            </div>
          )}
        </main>

        {/* Right Panel — Sources / Evidence / Bibliography / Integrity */}
        <aside className={styles.rightPanel}>
          <div className={styles.panelTabs}>
            {(['sources', 'evidence', 'bibliography', 'integrity'] as const).map(tab => (
              <button key={tab} className={`${styles.panelTab} ${rightPanel === tab ? styles.panelTabActive : ''}`}
                onClick={() => setRightPanel(tab)}>
                {tab === 'sources' ? '📄' : tab === 'evidence' ? '🔗' : tab === 'bibliography' ? '📖' : '🛡️'} {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>

          <div className={styles.panelContent}>
            {rightPanel === 'sources' && r && (
              <div>
                <h4 className={styles.panelSubtitle}>{r.sources.length} Sources Found</h4>
                {r.sources.slice(0, 15).map((s: any, i: number) => (
                  <div key={i} className={styles.sourceCard}>
                    <div className={styles.sourceTitle}>{s.title}</div>
                    <div className={styles.sourceMeta}>
                      {s.authors?.[0]?.name || 'Unknown'} {s.authors?.length > 1 ? 'et al.' : ''} ({s.year || 'n.d.'})
                    </div>
                    {s.journal && <div className={styles.sourceJournal}>{s.journal}</div>}
                    <div className={styles.trustRow}>
                      <span style={{ fontSize: 11 }}>Trust:</span>
                      <div className="trust-bar" style={{ flex: 1 }}>
                        <div className={`trust-bar-fill ${(s.trust_score || 0.5) > 0.7 ? 'trust-high' : (s.trust_score || 0.5) > 0.4 ? 'trust-medium' : 'trust-low'}`}
                          style={{ width: `${(s.trust_score || 0.5) * 100}%` }} />
                      </div>
                      <span style={{ fontSize: 11 }}>{Math.round((s.trust_score || 0.5) * 100)}%</span>
                    </div>
                    {s.doi && <a href={`https://doi.org/${s.doi}`} target="_blank" rel="noopener" className={styles.doiLink}>DOI ↗</a>}
                  </div>
                ))}
                {!r && <p style={{ color: 'var(--text-muted)', fontSize: 13, padding: 16 }}>Generate text to see sources</p>}
              </div>
            )}

            {rightPanel === 'bibliography' && r && (
              <div>
                <h4 className={styles.panelSubtitle}>APA 7th Bibliography</h4>
                {r.bibliography.map((ref: string, i: number) => (
                  <p key={i} className={styles.refEntry}>{ref}</p>
                ))}
                {r.bibliography.length === 0 && <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>No references generated</p>}
              </div>
            )}

            {rightPanel === 'evidence' && r && (
              <div>
                <h4 className={styles.panelSubtitle}>Evidence Traces</h4>
                {r.evidence_traces.map((t: any, i: number) => (
                  <div key={i} className={styles.evidenceCard}>
                    <p className={styles.evidenceClaim}>"{t.claim_text?.substring(0, 150)}..."</p>
                    <span className={`badge ${t.verification_status === 'auto_verified' ? 'badge-pass' : 'badge-warning'}`}>
                      {t.verification_status}
                    </span>
                  </div>
                ))}
                {r.evidence_traces.length === 0 && <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>No evidence traces</p>}
              </div>
            )}

            {rightPanel === 'integrity' && r && (
              <div>
                <h4 className={styles.panelSubtitle}>Integrity Report</h4>
                <div className={styles.integrityStatus}>
                  <span className={`badge ${r.integrity_status === 'pass' ? 'badge-pass' : r.integrity_status === 'warning' ? 'badge-warning' : 'badge-fail'}`}>
                    {r.integrity_status?.toUpperCase()}
                  </span>
                  <span style={{ fontSize: 13 }}>Confidence: {Math.round((r.integrity_report?.confidence_score || 0) * 100)}%</span>
                </div>
                {r.integrity_report?.unsupported_claims?.length > 0 && (
                  <div style={{ marginTop: 12 }}>
                    <strong style={{ fontSize: 13 }}>Unsupported Claims:</strong>
                    {r.integrity_report.unsupported_claims.map((c: any, i: number) => (
                      <p key={i} style={{ fontSize: 12, color: 'var(--burgundy)', marginTop: 4 }}>⚠️ {c.claim_text?.substring(0, 100)}...</p>
                    ))}
                  </div>
                )}
                {r.integrity_report?.recommendations?.length > 0 && (
                  <div style={{ marginTop: 12 }}>
                    <strong style={{ fontSize: 13 }}>Recommendations:</strong>
                    {r.integrity_report.recommendations.map((rec: string, i: number) => (
                      <p key={i} style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>💡 {rec}</p>
                    ))}
                  </div>
                )}
              </div>
            )}

            {!r && <p style={{ color: 'var(--text-muted)', fontSize: 13, padding: 20 }}>Generate text to see {rightPanel}</p>}
          </div>
        </aside>
      </div>

      {/* Mobile Bottom Tabs */}
      <nav className={styles.mobileNav}>
        <button onClick={() => setMobilePanel(mobilePanel === 'sources' ? null : 'sources')}>📄 Sources</button>
        <button onClick={() => setMobilePanel(mobilePanel === 'bibliography' ? null : 'bibliography')}>📖 Refs</button>
        <button onClick={() => setMobilePanel(mobilePanel === 'integrity' ? null : 'integrity')}>🛡️ Integrity</button>
      </nav>
    </div>
  );
}
