import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/Button/Button';
import { ErrorMessage } from '../components/ErrorMessage/ErrorMessage';
import { FormField } from '../components/FormField/FormField';
import { moneyRequestService } from '../services/moneyRequestService';
import type { MoneyRequestItem } from '../services/moneyRequestService';
import { disputeService } from '../services/disputeService';
import type { DisputeItem } from '../services/disputeService';
import { DisputeStatusBadge } from '../components/StatusBadge/DisputeStatusBadge';
import { userService } from '../services/userService';
import type { RecipientUser } from '../types/user';
import './RequestMoneyPage.css';

export function RequestMoneyPage() {
  const [activeTab, setActiveTab] = useState<'create' | 'incoming' | 'outgoing' | 'reversals'>('create');
  
  // Form State
  const [payerIdentifier, setPayerIdentifier] = useState('');
  const [amount, setAmount] = useState('');
  const [note, setNote] = useState('');
  
  // User Search Autocomplete
  const [searchResults, setSearchResults] = useState<RecipientUser[]>([]);
  const [showSearch, setShowSearch] = useState(false);

  // Status & List States
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | undefined>(undefined);
  const [successMessage, setSuccessMessage] = useState<string | undefined>(undefined);

  const [incomingList, setIncomingList] = useState<MoneyRequestItem[]>([]);
  const [outgoingList, setOutgoingList] = useState<MoneyRequestItem[]>([]);
  const [pendingReversals, setPendingReversals] = useState<DisputeItem[]>([]);
  const [myDisputes, setMyDisputes] = useState<DisputeItem[]>([]);
  const [loadingList, setLoadingList] = useState(false);

  // Reversal Request Inputs
  const [reversalRef, setReversalRef] = useState('');
  const [reversalReason, setReversalReason] = useState('');
  const [reversalMsg, setReversalMsg] = useState<string | null>(null);

  // Search User Autocomplete Hook
  useEffect(() => {
    if (payerIdentifier.trim().length >= 1) {
      userService.searchUsers(payerIdentifier).then((users) => {
        setSearchResults(users);
        setShowSearch(true);
      });
    } else {
      setSearchResults([]);
      setShowSearch(false);
    }
  }, [payerIdentifier]);

  // Load Request Lists Hook
  const loadRequests = async () => {
    setLoadingList(true);
    try {
      if (activeTab === 'incoming') {
        const inc = await moneyRequestService.getIncomingRequests();
        setIncomingList(inc);
      } else if (activeTab === 'outgoing') {
        const out = await moneyRequestService.getOutgoingRequests();
        setOutgoingList(out);
      } else if (activeTab === 'reversals') {
        const pending = await disputeService.getPendingConfirmations();
        setPendingReversals(pending);
        const history = await disputeService.getMyDisputes();
        setMyDisputes(history);
      }
    } catch (err: any) {
      console.error('Error fetching requests:', err);
    } finally {
      setLoadingList(false);
    }
  };

  useEffect(() => {
    if (activeTab !== 'create') {
      loadRequests();
    }
  }, [activeTab]);

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(undefined);
    setSuccessMessage(undefined);

    const parsedAmount = parseFloat(amount);
    if (!payerIdentifier || isNaN(parsedAmount) || parsedAmount <= 0) {
      setFormError('Please enter a valid payer username/email and amount.');
      return;
    }

    setIsSubmitting(true);
    try {
      await moneyRequestService.createRequest({
        payerIdentifier,
        amount: parsedAmount,
        note,
        expiresInHours: 24,
      });

      setSuccessMessage(`Money request of BDT ${parsedAmount.toFixed(2)} sent successfully!`);
      setPayerIdentifier('');
      setAmount('');
      setNote('');
    } catch (err: any) {
      setFormError(err.message || 'Failed to create money request.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleAction = async (requestId: string, action: 'ACCEPT' | 'DECLINE') => {
    try {
      await moneyRequestService.actionRequest(requestId, action);
      await loadRequests();
    } catch (err: any) {
      alert(`Action failed: ${err.message}`);
    }
  };

  const handleReversalSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reversalRef.trim() || !reversalReason.trim()) return;
    try {
      await disputeService.requestFalseTransactionReversal(reversalRef.trim(), reversalReason.trim());
      setReversalMsg(`Reversal request for ${reversalRef} submitted! Awaiting receiver confirmation.`);
      setReversalRef('');
      setReversalReason('');
      await loadRequests();
    } catch (err: any) {
      alert(`Request failed: ${err.message}`);
    }
  };

  const handleReceiverConfirm = async (disputeId: string, action: 'CONFIRM' | 'DENY') => {
    try {
      await disputeService.receiverConfirm(disputeId, action, 'Receiver response via web');
      await loadRequests();
    } catch (err: any) {
      alert(`Action failed: ${err.message}`);
    }
  };

  return (
    <main className="request-money-page">
      <div className="request-money-container">
        <header className="request-money-header">
          <Link to="/dashboard" className="request-money-header__back" aria-label="Go back to dashboard">
            ‹
          </Link>
          <h1 className="request-money-header__title">Money requests</h1>
        </header>

        <div className="request-tabs">
          <button
            className={`tab-button ${activeTab === 'create' ? 'active' : ''}`}
            onClick={() => setActiveTab('create')}
          >
            Create Request
          </button>
          <button
            className={`tab-button ${activeTab === 'incoming' ? 'active' : ''}`}
            onClick={() => setActiveTab('incoming')}
          >
            Incoming
          </button>
          <button
            className={`tab-button ${activeTab === 'outgoing' ? 'active' : ''}`}
            onClick={() => setActiveTab('outgoing')}
          >
            Outgoing
          </button>
          <button
            className={`tab-button ${activeTab === 'reversals' ? 'active' : ''}`}
            onClick={() => setActiveTab('reversals')}
          >
            False Tx Reversals
          </button>
        </div>

        {activeTab === 'create' && (
          <div className="card-box">
            <h2 className="card-title">Request Money from a User</h2>
            {formError && <ErrorMessage message={formError} />}
            {successMessage && (
              <div style={{ padding: '0.8rem', background: 'var(--color-primary-soft)', color: 'var(--color-primary-strong)', borderRadius: '8px' }}>
                {successMessage}
              </div>
            )}

            <form className="request-form" onSubmit={handleCreateSubmit}>
              <div style={{ position: 'relative' }}>
                <FormField
                  label="Payer Username or Email"
                  type="text"
                  name="payerIdentifier"
                  value={payerIdentifier}
                  onChange={(e) => setPayerIdentifier(e.target.value)}
                  placeholder="e.g. bindu_05"
                  required
                />
                {showSearch && searchResults.length > 0 && (
                  <div className="search-results">
                    {searchResults.map((user) => (
                      <div
                        key={user.id}
                        className="search-item"
                        onClick={() => {
                          setPayerIdentifier(user.handle);
                          setShowSearch(false);
                        }}
                      >
                        <strong>{user.name}</strong> (@{user.handle})
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <FormField
                label="Amount (BDT)"
                type="number"
                name="amount"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="100.00"
                min="1"
                step="0.01"
                required
              />

              <FormField
                label="Note / Purpose (Optional)"
                type="text"
                name="note"
                value={note}
                onChange={(e) => setNote(e.target.value)}
                placeholder="Project reimbursement"
              />

              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'Sending Request...' : 'Send Request'}
              </Button>
            </form>
          </div>
        )}

        {activeTab === 'incoming' && (
          <div className="card-box">
            <h2 className="card-title">Incoming Money Requests</h2>
            {loadingList ? (
              <p>Loading incoming requests...</p>
            ) : incomingList.length === 0 ? (
              <p style={{ color: 'var(--color-text-secondary)' }}>No incoming requests found.</p>
            ) : (
              incomingList.map((req) => (
                <div key={req.id} className="request-item">
                  <div className="request-info">
                    <span className="request-user">
                      Request from {req.requester_name || 'User'}
                    </span>
                    {req.note && <span className="request-note">Note: {req.note}</span>}
                    <span className="request-date">
                      Requested on {new Date(req.created_at).toLocaleString()}
                    </span>

                    {req.status === 'PENDING' && (
                      <div className="action-buttons">
                        <button
                          className="btn-accept"
                          onClick={() => handleAction(req.id, 'ACCEPT')}
                        >
                          Accept & Pay
                        </button>
                        <button
                          className="btn-decline"
                          onClick={() => handleAction(req.id, 'DECLINE')}
                        >
                          Decline
                        </button>
                      </div>
                    )}
                  </div>

                  <div className="request-amount-box">
                    <span className="request-amount">BDT {Number(req.amount).toFixed(2)}</span>
                    <span className={`request-status status-${req.status.toLowerCase()}`}>
                      {req.status}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'outgoing' && (
          <div className="card-box">
            <h2 className="card-title">Outgoing Money Requests</h2>
            {loadingList ? (
              <p>Loading outgoing requests...</p>
            ) : outgoingList.length === 0 ? (
              <p style={{ color: 'var(--color-text-secondary)' }}>No outgoing requests found.</p>
            ) : (
              outgoingList.map((req) => (
                <div key={req.id} className="request-item">
                  <div className="request-info">
                    <span className="request-user">
                      Requested from {req.payer_name || 'User'}
                    </span>
                    {req.note && <span className="request-note">Note: {req.note}</span>}
                    <span className="request-date">
                      {new Date(req.created_at).toLocaleString()}
                    </span>
                  </div>

                  <div className="request-amount-box">
                    <span className="request-amount">BDT {Number(req.amount).toFixed(2)}</span>
                    <span className={`request-status status-${req.status.toLowerCase()}`}>
                      {req.status}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'reversals' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div className="card-box">
              <h2 className="card-title">Report False Transaction Reversal</h2>
              {reversalMsg && (
                <div style={{ padding: '0.8rem', background: 'var(--color-primary-soft)', color: 'var(--color-primary-strong)', borderRadius: '8px' }}>
                  {reversalMsg}
                </div>
              )}
              <form className="request-form" onSubmit={handleReversalSubmit}>
                <FormField
                  label="Transaction Reference ID"
                  type="text"
                  name="reversalRef"
                  value={reversalRef}
                  onChange={(e) => setReversalRef(e.target.value)}
                  placeholder="e.g. TX-20260829-6A9824"
                  required
                />
                <FormField
                  label="Reason / Explanation"
                  type="text"
                  name="reversalReason"
                  value={reversalReason}
                  onChange={(e) => setReversalReason(e.target.value)}
                  placeholder="Sent money by mistake to wrong username"
                  required
                />
                <Button type="submit">Submit False Transaction Request</Button>
              </form>
            </div>

            {pendingReversals.length > 0 && (
              <div className="card-box">
                <h2 className="card-title">Pending False Transaction Confirmations for You</h2>
                {pendingReversals.map((d) => (
                  <div key={d.id} className="request-item">
                    <div className="request-info">
                      <span className="request-user">
                        @{d.sender_username} claims transfer {d.transaction_reference} (BDT {Number(d.amount).toFixed(2)}) was sent in error.
                      </span>
                      <span className="request-note">Reason: {d.reason}</span>
                      <div className="action-buttons">
                        <button
                          className="btn-accept"
                          onClick={() => handleReceiverConfirm(d.id, 'CONFIRM')}
                        >
                          Confirm & Allow Admin Refund
                        </button>
                        <button
                          className="btn-decline"
                          onClick={() => handleReceiverConfirm(d.id, 'DENY')}
                        >
                          Deny
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {myDisputes.length > 0 && (
              <div className="card-box">
                <h2 className="card-title">Your False Transaction & Dispute History</h2>
                {myDisputes.map((d) => (
                  <div key={d.id} className="request-item">
                    <div className="request-info">
                      <span className="request-user">
                        {d.dispute_type} • Ref: {d.transaction_reference || d.transaction_id}
                      </span>
                      <span className="request-note">Reason: {d.reason}</span>
                      <div style={{ marginTop: '0.3rem' }}>
                        <DisputeStatusBadge status={d.status} />
                      </div>
                    </div>
                    <div className="request-amount-box">
                      <span className="request-amount">BDT {Number(d.amount).toFixed(2)}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
