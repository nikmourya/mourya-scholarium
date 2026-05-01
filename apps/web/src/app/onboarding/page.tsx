'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import useStore from '@/store/useStore';

const STEPS = [
  { key: 'english_level', label: 'What is your English writing level?', options: ['beginner', 'intermediate', 'advanced', 'publication_ready'], display: ['Beginner', 'Intermediate', 'Advanced', 'Publication-Ready'] },
  { key: 'academic_level', label: 'What is your current academic level?', options: ['undergraduate', 'postgraduate', 'phd', 'professional', 'faculty'], display: ['Undergraduate', 'Postgraduate', 'PhD Scholar', 'Research Professional', 'Faculty / Author'] },
  { key: 'writing_type_needed', label: 'What type of writing do you need most?', options: ['literature_review', 'introduction', 'methodology', 'results', 'abstract', 'thesis_chapter', 'rewrite', 'summary', 'proposal', 'bibliography'], display: ['Literature Review', 'Introduction', 'Methodology', 'Results & Discussion', 'Abstract', 'Thesis Chapter', 'Rewrite/Polish', 'Citation-backed Summary', 'Research Proposal', 'Annotated Bibliography'] },
  { key: 'writing_style', label: 'What writing style do you want?', options: ['simple_academic', 'standard_academic', 'high_impact_journal', 'thesis_dissertation', 'supervisor_ready'], display: ['Simple Academic English', 'Standard Academic English', 'High-Impact Journal Style', 'Thesis/Dissertation Style', 'Supervisor-Ready Draft'] },
  { key: 'target_output_level', label: 'Output level target?', options: ['match_current', 'elevate_slightly', 'publication_ready'], display: ['Close to my current level', 'Slightly elevated', 'Publication-ready'] },
];

export default function OnboardingPage() {
  const router = useRouter();
  const saveProfile = useStore(s => s.saveProfile);
  const uploadStyleSample = useStore(s => s.uploadStyleSample);
  const [step, setStep] = useState(0);
  const [data, setData] = useState<any>({
    english_level: '', academic_level: '', discipline: '', citation_style: 'APA7',
    academic_only_sources: true, target_output_level: 'match_current', writing_type_needed: '',
    writing_style: '', preservation_priorities: [], improvement_targets: [],
  });
  const [sample, setSample] = useState('');
  const [loading, setLoading] = useState(false);

  const TOTAL = STEPS.length + 3; // +discipline, +sample, +improvement

  const handleSelect = (key: string, val: string) => {
    setData({ ...data, [key]: val });
    setStep(step + 1);
  };

  const handleMultiToggle = (key: string, val: string) => {
    const arr = data[key] || [];
    setData({ ...data, [key]: arr.includes(val) ? arr.filter((v: string) => v !== val) : [...arr, val] });
  };

  const handleFinish = async () => {
    setLoading(true);
    try {
      await saveProfile(data);
      if (sample.trim().length > 50) {
        await uploadStyleSample(sample);
      }
      router.push('/dashboard');
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-center" style={{ background: 'var(--ivory)' }}>
      <div className="card" style={{ width: '100%', maxWidth: 560 }}>
        {/* Progress */}
        <div style={{ marginBottom: 28 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, color: 'var(--text-muted)', marginBottom: 8 }}>
            <span>Step {step + 1} of {TOTAL}</span>
            <span>{Math.round(((step + 1) / TOTAL) * 100)}%</span>
          </div>
          <div style={{ height: 4, background: 'var(--ivory-dark)', borderRadius: 2 }}>
            <div style={{ height: '100%', width: `${((step + 1) / TOTAL) * 100}%`, background: 'var(--gold)', borderRadius: 2, transition: 'width 0.3s' }} />
          </div>
        </div>

        {/* Step content */}
        {step < STEPS.length && (
          <div>
            <h3 style={{ marginBottom: 20 }}>{STEPS[step].label}</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {STEPS[step].options.map((opt, i) => (
                <button key={opt} className="btn btn-ghost" onClick={() => handleSelect(STEPS[step].key, opt)}
                  style={{ justifyContent: 'flex-start', background: data[STEPS[step].key] === opt ? 'var(--gold-dim)' : undefined,
                    borderColor: data[STEPS[step].key] === opt ? 'var(--gold)' : undefined }}>
                  {STEPS[step].display[i]}
                </button>
              ))}
            </div>
          </div>
        )}

        {step === STEPS.length && (
          <div>
            <h3 style={{ marginBottom: 12 }}>What is your discipline / field?</h3>
            <input className="input" value={data.discipline} onChange={e => setData({ ...data, discipline: e.target.value })} placeholder="e.g., Environmental Science, Geography, GIS" />
            <button className="btn btn-primary" style={{ marginTop: 16, width: '100%', justifyContent: 'center' }} onClick={() => setStep(step + 1)}>Continue</button>
          </div>
        )}

        {step === STEPS.length + 1 && (
          <div>
            <h3 style={{ marginBottom: 8 }}>Paste a writing sample (optional)</h3>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 12 }}>100–500 words of your own academic writing helps us match your style.</p>
            <textarea className="textarea" value={sample} onChange={e => setSample(e.target.value)} rows={8} placeholder="Paste your writing sample here..." />
            <button className="btn btn-primary" style={{ marginTop: 12, width: '100%', justifyContent: 'center' }} onClick={() => setStep(step + 1)}>
              {sample.trim() ? 'Continue' : 'Skip'}
            </button>
          </div>
        )}

        {step === STEPS.length + 2 && (
          <div>
            <h3 style={{ marginBottom: 12 }}>What should we improve?</h3>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {['grammar', 'coherence', 'tone', 'conciseness', 'academic_language', 'transitions', 'citation_support', 'clarity', 'argument_quality'].map(t => (
                <button key={t} className="btn btn-sm" onClick={() => handleMultiToggle('improvement_targets', t)}
                  style={{ background: (data.improvement_targets || []).includes(t) ? 'var(--gold)' : 'var(--white)',
                    color: (data.improvement_targets || []).includes(t) ? 'var(--navy)' : 'var(--text)',
                    border: '1px solid var(--ivory-dark)' }}>
                  {t.replace(/_/g, ' ')}
                </button>
              ))}
            </div>
            <button className="btn btn-primary btn-lg" style={{ marginTop: 24, width: '100%', justifyContent: 'center' }}
              onClick={handleFinish} disabled={loading}>
              {loading ? <span className="spinner" /> : 'Complete Setup & Enter Studio'}
            </button>
          </div>
        )}

        {/* Back button */}
        {step > 0 && step <= TOTAL && (
          <button className="btn btn-ghost btn-sm" style={{ marginTop: 16 }} onClick={() => setStep(step - 1)}>← Back</button>
        )}
      </div>
    </div>
  );
}
