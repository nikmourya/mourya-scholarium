'use client';
import { useRouter } from 'next/navigation';
import styles from './page.module.css';

export default function LandingPage() {
  const router = useRouter();

  return (
    <div className={styles.landing}>
      {/* Hero */}
      <header className={styles.hero}>
        <div className={styles.heroInner}>
          <div className={styles.brand}>
            <div className={styles.logo}>
              <span className={styles.logoMark}>MS</span>
            </div>
            <h1 className={styles.title}>Mourya Scholarium</h1>
            <p className={styles.tagline}>Your Portal to Advanced Research, Learning, and Academic Excellence</p>
          </div>
          <p className={styles.subtitle}>
            A premium scholar-first academic writing and research intelligence platform.
            Citation-grounded. Style-adapted. Source-verified.
          </p>
          <div className={styles.ctas}>
            <button className="btn btn-primary btn-lg" onClick={() => router.push('/register')}>
              Start Writing
            </button>
            <button className="btn btn-ghost btn-lg" onClick={() => router.push('/login')}>
              Sign In
            </button>
          </div>
        </div>
      </header>

      {/* Features */}
      <section className={styles.features}>
        <div className={styles.featureGrid}>
          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>📚</div>
            <h3>Source-Grounded</h3>
            <p>Every claim is backed by real peer-reviewed scholarly sources. No fabricated citations, ever.</p>
          </div>
          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>✍️</div>
            <h3>Style-Adapted</h3>
            <p>Writing that matches your English level and preserves your academic voice while improving quality.</p>
          </div>
          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>🔬</div>
            <h3>Integrity-First</h3>
            <p>Every output passes integrity checks. Evidence traces are visible. Sources are verifiable.</p>
          </div>
        </div>
      </section>

      {/* Modes */}
      <section className={styles.modes}>
        <h2>Writing Modes</h2>
        <div className={styles.modeGrid}>
          {['Write from Prompt', 'Literature Review', 'Rewrite & Polish', 'Methodology', 'Results to Prose', 'Research Proposal'].map(m => (
            <div key={m} className={styles.modeChip}>{m}</div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className={styles.footer}>
        <p>© 2026 Mourya Scholarium. Built for scholars, by scholars.</p>
      </footer>
    </div>
  );
}
