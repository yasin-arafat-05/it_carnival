import { PlaceholderPage } from './PlaceholderPage';

/**
 * Temporary Dashboard stand-in. The real Dashboard belongs to Group B —
 * this only exists so Feature 41 (Splash) has a real route to send an
 * authenticated mock session to.
 */
export function DashboardPlaceholderPage() {
  return (
    <PlaceholderPage
      title="Dashboard coming next"
      description="Your account overview will live here."
    />
  );
}
