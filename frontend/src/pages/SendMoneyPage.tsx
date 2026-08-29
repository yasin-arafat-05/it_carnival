import { useEffect, useRef, useState } from 'react';
import type { FormEvent } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { Button } from '../components/Button/Button';
import { ErrorBanner } from '../components/ErrorBanner/ErrorBanner';
import { ErrorMessage } from '../components/ErrorMessage/ErrorMessage';
import { FormField } from '../components/FormField/FormField';
import { LoadingIndicator } from '../components/LoadingIndicator/LoadingIndicator';
import { Modal } from '../components/Modal/Modal';
import { HoldToConfirmButton } from '../components/HoldToConfirmButton/HoldToConfirmButton';
import { TransactionStatusBadge } from '../components/StatusBadge/TransactionStatusBadge';
import { mockDashboardService } from '../services/dashboardService';
import { mockSendMoneyService } from '../services/sendMoneyService';
import { mockUserService } from '../services/userService';
import { formatCurrency } from '../utils/currency';
import {
  parseAmount,
  validateAmount,
  validateNote,
  validateNotSelfTransfer,
} from '../utils/sendMoneyValidation';
import type { AppErrorCode } from '../types/errors';
import type { RecipientUser } from '../types/user';
import './SendMoneyPage.css';

interface FieldErrors {
  amount?: string;
  note?: string;
}

type ScreenState =
  | { step: 'loading' }
  | { step: 'load-error'; message: string }
  | { step: 'form' }
  | { step: 'result'; success: true; transactionId: string; reference: string }
  | { step: 'result'; success: false; code?: AppErrorCode; message: string };

/**
 * Feature 8/45 — Send Money screen, plus Feature 10/47 (Transaction
 * Confirmation) and Feature 48 (Transfer Result Screen).
 *
 * Flow: load the receiver (by :userId from the route) and the sender's
 * current mock balance -> fill in amount/note with client-side validation
 * -> confirm in a modal -> submit once (idempotency-guarded in the UI) ->
 * show a success or failure result. All data comes from
 * `mockUserService` / `mockDashboardService` / `mockSendMoneyService` —
 * this page never hardcodes a balance or recipient record, so those
 * services can be swapped for real API calls later without UI changes.
 */
