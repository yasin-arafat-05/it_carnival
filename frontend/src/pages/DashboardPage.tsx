import { useCallback, useEffect, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { BalanceCard, BalanceCardSkeleton } from '../components/BalanceCard/BalanceCard';
import { Button } from '../components/Button/Button';
import '../components/Button/Button.css';
import { ErrorMessage } from '../components/ErrorMessage/ErrorMessage';
import { Logo } from '../components/Brand/Logo';
import { TransactionRow, TransactionRowSkeleton } from '../components/TransactionRow/TransactionRow';
import { dashboardService } from '../services/dashboardService';
import { notificationService } from '../services/notificationService';
import type { NotificationItem } from '../services/notificationService';
import type { DashboardData } from '../types/dashboard';
import './DashboardPage.css';

function getFirstName(fullName: string): string {
  return fullName.trim().split(/\s+/)[0] ?? fullName;
}

export function DashboardPage() {
  const navigate = useNavigate();
  const [data, setData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Notification Drawer State
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [showNotifications, setShowNotifications] = useState(false);

  const isMounted = useRef(true);

  const loadDashboard = useCallback(() => {
    setIsLoading(true);
    setError(null);

    dashboardService
      .getDashboardData()
      .then((result) => {
        if (!isMounted.current) return;
        if (result.user.role === 'ADMIN') {
          navigate('/admin/dashboard', { replace: true });
          return;
        }
        setData(result);
      })
      .catch((err: unknown) => {
        if (!isMounted.current) return;
        const message = err instanceof Error ? err.message : "Couldn't load balance";
        setError(message);
      })
      .finally(() => {
        if (!isMounted.current) return;
        setIsLoading(false);
      });
  }, []);

  const loadNotifications = useCallback(() => {
    notificationService
      .getNotifications()
      .then((list) => {
        if (!isMounted.current) return;
        setNotifications(list);
      })
      .catch(console.error);
  }, []);

  useEffect(() => {
    isMounted.current = true;
    loadDashboard();
    loadNotifications();
    return () => {
      isMounted.current = false;
    };
  }, [loadDashboard, loadNotifications]);

  const handleMarkAllRead = async () => {
    try {
      await notificationService.markAllAsRead();
      loadNotifications();
    } catch (err) {
      console.error(err);
    }
  };

  const unreadCount = notifications.filter((n) => !n.is_read).length;
  const recentTransactions = data?.transactions.slice(0, 5) ?? [];

  return (
    <main className="dashboard-page">
      <div className="dashboard-page__container" style={{ position: 'relative' }}>
        <header className="dashboard-header">
          <div className="dashboard-header__brand">
            <Logo size={36} withWordmark={false} />
            <h1 className="dashboard-header__greeting">
              {isLoading && !data
                ? 'Welcome back'
                : `Hi, ${data ? getFirstName(data.user.name) : 'there'}`}
            </h1>
          </div>
          
          <div className="dashboard-header__actions">
            <button
              className="notification-bell-btn"
              onClick={() => setShowNotifications(!showNotifications)}
              title="Notifications"
            >
              🔔
              {unreadCount > 0 && <span className="notification-badge">{unreadCount}</span>}
            </button>

            <Link
              to="/profile"
              className="dashboard-header__profile-link"
              aria-label="Go to your profile"
            >
              {data ? getFirstName(data.user.name).charAt(0).toUpperCase() : '·'}
            </Link>
          </div>
        </header>

        {showNotifications && (
          <div className="notification-dropdown">
            <div className="notification-dropdown__header">
              <span className="notification-dropdown__title">Notifications</span>
              {unreadCount > 0 && (
                <button className="read-all-btn" onClick={handleMarkAllRead}>
                  Mark all read
                </button>
              )}
            </div>

            <div className="notification-list">
              {notifications.length === 0 ? (
                <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>No notifications yet.</p>
              ) : (
                notifications.map((notif) => (
                  <div
                    key={notif.id}
                    className={`notification-card ${!notif.is_read ? 'unread' : ''}`}
                    onClick={() => {
                      if (!notif.is_read) {
                        notificationService.markAsRead(notif.id).then(loadNotifications);
                      }
                    }}
                  >
                    <span className="notification-card__title">{notif.title}</span>
                    <span className="notification-card__message">{notif.message}</span>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {error && !isLoading ? (
          <section className="dashboard-section" aria-labelledby="balance-error-heading">
            <h2 id="balance-error-heading" className="dashboard-section__title">
              Available balance
            </h2>
            <ErrorMessage message={error} />
            <Button variant="secondary" onClick={loadDashboard}>
              Retry
            </Button>
          </section>
        ) : isLoading || !data ? (
          <BalanceCardSkeleton />
        ) : (
          <BalanceCard balance={data.balance} currency={data.currency} />
        )}

        <div className="dashboard-actions">
          <Link to="/send" className="button button--primary dashboard-actions__link">
            Send money
          </Link>
          <Link to="/request" className="button button--secondary dashboard-actions__link">
            Request money
          </Link>
        </div>

        <section className="dashboard-section" aria-labelledby="transactions-heading">
          <div className="dashboard-section__heading">
            <h2 id="transactions-heading" className="dashboard-section__title">
              Recent transactions
            </h2>
            <Link to="/transactions" className="dashboard-section__link">
              View all
            </Link>
          </div>

          {isLoading || !data ? (
            <ul className="transaction-list">
              <TransactionRowSkeleton />
              <TransactionRowSkeleton />
              <TransactionRowSkeleton />
            </ul>
          ) : recentTransactions.length === 0 ? (
            <p className="dashboard-empty">No transactions yet.</p>
          ) : (
            <ul className="transaction-list">
              {recentTransactions.map((transaction) => (
                <TransactionRow key={transaction.id} transaction={transaction} />
              ))}
            </ul>
          )}
        </section>
      </div>
    </main>
  );
}
