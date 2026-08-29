import type { ReactNode } from 'react';
import { Logo } from '../components/Brand/Logo';
import './AuthLayout.css';

interface AuthLayoutProps {
  title: string;
  description?: string;
  children: ReactNode;
  footer?: ReactNode;
}

/**
 * Shared shell for auth screens (Login, Register): centered card, logo,
 * heading, and a footer slot for "switch to the other auth screen" links.
 * Full-viewport, mobile-first, no horizontal scroll.
 */
export function AuthLayout({ title, description, children, footer }: AuthLayoutProps) {
  return (
    <main className="auth-layout">
      <div className="auth-layout__card">
        <div className="auth-layout__brand">
          <Logo size={44} withWordmark={false} />
        </div>
        <div className="auth-layout__heading">
          <h1 className="auth-layout__title">{title}</h1>
          {description && <p className="auth-layout__description">{description}</p>}
        </div>
        {children}
        {footer && <div className="auth-layout__footer">{footer}</div>}
      </div>
    </main>
  );
}