export function SendMoneyPage() {
  const { userId } = useParams<{ userId: string }>();
  const navigate = useNavigate();

  const [screen, setScreen] = useState<ScreenState>({ step: 'loading' });
  const [receiver, setReceiver] = useState<RecipientUser | undefined>(undefined);
  const [currentUserId, setCurrentUserId] = useState<string | undefined>(undefined);
  const [availableBalance, setAvailableBalance] = useState(0);
  const [currency, setCurrency] = useState('BDT');
  const [todaySentTotal, setTodaySentTotal] = useState(0);

  const [amount, setAmount] = useState('');
  const [note, setNote] = useState('');
  const [touched, setTouched] = useState<{ amount?: boolean; note?: boolean }>({});
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);

  const isSubmittingRef = useRef(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    let cancelled = false;

    if (!userId) {
      setScreen({ step: 'load-error', message: "Couldn't load recipient." });
      return;
    }

    setScreen({ step: 'loading' });

    Promise.all([mockUserService.getUserById(userId), mockDashboardService.getDashboardData()])
      .then(([user, dashboard]) => {
        if (cancelled) return;
        if (!user) {
          setScreen({ step: 'load-error', message: "Couldn't find that recipient." });
          return;
        }
        setReceiver(user);
        setCurrentUserId(dashboard.user.id);
        setAvailableBalance(dashboard.balance);
        setCurrency(dashboard.currency);

        const todayStr = new Date().toISOString().split('T')[0];
        const sentToday = (dashboard.transactions || []).reduce((sum: number, tx: any) => {
          if (tx.direction === 'sent' && tx.occurredAt && tx.occurredAt.startsWith(todayStr)) {
            return sum + Number(tx.amount);
          }
          return sum;
        }, 0);
        setTodaySentTotal(sentToday);
        setScreen({ step: 'form' });
      })
      .catch(() => {
        if (cancelled) return;
        setScreen({ step: 'load-error', message: "Couldn't load balance." });
      });

    return () => {
      cancelled = true;
    };
  }, [userId]);

  const remainingDailyLimit = Math.max(0, 50000 - todaySentTotal);

  const errors: FieldErrors = {
    amount: validateAmount(amount, availableBalance, remainingDailyLimit),
    note: validateNote(note),
  };
  const selfTransferError =
    receiver && currentUserId ? validateNotSelfTransfer(receiver.id, currentUserId) : undefined;
  const isValid = !errors.amount && !errors.note && !selfTransferError && Boolean(receiver);

  function handleRetryLoad() {
    setScreen({ step: 'loading' });
    // Re-trigger the effect by forcing a fresh load through the same params.
    if (!userId) return;
    Promise.all([mockUserService.getUserById(userId), mockDashboardService.getDashboardData()])
      .then(([user, dashboard]) => {
        if (!user) {
          setScreen({ step: 'load-error', message: "Couldn't find that recipient." });
          return;
        }
        setReceiver(user);
        setCurrentUserId(dashboard.user.id);
        setAvailableBalance(dashboard.balance);
        setCurrency(dashboard.currency);
        setScreen({ step: 'form' });
      })
      .catch(() => {
        setScreen({ step: 'load-error', message: "Couldn't load balance." });
      });
  }

  function handleReviewSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setTouched({ amount: true, note: true });
    if (!isValid) return;
    setIsConfirmOpen(true);
  }

  function handleConfirm() {
    // Idempotency guard (UI-only): ignore repeat taps while a request is
    // already in flight. See `mockSendMoneyService` for the required
    // server-side counterpart.
    if (isSubmittingRef.current || !receiver) return;
    isSubmittingRef.current = true;
    setIsSubmitting(true);

    const parsedAmount = parseAmount(amount) ?? 0;

    mockSendMoneyService
      .sendMoney({ receiverId: receiver.id, amount: parsedAmount, note: note.trim() })
      .then((result) => {
        setIsConfirmOpen(false);
        if (result.ok) {
          setScreen({
            step: 'result',
            success: true,
            transactionId: result.transactionId,
            reference: result.reference,
          });
        } else {
          setScreen({ step: 'result', success: false, code: result.code, message: result.message });
        }
      })
      .finally(() => {
        isSubmittingRef.current = false;
        setIsSubmitting(false);
      });
  }

  function handleTryAgain() {
    setScreen({ step: 'form' });
  }

  const parsedAmount = parseAmount(amount);

  return (
    <main className="send-money-page">
      <div className="send-money-page__container">
        <header className="send-money-page__header">
          <Link to="/send" className="send-money-page__back" aria-label="Back to search">
            ←
          </Link>
          <h1 className="send-money-page__title">Send money</h1>
        </header>

        {screen.step === 'loading' && (
          <section className="send-money-page__section">
            <LoadingIndicator label="Loading recipient…" />
          </section>
        )}

        {screen.step === 'load-error' && (
          <section className="send-money-page__section">
            <ErrorMessage message={screen.message} />
            <Button variant="secondary" onClick={handleRetryLoad}>
              Retry
            </Button>
          </section>
        )}

        {screen.step === 'form' && receiver && (
          <>
            <section className="send-money-page__section">
              <div className="receiver-summary">
                <span className="receiver-summary__avatar" aria-hidden="true">
                  {receiver.name.trim().charAt(0).toUpperCase()}
                </span>
                <span className="receiver-summary__text">
                  <span className="receiver-summary__name">{receiver.name}</span>
                  <span className="receiver-summary__meta">@{receiver.handle}</span>
                </span>
              </div>
            </section>

            <section className="send-money-page__section">
              <form onSubmit={handleReviewSubmit} noValidate>
                {selfTransferError && touched.amount && <ErrorMessage message={selfTransferError} />}

                <FormField
                  label="Amount"
                  inputMode="decimal"
                  placeholder="0.00"
                  name="amount"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  onBlur={() => setTouched((t) => ({ ...t, amount: true }))}
                  error={touched.amount ? errors.amount : undefined}
                  hint={`Available balance: ${formatCurrency(availableBalance, currency)} • Daily limit remaining: ${formatCurrency(remainingDailyLimit, currency)} / ${formatCurrency(50000, currency)}`}
                />

                <FormField
                  label="Note (optional)"
                  type="text"
                  name="note"
                  placeholder="What's this for?"
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                  onBlur={() => setTouched((t) => ({ ...t, note: true }))}
                  error={touched.note ? errors.note : undefined}
                />

                <Button type="submit" fullWidth disabled={!isValid}>
                  Review transfer
                </Button>
              </form>
            </section>
          </>
        )}

        {screen.step === 'result' && (
          <section className="send-money-page__section">
            {screen.success ? (
              <div className="transfer-result">
                <span className="transfer-result__icon transfer-result__icon--success" aria-hidden="true">
                  ✓
                </span>
                <h2 className="transfer-result__heading">Money sent</h2>
                <p className="transfer-result__message">
                  Your transfer to {receiver?.name ?? 'the recipient'} is complete.
                </p>
                <TransactionStatusBadge status="completed" />
                <dl className="transfer-result__details confirm-summary">
                  <div className="confirm-summary__row">
                    <dt>Amount</dt>
                    <dd className="confirm-summary__amount">
                      {formatCurrency(parsedAmount ?? 0, currency)}
                    </dd>
                  </div>
                  <div className="confirm-summary__row">
                    <dt>Receiver</dt>
                    <dd>{receiver?.name ?? '—'}</dd>
                  </div>
                  <div className="confirm-summary__row">
                    <dt>Transaction ID</dt>
                    <dd>{screen.transactionId}</dd>
                  </div>
                  <div className="confirm-summary__row">
                    <dt>Reference</dt>
                    <dd>{screen.reference}</dd>
                  </div>
                </dl>
                <div className="transfer-result__actions">
                  <Button fullWidth onClick={() => navigate('/dashboard')}>
                    Back to dashboard
                  </Button>
                </div>
              </div>
            ) : (
              <div className="transfer-result">
                <span className="transfer-result__icon transfer-result__icon--failure" aria-hidden="true">
                  ⚠
                </span>
                <h2 className="transfer-result__heading">Transfer failed</h2>
                <TransactionStatusBadge status="failed" />
                <ErrorBanner code={screen.code} message={screen.message} />
                <div className="transfer-result__actions">
                  <Button fullWidth onClick={handleTryAgain}>
                    Try again
                  </Button>
                  <Button variant="secondary" fullWidth onClick={() => navigate('/dashboard')}>
                    Back to dashboard
                  </Button>
                </div>
              </div>
            )}
          </section>
        )}
      </div>

      {isConfirmOpen && receiver && (
        <Modal
          title="Confirm transfer"
          isDismissDisabled={isSubmitting}
          onClose={() => {
            if (!isSubmitting) setIsConfirmOpen(false);
          }}
          footer={
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem', width: '100%' }}>
              <HoldToConfirmButton
                durationMs={5000}
                onConfirm={handleConfirm}
                isSubmitting={isSubmitting}
              />
              <Button
                variant="secondary"
                onClick={() => setIsConfirmOpen(false)}
                disabled={isSubmitting}
                fullWidth
              >
                Cancel
              </Button>
            </div>
          }
        >
          <dl className="confirm-summary">
            <div className="confirm-summary__row">
              <dt>Receiver</dt>
              <dd>{receiver.name}</dd>
            </div>
            <div className="confirm-summary__row">
              <dt>Amount</dt>
              <dd className="confirm-summary__amount">
                {formatCurrency(parsedAmount ?? 0, currency)}
              </dd>
            </div>
            <div className="confirm-summary__row">
              <dt>Note</dt>
              <dd>{note.trim() || '—'}</dd>
            </div>
          </dl>
        </Modal>
      )}
    </main>
  );
}
