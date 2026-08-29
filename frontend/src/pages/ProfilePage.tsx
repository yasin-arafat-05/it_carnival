import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/Button/Button';
import { Logo } from '../components/Brand/Logo';
import { StatusBadge } from '../components/StatusBadge/StatusBadge';
import { Toggle } from '../components/Toggle/Toggle';
import { MOCK_USER } from '../data/mockAuth';
import './ProfilePage.css';

function formatCreatedDate(value?: string): string {
  if (!value) return '—';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
}

/**
 * Feature 4/54 — Profile & Settings.
 *
 * Reads from the same `MOCK_USER` used by the mock auth service — no
 * second user-data system. Everything here is read-only display plus
 * local, non-persistent UI toggles; "Log out" only navigates to /login
 * as a mock action, it does not touch any real session state.
 */
export function ProfilePage() {
  const navigate = useNavigate();
  const user = MOCK_USER;

  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [darkModeEnabled, setDarkModeEnabled] = useState(false);

  const status = user.accountStatus ?? 'active';

  function handleLogout() {
    navigate('/login', { replace: true });
  }

  return (
    <main className="profile-page">
      <div className="profile-page__container">
        <header className="profile-page__header">
          <Logo size={40} withWordmark={false} />
          <h1 className="profile-page__title">Profile &amp; settings</h1>
        </header>

        <section className="profile-section" aria-labelledby="profile-info-heading">
          <div className="profile-section__heading">
            <h2 id="profile-info-heading" className="profile-section__title">
              Your information
            </h2>
            <StatusBadge status={status} />
          </div>

          <dl className="profile-info-list">
            <div className="profile-info-list__row">
              <dt>Full name</dt>
              <dd>{user.name}</dd>
            </div>
            <div className="profile-info-list__row">
              <dt>Username</dt>
              <dd>{user.username}</dd>
            </div>
            <div className="profile-info-list__row">
              <dt>Email</dt>
              <dd>{user.email}</dd>
            </div>
            <div className="profile-info-list__row">
              <dt>Phone</dt>
              <dd>{user.phone ?? '—'}</dd>
            </div>
            <div className="profile-info-list__row">
              <dt>Account created</dt>
              <dd>{formatCreatedDate(user.createdAt)}</dd>
            </div>
          </dl>
        </section>

        <section className="profile-section" aria-labelledby="settings-heading">
          <h2 id="settings-heading" className="profile-section__title">
            Settings
          </h2>

          <div className="profile-settings-list">
            <Toggle
              label="Notifications"
              description="Get alerts about account activity."
              checked={notificationsEnabled}
              onChange={setNotificationsEnabled}
            />
            <Toggle
              label="Dark appearance"
              description="Switch to a darker color theme."
              checked={darkModeEnabled}
              onChange={setDarkModeEnabled}
            />
          </div>

          <Button variant="secondary" fullWidth onClick={handleLogout}>
            Log out
          </Button>
        </section>
      </div>
    </main>
  );
}
