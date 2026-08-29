import './Logo.css';

interface LogoProps {
  /** Visual size of the mark in pixels. Defaults to 56. */
  size?: number;
  /** Show the "IT Carnival" wordmark next to the mark. Defaults to true. */
  withWordmark?: boolean;
  className?: string;
}

/**
 * Product brand mark for IT Carnival.
 *
 * A simple, professional mark — a rounded shield holding an upward arrow,
 * meant to read as "safe" and "moving your money forward" without leaning
 * on crypto/fintech visual clichés (no coins, no neon, no 3D gradients).
 */
export function Logo({ size = 56, withWordmark = true, className }: LogoProps) {
  return (
    <div className={`logo${className ? ` ${className}` : ''}`}>
      <svg
        width={size}
        height={size}
        viewBox="0 0 48 48"
        fill="none"
        role="img"
        aria-label="IT Carnival logo"
      >
        <rect x="1" y="1" width="46" height="46" rx="14" fill="#1F7A4D" />
        <path
          d="M24 12c-.5 0-1 .16-1.4.47l-8 6.15A2.25 2.25 0 0 0 13.75 20.5v9.1A2.25 2.25 0 0 0 15 31.68l8 3.72c.63.3 1.37.3 2 0l8-3.72a2.25 2.25 0 0 0 1.25-2.08v-9.1c0-.72-.34-1.4-.9-1.88l-8-6.15A2.3 2.3 0 0 0 24 12Z"
          fill="#FFFFFF"
          fillOpacity="0.14"
        />
        <path
          d="M24 17.5v13m0-13-4.5 4.3M24 17.5l4.5 4.3"
          stroke="#FFFFFF"
          strokeWidth="2.25"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
      {withWordmark && <span className="logo__wordmark">IT Carnival</span>}
    </div>
  );
}
