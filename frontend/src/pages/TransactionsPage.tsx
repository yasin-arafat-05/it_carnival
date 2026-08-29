import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/Button/Button';
import { FormField } from '../components/FormField/FormField';
import { Modal } from '../components/Modal/Modal';
import { TransactionStatusBadge } from '../components/StatusBadge/TransactionStatusBadge';
import { DisputeStatusBadge } from '../components/StatusBadge/DisputeStatusBadge';
import { transactionService } from '../services/transactionService';
import { disputeService } from '../services/disputeService';
import type { TransactionItem, LedgerItem } from '../services/transactionService';
import type { DisputeItem } from '../services/disputeService';
import './TransactionsPage.css';

export function TransactionsPage() {
  const [activeTab, setActiveTab] = useState<'transactions' | 'ledger'>('transactions');
  const [transactions, setTransactions] = useState<TransactionItem[]>([]);
  const [ledgerEntries, setLedgerEntries] = useState<LedgerItem[]>([]);
  const [myDisputes, setMyDisputes] = useState<DisputeItem[]>([]);
  const [loading, setLoading] = useState(true);

  // Selected Transaction Details Modal
  const [selectedTx, setSelectedTx] = useState<TransactionItem | null>(null);
  const [activeDispute, setActiveDispute] = useState<DisputeItem | null>(null);

  // Dispute Filing Modal
  const [isFilingDispute, setIsFilingDispute] = useState(false);
  const [disputeReason, setDisputeReason] = useState('');
  const [submittingDispute, setSubmittingDispute] = useState(false);
  const [disputeError, setDisputeError] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'transactions') {
        const [txList, dispList] = await Promise.all([
          transactionService.getTransactions(1, 50),
          disputeService.getMyDisputes(),
        ]);
        setTransactions(txList);
        setMyDisputes(dispList);
      } else {
        const lList = await transactionService.getLedgerEntries(1, 50);
        setLedgerEntries(lList);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [activeTab]);

  const handleOpenTx = async (tx: TransactionItem) => {
    setSelectedTx(tx);
    const existing = myDisputes.find((d) => d.transaction_reference === tx.reference_id);
    if (existing) {
      setActiveDispute(existing);
    } else {
      try {
        const fetched = await disputeService.getDisputeForTransaction(tx.reference_id);
        setActiveDispute(fetched || null);
      } catch {
        setActiveDispute(null);
      }
    }
  };

  const handleStartDispute = () => {
    setDisputeReason('');
    setDisputeError(null);
    setIsFilingDispute(true);
  };

  const handleSubmitDispute = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedTx) return;
    if (!disputeReason.trim()) {
      setDisputeError('Please describe why this transaction is false or disputed.');
      return;
    }

    setSubmittingDispute(true);
    setDisputeError(null);

    try {
      const created = await disputeService.requestFalseTransactionReversal(
        selectedTx.reference_id,
        disputeReason.trim()
      );
      setActiveDispute(created);
      setIsFilingDispute(false);
      await loadData();
    } catch (err: any) {
      setDisputeError(err.message || 'Failed to submit dispute claim.');
    } finally {
      setSubmittingDispute(false);
    }
  };

  return (
    <main className="transactions-page">
      <div className="transactions-container">
        <header className="transactions-header">
          <Link to="/dashboard" className="transactions-header__back" aria-label="Go back to dashboard">
            ‹
          </Link>
          <h1 className="transactions-header__title">Transaction history</h1>
        </header>

        <div className="tx-tabs">
          <button
            className={`tx-tab-btn ${activeTab === 'transactions' ? 'active' : ''}`}
            onClick={() => setActiveTab('transactions')}
          >
            All Transactions
          </button>
          <button
            className={`tx-tab-btn ${activeTab === 'ledger' ? 'active' : ''}`}
            onClick={() => setActiveTab('ledger')}
          >
            Double-Entry Ledger Audit
          </button>
        </div>

        <div className="tx-card">
          {loading ? (
            <p>Loading records...</p>
          ) : activeTab === 'transactions' ? (
            transactions.length === 0 ? (
              <p style={{ color: '#94a3b8' }}>No transactions found.</p>
            ) : (
              transactions.map((tx) => {
                const disp = myDisputes.find((d) => d.transaction_reference === tx.reference_id);
                return (
                  <div key={tx.id} className="tx-item" onClick={() => handleOpenTx(tx)}>
                    <div>
                      <span className="tx-ref">{tx.reference_id}</span>
                      <div className="tx-parties">
                        {tx.sender_username ? `${tx.sender_username} → ` : 'System → '}
                        {tx.receiver_username || 'Account'}
                      </div>
                      <div className="tx-meta">
                        {tx.note ? `Note: ${tx.note} • ` : ''}
                        {new Date(tx.created_at).toLocaleString()}
                      </div>
                    </div>
                    <div className="tx-right">
                      <div className="tx-amount">BDT {Number(tx.amount).toFixed(2)}</div>
                      <div style={{ display: 'flex', gap: '0.4rem', alignItems: 'center', justifyContent: 'flex-end', marginTop: '0.2rem' }}>
                        <span className="tx-type">{tx.transaction_type}</span>
                        {disp ? (
                          <DisputeStatusBadge status={disp.status} />
                        ) : (
                          <TransactionStatusBadge
                            status={(tx.status?.toLowerCase() as any) || 'completed'}
                          />
                        )}
                      </div>
                    </div>
                  </div>
                );
              })
            )
          ) : ledgerEntries.length === 0 ? (
            <p style={{ color: '#94a3b8' }}>No ledger audit logs found.</p>
          ) : (
            ledgerEntries.map((entry) => (
              <div key={entry.id} className="tx-item" style={{ cursor: 'default' }}>
                <div>
                  <span
                    className={`tx-type ${
                      entry.entry_type === 'DEBIT' ? 'entry-debit' : 'entry-credit'
                    }`}
                  >
                    {entry.entry_type}
                  </span>
                  <div className="tx-meta" style={{ marginTop: '0.3rem' }}>
                    Balance After: BDT {Number(entry.balance_after).toFixed(2)}
                  </div>
                  <div className="tx-meta">
                    {new Date(entry.created_at).toLocaleString()}
                  </div>
                </div>
                <div className="tx-right">
                  <div
                    className={`tx-amount ${
                      entry.entry_type === 'DEBIT' ? 'entry-debit' : 'entry-credit'
                    }`}
                  >
                    {entry.entry_type === 'DEBIT' ? '-' : '+'} BDT {Number(entry.amount).toFixed(2)}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Selected Transaction Details Modal */}
      {selectedTx && !isFilingDispute && (
        <Modal
          title="Transaction Details"
          onClose={() => setSelectedTx(null)}
          footer={
            <Button variant="secondary" onClick={() => setSelectedTx(null)} fullWidth>
              Close
            </Button>
          }
        >
          <div className="tx-details-content">
            <dl className="tx-details-summary">
              <div className="tx-details-row">
                <dt>Reference ID</dt>
                <dd style={{ fontFamily: 'monospace' }}>{selectedTx.reference_id}</dd>
              </div>
              <div className="tx-details-row">
                <dt>Sender</dt>
                <dd>{selectedTx.sender_username || 'System'}</dd>
              </div>
              <div className="tx-details-row">
                <dt>Receiver</dt>
                <dd>{selectedTx.receiver_username || 'Account'}</dd>
              </div>
              <div className="tx-details-row">
                <dt>Amount</dt>
                <dd style={{ color: 'var(--color-primary-strong)', fontSize: '1.1rem' }}>
                  BDT {Number(selectedTx.amount).toFixed(2)}
                </dd>
              </div>
              <div className="tx-details-row">
                <dt>Transaction Type</dt>
                <dd>{selectedTx.transaction_type}</dd>
              </div>
              <div className="tx-details-row">
                <dt>Date &amp; Time</dt>
                <dd>{new Date(selectedTx.created_at).toLocaleString()}</dd>
              </div>
              <div className="tx-details-row">
                <dt>Status</dt>
                <dd>
                  {activeDispute ? (
                    <DisputeStatusBadge status={activeDispute.status} />
                  ) : (
                    <TransactionStatusBadge status={(selectedTx.status?.toLowerCase() as any) || 'completed'} />
                  )}
                </dd>
              </div>
            </dl>

            {/* Dispute / False Transaction Audit Timeline */}
            {activeDispute ? (
              <div className="dispute-timeline">
                <div className="dispute-timeline-title">Dispute Audit Timeline</div>
                
                <div className="timeline-step completed">
                  <div className="timeline-dot" />
                  <div className="timeline-info">
                    <span className="timeline-label">1. Dispute Claim Submitted</span>
                    <span className="timeline-sub">Reason: {activeDispute.reason}</span>
                    <span className="timeline-sub">{new Date(activeDispute.created_at).toLocaleString()}</span>
                  </div>
                </div>

                <div className={`timeline-step ${activeDispute.status !== 'PENDING_RECEIVER_CONFIRMATION' ? 'completed' : ''}`}>
                  <div className="timeline-dot" />
                  <div className="timeline-info">
                    <span className="timeline-label">2. Receiver Verification</span>
                    <span className="timeline-sub">
                      {activeDispute.status === 'PENDING_RECEIVER_CONFIRMATION'
                        ? 'Awaiting receiver confirmation...'
                        : activeDispute.status === 'CONFIRMED_BY_RECEIVER' || activeDispute.status === 'RECEIVER_CONFIRMED'
                        ? 'Receiver Confirmed claim'
                        : activeDispute.status === 'REJECTED' || activeDispute.status === 'REJECTED_BY_RECEIVER'
                        ? 'Rejected by Receiver'
                        : 'Verification completed'}
                    </span>
                  </div>
                </div>

                <div className={`timeline-step ${activeDispute.status === 'RESOLVED_REVERSED' || activeDispute.status === 'REFUND_COMPLETED' ? 'completed' : ''}`}>
                  <div className="timeline-dot" />
                  <div className="timeline-info">
                    <span className="timeline-label">3. Admin Audit &amp; Refund Execution</span>
                    <span className="timeline-sub">
                      {activeDispute.status === 'RESOLVED_REVERSED' || activeDispute.status === 'REFUND_COMPLETED'
                        ? 'Refund approved and money credited back to sender.'
                        : 'Admin verification in progress...'}
                    </span>
                  </div>
                </div>
              </div>
            ) : (
              selectedTx.status?.toUpperCase() === 'COMPLETED' && (
                <Button variant="secondary" fullWidth onClick={handleStartDispute}>
                  Report False Transaction
                </Button>
              )
            )}
          </div>
        </Modal>
      )}

      {/* File Dispute / False Transaction Modal */}
      {isFilingDispute && selectedTx && (
        <Modal
          title="Report False Transaction"
          onClose={() => setIsFilingDispute(false)}
          footer={
            <div style={{ display: 'flex', gap: '0.8rem', width: '100%' }}>
              <Button variant="secondary" onClick={() => setIsFilingDispute(false)} disabled={submittingDispute}>
                Cancel
              </Button>
              <Button onClick={handleSubmitDispute} disabled={submittingDispute} isLoading={submittingDispute}>
                Submit Dispute Claim
              </Button>
            </div>
          }
        >
          <form onSubmit={handleSubmitDispute} className="tx-details-content">
            <div className="dispute-warning-banner">
              ⚠️ <strong>Admin Verification Required:</strong> Submitting a false transaction report initiates a formal review. The receiver will be notified to confirm or deny, and an admin will audit before refund execution.
            </div>

            <FormField
              label="Reason for Dispute / Details"
              placeholder="Explain why this transaction was wrong or unintended..."
              value={disputeReason}
              onChange={(e) => setDisputeReason(e.target.value)}
              error={disputeError || undefined}
            />
          </form>
        </Modal>
      )}
    </main>
  );
}
