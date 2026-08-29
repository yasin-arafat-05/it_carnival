import { Link } from 'react-router-dom';
import { Logo } from '../components/Brand/Logo';
import './PlaceholderPage.css';

interface PlaceholderPageProps {
  title: string;
  description?: string;
}

/**
 * Temporary stand-in for a screen that hasn't been built yet.
 * Feature 41 only wires up routing; Login/Register/Dashboard/Profile get
 * their real UI in later tasks.
 */
export function PlaceholderPage({ title, description }: PlaceholderPageProps) {
  return (
    <main className="placeholder-page">
      <div className="placeholder-page__card">
        <Logo size={40} />
        <h1 className="placeholder-page__title">{title}</h1>
        {description && <p className="placeholder-page__description">{description}</p>}
        <Link className="placeholder-page__link" to="/">
          Back to start
        </Link>
      </div>
    </main>
  );
}
