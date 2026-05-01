import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Mourya Scholarium — Academic Intelligence Platform',
  description: 'Your Portal to Advanced Research, Learning, and Academic Excellence. A premium scholar-first academic writing and research intelligence platform.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
