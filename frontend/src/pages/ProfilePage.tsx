import { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from '../components/Button/Button';
import { Logo } from '../components/Brand/Logo';
import { StatusBadge } from '../components/StatusBadge/StatusBadge';
import { Toggle } from '../components/Toggle/Toggle';
import { apiFetch } from '../config/api';
import { authService } from '../services/authService';
import './ProfilePage.css';

function formatCreatedDate(value?: string): string {
  if (!value) return '—';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
}

export function ProfilePage() {
  const navigate = useNavigate();
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [darkModeEnabled, setDarkModeEnabled] = useState(false);

  useEffect(() => {
    apiFetch<any>('/users/me')
      .then((data) => {
        setUser({
          name: data.full_name,
          username: data.username,
          email: data.email,
          phone: data.phone_number,
          role: data.role || 'USER',
          accountStatus: (data.account_status || 'ACTIVE').toLowerCase(),
          createdAt: data.created_at,
          account: data.account,
        });
      })
      .catch(() => {
        authService.logout();
        navigate('/login', { replace: true });
      })
      .finally(() => setLoading(false));
  }, [navigate]);

  function handleLogout() {
    authService.logout();
    navigate('/login', { replace: true });
  }

  if (loading) {
    return (
      <main className="profile-page">
        <div className="profile-page__container">
          <p>Loading profile...</p>
        </div>
      </main>
    );
  }

  const status = user?.accountStatus ?? 'active';

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
              <dd>{user?.name}</dd>
            </div>
            <div className="profile-info-list__row">
              <dt>Username</dt>
              <dd>{user?.username}</dd>
            </div>
            <div className="profile-info-list__row">
              <dt>Role</dt>
              <dd style={{ fontWeight: 'bold', color: 'var(--color-primary)' }}>{user?.role}</dd>
            </div>
            <div className="profile-info-list__row">
              <dt>Email</dt>
              <dd>{user?.email}</dd>
            </div>
            <div className="profile-info-list__row">
              <dt>Phone</dt>
              <dd>{user?.phone ?? '—'}</dd>
            </div>
            <div className="profile-info-list__row">
              <dt>Account Number</dt>
              <dd>{user?.account?.account_number ?? '—'}</dd>
            </div>
            <div className="profile-info-list__row">
              <dt>Account created</dt>
              <dd>{formatCreatedDate(user?.createdAt)}</dd>
            </div>
          </dl>

          {user?.role === 'ADMIN' && (
            <Link
              to="/admin/dashboard"
              className="button button--primary"
              style={{ width: '100%', textAlign: 'center', marginTop: '1rem' }}
            >
              Open Admin Control Center
            </Link>
          )}
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
