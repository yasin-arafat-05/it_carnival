import { Skeleton } from '../Skeleton/Skeleton';
import type { RecipientUser } from '../../types/user';
import './RecipientListItem.css';

interface RecipientListItemProps {
  user: RecipientUser;
  onSelect: (user: RecipientUser) => void;
}

/**
 * Single selectable row in the recipient search results. Purely
 * presentational — receives a `RecipientUser` and a select callback, does
 * not fetch or filter anything itself.
 */
export function RecipientListItem({ user, onSelect }: RecipientListItemProps) {
  const initial = user.name.trim().charAt(0).toUpperCase();

  return (
    <li className="recipient-item">
      <button
        type="button"
        className="recipient-item__button"
        onClick={() => onSelect(user)}
      >
        <span className="recipient-item__avatar" aria-hidden="true">
          {initial}
        </span>
        <span className="recipient-item__text">
          <span className="recipient-item__name">{user.name}</span>
          <span className="recipient-item__meta">
            @{user.handle} · {user.email}
          </span>
        </span>
      </button>
    </li>
  );
}

/** Skeleton counterpart shown while the recipient search is loading. */
export function RecipientListItemSkeleton() {
  return (
    <li className="recipient-item" aria-hidden="true">
      <div className="recipient-item__button">
        <Skeleton width="40px" height="40px" radius="999px" />
        <span className="recipient-item__text">
          <Skeleton width="140px" height="15px" />
          <Skeleton width="180px" height="13px" />
        </span>
      </div>
    </li>
  );
}
