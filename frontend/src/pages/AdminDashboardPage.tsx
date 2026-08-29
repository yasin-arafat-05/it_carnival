import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '../components/Button/Button';
import { FormField } from '../components/FormField/FormField';
import { Logo } from '../components/Brand/Logo';
import { adminService } from '../services/adminService';
import { authService } from '../services/authService';
import { DisputeStatusBadge } from '../components/StatusBadge/DisputeStatusBadge';
import type { TransactionItem } from '../services/transactionService';
import type { DisputeItem } from '../services/disputeService';
import './AdminDashboardPage.css';

export function AdminDashboardPage() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'disputes' | 'transactions' | 'users'>('disputes');

  // Transactions State
  const [searchQuery, setSearchQuery] = useState('');
  const [transactions, setTransactions] = useState<TransactionItem[]>([]);
  const [loadingTxs, setLoadingTxs] = useState(false);

  // Disputes State
  const [disputes, setDisputes] = useState<DisputeItem[]>([]);
  const [loadingDisputes, setLoadingDisputes] = useState(false);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  // Make Admin State
  const [promoteUsername, setPromoteUsername] = useState('');
  const [promoteStatus, setPromoteStatus] = useState<string | null>(null);

  const handleLogout = () => {
    authService.logout();
    navigate('/login', { replace: true });
  };

  const loadDisputes = async () => {
    setLoadingDisputes(true);
    try {
      const list = await adminService.getSystemDisputes();
      setDisputes(list);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoadingDisputes(false);
    }
  };

  const loadTransactions = async () => {
    setLoadingTxs(true);
    try {
      const txs = await adminService.getSystemTransactions(1, 50, searchQuery);
      setTransactions(txs);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoadingTxs(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'disputes') {
      loadDisputes();
    } else if (activeTab === 'transactions') {
      loadTransactions();
    }
  }, [activeTab]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadTransactions();
  };

  const handleExecuteReversal = async (disputeId: string) => {
    try {
      await adminService.executeReversal(disputeId, 'Executed reversal via Admin Panel');
      setActionMessage('Reversal executed successfully! Money refunded to sender.');
      await loadDisputes();
    } catch (err: any) {
      alert(`Reversal failed: ${err.message}`);
    }
  };

  const handleResolveComplaint = async (disputeId: string, decision: 'APPROVE_REVERSAL' | 'REJECT') => {
    try {
      await adminService.resolveComplaint(disputeId, decision, `Resolved by Admin as ${decision}`);
      setActionMessage(`Complaint ${decision.toLowerCase()} resolved.`);
      await loadDisputes();
    } catch (err: any) {
      alert(`Resolution failed: ${err.message}`);
    }
  };

  const handlePromoteAdmin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!promoteUsername.trim()) return;
    try {
      const res = await adminService.makeAdmin(promoteUsername.trim());
      setPromoteStatus(res.message);
      setPromoteUsername('');
    } catch (err: any) {
      setPromoteStatus(`Error: ${err.message}`);
    }
  };

  return (
    <main className="admin-page">
      <div className="admin-container">
        <header className="admin-header">
          <div className="admin-header__brand">
            <Logo size={32} withWordmark={false} />
            <h1 className="admin-header__title">Admin Dashboard &amp; System Audit</h1>
            <span className="admin-badge">ADMIN</span>
          </div>
          <div style={{ display: 'flex', gap: '0.8rem', alignItems: 'center' }}>
            <Link to="/profile" className="button button--secondary" style={{ padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}>
              Profile
            </Link>
            <Button variant="secondary" onClick={handleLogout} style={{ padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}>
              Logout
            </Button>
          </div>
        </header>

        <div className="admin-tabs">
          <button
            className={`admin-tab-btn ${activeTab === 'disputes' ? 'active' : ''}`}
            onClick={() => setActiveTab('disputes')}
          >
            Disputes & Reversals
          </button>
          <button
            className={`admin-tab-btn ${activeTab === 'transactions' ? 'active' : ''}`}
            onClick={() => setActiveTab('transactions')}
          >
            All System Transactions
          </button>
          <button
            className={`admin-tab-btn ${activeTab === 'users' ? 'active' : ''}`}
            onClick={() => setActiveTab('users')}
          >
            Admin Management
          </button>
        </div>

        {actionMessage && (
          <div style={{ padding: '0.8rem', background: 'var(--color-primary-soft)', color: 'var(--color-primary-strong)', borderRadius: '8px' }}>
            {actionMessage}
          </div>
        )}

        {activeTab === 'disputes' && (
          <div className="admin-card">
            <h2 className="card-title">Disputes & False Transaction Reversals</h2>
            {loadingDisputes ? (
              <p>Loading disputes...</p>
            ) : disputes.length === 0 ? (
              <p style={{ color: 'var(--color-text-secondary)' }}>No open disputes or false transaction claims.</p>
            ) : (
              disputes.map((d) => (
                <div key={d.id} className="dispute-item">
                  <div className="dispute-item__header">
                    <span className="dispute-type">{d.dispute_type}</span>
                    <DisputeStatusBadge status={d.status} />
                  </div>

                  <div>
                    <strong>Ref:</strong> {d.transaction_reference || d.transaction_id}
                  </div>
                  <div>
                    <strong>Parties:</strong> Sender @{d.sender_username || 'Sender'} &rarr; Receiver @{d.receiver_username || 'Receiver'}
                  </div>
                  <div>
                    <strong>Amount:</strong> BDT {Number(d.amount).toFixed(2)}
                  </div>

                  <div className="dispute-reason">
                    <strong>Reason:</strong> {d.reason}
                    {d.receiver_notes && (
                      <div style={{ marginTop: '0.3rem', color: 'var(--color-primary-strong)' }}>
                        <strong>Receiver Confirmation:</strong> {d.receiver_notes}
                      </div>
                    )}
                  </div>

                  <div className="dispute-actions">
                    {(d.status === 'CONFIRMED_BY_RECEIVER' || d.status === 'UNDER_INVESTIGATION' || d.status === 'PENDING_RECEIVER_CONFIRMATION') && (
                      <button
                        className="btn-execute"
                        onClick={() => handleExecuteReversal(d.id)}
                      >
                        Execute Money Reversal (Refund)
                      </button>
                    )}

                    {d.status === 'UNDER_INVESTIGATION' && (
                      <button
                        className="btn-reject"
                        onClick={() => handleResolveComplaint(d.id, 'REJECT')}
                      >
                        Reject Complaint
                      </button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'transactions' && (
          <div className="admin-card">
            <h2 className="card-title">System-Wide Transactions Audit</h2>
            <form className="admin-search-box" onSubmit={handleSearchSubmit}>
              <FormField
                label=""
                type="text"
                name="searchQuery"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search reference ID or username (e.g. TX-20260829 or bindu_05)"
              />
              <Button type="submit">Search</Button>
            </form>

            {loadingTxs ? (
              <p>Searching transactions...</p>
            ) : transactions.length === 0 ? (
              <p style={{ color: 'var(--color-text-secondary)' }}>No matching transactions found.</p>
            ) : (
              transactions.map((tx) => (
                <div key={tx.id} className="tx-item">
                  <div>
                    <span className="tx-ref">{tx.reference_id}</span>
                    <div className="tx-parties">
                      {tx.sender_username ? `@${tx.sender_username} → ` : 'System → '}
                      {tx.receiver_username ? `@${tx.receiver_username}` : 'Account'}
                    </div>
                    <div className="tx-meta">
                      {tx.note ? `Note: ${tx.note} • ` : ''}
                      {new Date(tx.created_at).toLocaleString()}
                    </div>
                  </div>
                  <div className="tx-right">
                    <div className="tx-amount">BDT {Number(tx.amount).toFixed(2)}</div>
                    <span className="tx-type">{tx.transaction_type}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'users' && (
          <div className="admin-card">
            <h2 className="card-title">Promote User to Admin Role</h2>
            {promoteStatus && (
              <div style={{ padding: '0.8rem', background: 'var(--color-primary-soft)', color: 'var(--color-primary-strong)', borderRadius: '8px' }}>
                {promoteStatus}
              </div>
            )}
            <form className="request-form" onSubmit={handlePromoteAdmin}>
              <FormField
                label="Target Username"
                type="text"
                name="promoteUsername"
                value={promoteUsername}
                onChange={(e) => setPromoteUsername(e.target.value)}
                placeholder="e.g. yasin_arafat_05"
              />
              <Button type="submit">Grant ADMIN Role</Button>
            </form>
          </div>
        )}
      </div>
    </main>
  );
}
