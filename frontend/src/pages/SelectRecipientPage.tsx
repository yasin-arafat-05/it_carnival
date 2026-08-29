import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FormField } from '../components/FormField/FormField';
import {
  RecipientListItem,
  RecipientListItemSkeleton,
} from '../components/RecipientListItem/RecipientListItem';
import { mockUserService } from '../services/userService';
import type { RecipientUser } from '../types/user';
import './SelectRecipientPage.css';

/**
 * Feature 7/46 — Search / Select User (Send Money flow, step 1).
 *
 * Lets the sender search the mock user directory and pick a recipient.
 * On selection, navigates to /send/:userId so the Send Money screen can
 * load that recipient by id. All data comes from `mockUserService` — this
 * page never hardcodes user records.
 */
export function SelectRecipientPage() {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<RecipientUser[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const isMounted = useRef(true);
  const requestSeq = useRef(0);

  useEffect(() => {
    isMounted.current = true;
    return () => {
      isMounted.current = false;
    };
  }, []);

  useEffect(() => {
    const seq = ++requestSeq.current;
    setIsLoading(true);

    mockUserService.searchUsers(query).then((users) => {
      // Ignore stale responses if a newer search started meanwhile.
      if (!isMounted.current || seq !== requestSeq.current) return;
      setResults(users);
      setIsLoading(false);
    });
  }, [query]);

  function handleSelect(user: RecipientUser) {
    navigate(`/send/${user.id}`);
  }

  return (
    <main className="select-recipient-page">
      <div className="select-recipient-page__container">
        <header className="select-recipient-page__header">
          <Link to="/dashboard" className="select-recipient-page__back" aria-label="Back to dashboard">
            ←
          </Link>
          <h1 className="select-recipient-page__title">Send money</h1>
        </header>

        <div className="select-recipient-page__search">
          <FormField
            label="Search people"
            placeholder="Name, @handle, email, or phone"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            autoFocus
          />
        </div>

        {isLoading ? (
          <ul className="recipient-list">
            <RecipientListItemSkeleton />
            <RecipientListItemSkeleton />
            <RecipientListItemSkeleton />
          </ul>
        ) : results.length === 0 ? (
          <div className="recipient-list">
            <p className="recipient-list__empty">No users found.</p>
          </div>
        ) : (
          <ul className="recipient-list">
            {results.map((user) => (
              <RecipientListItem key={user.id} user={user} onSelect={handleSelect} />
            ))}
          </ul>
        )}
      </div>
    </main>
  );
}
