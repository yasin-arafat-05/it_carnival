import { useCallback, useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { BalanceCard, BalanceCardSkeleton } from '../components/BalanceCard/BalanceCard';
import { Button } from '../components/Button/Button';
import '../components/Button/Button.css';
import { ErrorMessage } from '../components/ErrorMessage/ErrorMessage';
import { Logo } from '../components/Brand/Logo';
import { TransactionRow, TransactionRowSkeleton } from '../components/TransactionRow/TransactionRow';
import { mockDashboardService } from '../services/dashboardService';
import type { DashboardData } from '../types/dashboard';
import './DashboardPage.css';

function getFirstName(fullName: string): string {
  return fullName.trim().split(/\s+/)[0] ?? fullName;
}

/**
 * Feature 5/44 — Wallet Dashboard / Home.
 *
 * Loads mock dashboard data (user, balance, recent transactions) from
 * `mockDashboardService` and renders it. This page owns the load/error
 * state; the display components it renders (`BalanceCard`, `TransactionRow`)
 * never fetch or compute data themselves — they only format what they're
 * given.
 */
export function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const isMounted = useRef(true);

  const loadDashboard = useCallback(() => {
    setIsLoading(true);
    setError(null);

    mockDashboardService
      .getDashboardData()
      .then((result) => {
        if (!isMounted.current) return;
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

  useEffect(() => {
    isMounted.current = true;
    loadDashboard();
    return () => {
      isMounted.current = false;
    };
  }, [loadDashboard]);

  const recentTransactions = data?.transactions.slice(0, 5) ?? [];

  return (
    <main className="dashboard-page">
      <div className="dashboard-page__container">
        <header className="dashboard-header">
          <div className="dashboard-header__brand">
            <Logo size={36} withWordmark={false} />
            <h1 className="dashboard-header__greeting">
              {isLoading && !data
                ? 'Welcome back'
                : `Hi, ${data ? getFirstName(data.user.name) : 'there'}`}
            </h1>
          </div>
          <Link
            to="/profile"
            className="dashboard-header__profile-link"
            aria-label="Go to your profile"
          >
            {data ? getFirstName(data.user.name).charAt(0).toUpperCase() : '·'}
          </Link>
        </header>

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
