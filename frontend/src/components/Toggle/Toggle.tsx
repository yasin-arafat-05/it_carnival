import { useId } from 'react';
import './Toggle.css';

interface ToggleProps {
  label: string;
  description?: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}

/**
 * Accessible on/off switch used in Settings. UI-only — callers own
 * whatever local state the toggle reflects; nothing here persists or
 * calls an API.
 */
export function Toggle({ label, description, checked, onChange }: ToggleProps) {
  const id = useId();

  return (
    <div className="toggle-row">
      <div className="toggle-row__text">
        <label className="toggle-row__label" htmlFor={id}>
          {label}
        </label>
        {description && <p className="toggle-row__description">{description}</p>}
      </div>
      <button
        id={id}
        type="button"
        role="switch"
        aria-checked={checked}
        className={`toggle${checked ? ' toggle--on' : ''}`}
        onClick={() => onChange(!checked)}
      >
        <span className="toggle__thumb" />
      </button>
    </div>
  );
}
